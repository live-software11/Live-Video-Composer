"""
Live Video Composer - Convertitore di Immagini e Video con supporto Multi-Layer Collage
Un'applicazione per adattare immagini e video a diverse risoluzioni e creare collage.
"""

import sys

if sys.version_info < (3, 10):
    sys.exit("Python 3.10+ required (current: %s)" % sys.version)

# ─── Gestione avvio con --deactivate (headless, prima di importare tkinter) ──
# Usato dallo script di disinstallazione Inno Setup per liberare la licenza.
import os
_LICENSE_ENABLED = os.environ.get("LIVEWORKS_LICENSE_ENABLED", "").lower() == "true"

if _LICENSE_ENABLED and "--deactivate" in sys.argv:
    from license.manager import run_deactivate_uninstall
    run_deactivate_uninstall()
    sys.exit(0)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, UnidentifiedImageError
import threading
import math
from pathlib import Path
import uuid
import logging
import gc
from logging.handlers import RotatingFileHandler

from localization import (
    t, init_language, set_language, get_language,
    get_preset_values, preset_display_to_id, preset_id_to_resolution,
)

# Configura logging (solo su file in temp user, non nella cartella dell'exe)
def _get_log_path():
    """Restituisce il percorso del file di log in una posizione non invasiva"""
    # Usa la cartella AppData/Local per il log, non la cartella dell'exe
    if sys.platform == 'win32':
        appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        log_dir = Path(appdata) / 'LiveVideoComposer'
    else:
        log_dir = Path.home() / '.live-video-composer'
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Fallback: cartella temp di sistema
        import tempfile
        log_dir = Path(tempfile.gettempdir())
    return log_dir / 'live_video_composer.log'

_log_handler = RotatingFileHandler(
    _get_log_path(), maxBytes=5 * 1024 * 1024, backupCount=3,
    encoding='utf-8', errors='replace'
)
_log_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[_log_handler])
logger = logging.getLogger('LiveVideoComposer')

try:
    import cv2
    import numpy as np
    VIDEO_SUPPORT = True
    logger.info(f"OpenCV {cv2.__version__} caricato, supporto video attivo")
except ImportError:
    VIDEO_SUPPORT = False
    logger.info("OpenCV non disponibile - supporto video disattivato")

# Costanti per i formati supportati (set per lookup O(1))
IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff'}
VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}

# Costanti per gli handle
HANDLE_SIZE = 8
HANDLE_COLOR = "#4a9eff"
ROTATION_HANDLE_DISTANCE = 25

# ============================================================================
# COSTANTI OPERATIVE
# ============================================================================
MAX_GIF_FRAMES = 3000               # Limite memoria per GIF animate
DOWNSCALE_THRESHOLD = 2.0           # Se img > 2x output -> working copy ridotta
DND_SETUP_DELAY_MS = 500            # Ritardo setup windnd (vincolo sacro #3)
DEBOUNCE_NORMAL_MS = 16             # Redraw ~60fps
DEBOUNCE_DRAG_MS = 33               # Redraw ~30fps durante drag
PREVIEW_SCALE_MARGIN = 0.9          # Margine preview sul canvas


class ImageLayer:
    """Rappresenta un'immagine nel collage con le sue proprietà"""
    __slots__ = ['id', 'original_image', 'name', 'offset_x', 'offset_y', 'zoom',
                 'rotation', 'flip_h', 'flip_v', 'is_video', 'video_path',
                 'video_fps', 'video_frames', 'bounds_in_canvas', '_cache', '_cache_key',
                 '_zoom_cache', '_zoom_cache_key', '_original_path']

    def __init__(self, image, name=None):
        self.id = str(uuid.uuid4())[:8]
        self.original_image = image
        self.name = name if name is not None else t("layer.default_name")

        # Trasformazioni
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 100  # percentuale
        self.rotation = 0  # gradi
        self.flip_h = False  # specchio orizzontale
        self.flip_v = False  # specchio verticale

        # Proprietà video (opzionali)
        self.is_video = False
        self.video_path = None
        self.video_fps = 30
        self.video_frames = 0

        # Bounds calcolati nel canvas
        self.bounds_in_canvas = None  # (x, y, w, h)

        # Cache per immagine trasformata (rotation, flip)
        self._cache = None
        self._cache_key = None

        # Cache per immagine già zoomata (evita resize ripetuti durante pan)
        self._zoom_cache = None
        self._zoom_cache_key = None

        # Percorso file originale (per export a piena risoluzione quando è attivo downscale)
        self._original_path = None

    def get_transformed_image(self, use_cache=True, zoom=None, fast_mode=False):
        """Restituisce l'immagine con trasformazioni applicate (con cache).
        Se zoom e' fornito, restituisce l'immagine gia' ridimensionata (cache separata).
        fast_mode=True usa NEAREST per rotation/resize (piu' veloce durante il drag).
        """
        if self.original_image is None:
            return None

        base_key = (self.rotation, self.flip_h, self.flip_v)

        # Cache zoom: se zoom fornito e cache hit, ritorna subito
        if zoom is not None and use_cache and not fast_mode:
            zoom_key = (*base_key, zoom)
            if self._zoom_cache is not None and self._zoom_cache_key == zoom_key:
                return self._zoom_cache

        # Base: trasformazioni (rotation, flip)
        # fast_mode bypassa la cache (risultato NEAREST non va in cache)
        if not fast_mode and use_cache and self._cache is not None and self._cache_key == base_key:
            img = self._cache
        else:
            img = self.original_image.copy()
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            if self.flip_h:
                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if self.flip_v:
                img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            if self.rotation != 0:
                resample = Image.Resampling.NEAREST if fast_mode else Image.Resampling.BILINEAR
                img = img.rotate(-self.rotation, resample=resample, expand=True)
            if use_cache and not fast_mode:
                self._cache = img
                self._cache_key = base_key

        # Applica zoom se richiesto
        if zoom is not None:
            zoom_pct = zoom / 100.0
            new_w = max(1, int(img.size[0] * zoom_pct))
            new_h = max(1, int(img.size[1] * zoom_pct))
            resample = Image.Resampling.NEAREST if fast_mode else Image.Resampling.BILINEAR
            img = img.resize((new_w, new_h), resample)
            if use_cache and not fast_mode:
                self._zoom_cache = img
                self._zoom_cache_key = (*base_key, zoom)

        return img

    def invalidate_cache(self):
        """Invalida la cache dell'immagine trasformata"""
        self._cache = None
        self._cache_key = None
        self._zoom_cache = None
        self._zoom_cache_key = None

    def cleanup(self):
        """Libera risorse associate al layer"""
        self.invalidate_cache()
        self.original_image = None
        self.bounds_in_canvas = None

    def get_display_name(self):
        return f"{self.name} ({self.id})"


class LiveVideoComposer:
    def __init__(self, root):
        self.root = root
        self.root.title(t("app.title"))
        self.root.state('zoomed')  # Fullscreen su Windows
        self.root.minsize(1100, 700)

        # Lista delle immagini (layers)
        self.layers = []
        self.selected_layer = None

        # Stato video (per il primo layer se è video)
        self.is_video = False
        self.video_file = None

        # Parametri output
        self.output_width = tk.IntVar(value=3840)
        self.output_height = tk.IntVar(value=1396)
        self.bg_color_var = tk.StringVar(value="#000000")

        # Parametri qualità (inizializzati qui, usati nel pannello export)
        self.img_quality = tk.IntVar(value=100)

        # Stato UI
        self.display_image = None
        self.canvas_bounds = None
        self.preview_scale = 1.0
        self.handles = {}

        # Stato trascinamento
        self.is_dragging = False
        self.active_handle = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_start_offset_x = 0
        self.drag_start_offset_y = 0
        self.resize_start_zoom = 100
        self.resize_start_pos = (0, 0)
        self.rotation_start_angle = 0
        self.rotation_start_value = 0
        self.rotation_center = (0, 0)

        # Debounce per redraw
        self._redraw_scheduled = False
        self._redraw_job = None
        self._resize_job = None

        # Cache dimensioni canvas (evita update_idletasks nel hot path)
        self._cached_canvas_size = (0, 0)

        # Oggetti canvas riutilizzabili (evita delete/create ogni frame)
        self._canvas_persistent_ids = None

        # Flag per evitare re-bind ricorsivo scroll
        self._scroll_bound = False

        # Parametri qualità export (default: Media)
        self.export_dpi = tk.IntVar(value=150)
        self.export_bit_depth = tk.IntVar(value=16)
        self.quality_preset = tk.StringVar(value="media")

        # Flag export cancellabile
        self._export_cancelled = threading.Event()

        # Setup
        self.setup_style()
        self._set_window_icon()
        self.create_widgets()
        self.setup_bindings()
        self.setup_drag_and_drop()

        # Protocollo chiusura finestra: cleanup risorse prima di uscire
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Inizializza canvas con preview vuoto (risoluzione default)
        self.root.after(100, self.init_canvas_preview)

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Palette Blu Moderna - Tech/Cyber style
        self.bg_color = "#0a1929"        # Sfondo blu notte profondo
        self.bg_secondary = "#132f4c"    # Sfondo secondario blu scuro
        self.bg_tertiary = "#1a3a5c"     # Terziario per hover
        self.fg_color = "#e3f2fd"        # Testo bianco-blu
        self.fg_secondary = "#90caf9"    # Testo secondario blu chiaro
        self.accent_color = "#29b6f6"    # Cyan/azzurro brillante
        self.accent_hover = "#4fc3f7"    # Hover più chiaro
        self.accent_glow = "#0288d1"     # Blu più scuro per contrasto
        self.success_color = "#66bb6a"   # Verde per export immagine
        self.video_color = "#7c4dff"     # Viola per export video
        self.border_color = "#1e4976"    # Bordi blu

        self.root.configure(bg=self.bg_color)

        # Stili base
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color,
                       font=('Segoe UI', 10))
        style.configure("Header.TLabel", background=self.bg_color, foreground=self.accent_color,
                       font=('Segoe UI', 11, 'bold'))

        # Pulsanti moderni
        style.configure("TButton", font=('Segoe UI', 10), padding=8,
                       background=self.bg_secondary, foreground=self.fg_color)
        style.map("TButton",
                 background=[('active', self.bg_tertiary), ('pressed', self.accent_color)])

        # Pulsante accent (esportazione)
        style.configure("Accent.TButton", font=('Segoe UI', 11, 'bold'), padding=10,
                       background=self.accent_color, foreground="#0a1929")
        style.map("Accent.TButton",
                 background=[('active', self.accent_hover), ('disabled', self.border_color)])

        # Pulsante verde (export immagine)
        style.configure("Green.TButton", font=('Segoe UI', 10, 'bold'), padding=8,
                       background=self.success_color, foreground="#0a1929")
        style.map("Green.TButton",
                 background=[('active', '#81c784'), ('disabled', self.border_color)])

        # Pulsante viola (export video)
        style.configure("Blue.TButton", font=('Segoe UI', 10, 'bold'), padding=8,
                       background=self.video_color, foreground="#ffffff")
        style.map("Blue.TButton",
                 background=[('active', '#9575cd'), ('disabled', self.border_color)])

        # Scale/Slider
        style.configure("TScale", background=self.bg_color, troughcolor=self.bg_secondary)
        style.configure("Horizontal.TScale", background=self.bg_color)

        # Combobox - colori leggibili
        style.configure("TCombobox",
                       font=('Segoe UI', 10),
                       fieldbackground=self.bg_secondary,
                       background=self.bg_secondary,
                       foreground=self.fg_color,
                       arrowcolor=self.fg_color,
                       selectbackground=self.accent_color,
                       selectforeground="#0a1929")
        style.map("TCombobox",
                 fieldbackground=[('readonly', self.bg_secondary), ('disabled', self.bg_color)],
                 foreground=[('readonly', self.fg_color), ('disabled', self.border_color)],
                 background=[('active', self.bg_tertiary), ('readonly', self.bg_secondary)])

        # Configura anche il dropdown del combobox
        self.root.option_add('*TCombobox*Listbox.background', self.bg_secondary)
        self.root.option_add('*TCombobox*Listbox.foreground', self.fg_color)
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.accent_color)
        self.root.option_add('*TCombobox*Listbox.selectForeground', '#0a1929')
        self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 10))

        # Radiobutton
        style.configure("TRadiobutton", background=self.bg_color, foreground=self.fg_color,
                       font=('Segoe UI', 10))
        style.map("TRadiobutton",
                 background=[('active', self.bg_color)])

        # LabelFrame con bordi blu luminosi
        style.configure("TLabelframe", background=self.bg_color, foreground=self.fg_color,
                       bordercolor=self.border_color)
        style.configure("TLabelframe.Label", background=self.bg_color, foreground="#ffffff",
                       font=('Segoe UI', 10, 'bold'))

        # LabelFrame stili per diverse sezioni (colori ben differenziati)
        self.section_colors = {
            'layers': '#1a365d',      # Layers - blu navy intenso
            'transform': '#0f2840',   # Trasformazioni - blu scuro base
            'size': '#1e4a3d',        # Dimensioni - verde-blu (teal scuro)
            'fit': '#2d1f47',         # Adattamento - viola scuro
            'mirror': '#3d2a1f',      # Specchio - marrone/arancio scuro
        }

        # Colori bordo per ogni sezione (più luminosi)
        self.section_borders = {
            'layers': '#3182ce',      # Blu brillante
            'transform': '#1e88e5',   # Blu
            'size': '#26a69a',        # Teal
            'fit': '#7c4dff',         # Viola
            'mirror': '#ff7043',      # Arancio
        }

        for name, color in self.section_colors.items():
            border = self.section_borders.get(name, self.border_color)
            style.configure(f"{name.capitalize()}.TLabelframe", background=color,
                           foreground=self.fg_color, bordercolor=border, borderwidth=2)
            # Titoli uniformi: bianco, bold, font 10
            style.configure(f"{name.capitalize()}.TLabelframe.Label",
                           background=color,
                           foreground="#ffffff",
                           font=('Segoe UI', 10, 'bold'))

        # Toggle Switch moderno per Blocca Proporzioni - bianco e bold
        style.configure("Toggle.TCheckbutton",
                       background=self.bg_color,
                       foreground="#ffffff",
                       font=('Segoe UI', 10, 'bold'),
                       padding=4)
        style.map("Toggle.TCheckbutton",
                 background=[('active', self.bg_tertiary), ('selected', self.accent_glow)],
                 foreground=[('active', '#ffffff'), ('selected', '#ffffff')])

        # Entry
        style.configure("TEntry", fieldbackground=self.bg_secondary, foreground=self.fg_color,
                       insertcolor=self.fg_color)

        # Progressbar
        style.configure("TProgressbar", background=self.accent_color, troughcolor=self.bg_secondary)

    def _set_window_icon(self):
        """Imposta l'icona della finestra da icon.ico. Rigenerare con: python scripts/create-icon.py"""
        icon_path = Path(__file__).resolve().parent / "icon.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except tk.TclError:
                pass

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header con toggle lingua (lingua attiva evidenziata)
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Frame(header_frame, bg=self.bg_color).pack(side=tk.LEFT, expand=True)
        lang_frame = tk.Frame(header_frame, bg=self.bg_color)
        lang_frame.pack(side=tk.RIGHT)
        self.lang_btn_it = tk.Button(lang_frame, text="IT", width=3, font=('Segoe UI', 9, 'bold'),
                                     relief=tk.FLAT, bd=0, cursor='hand2',
                                     command=lambda: self._set_lang("it"))
        self.lang_btn_it.pack(side=tk.LEFT, padx=1)
        self.lang_btn_it.bind("<Enter>", lambda e: self._lang_btn_hover("it", True))
        self.lang_btn_it.bind("<Leave>", lambda e: self._lang_btn_hover("it", False))
        self.lang_btn_en = tk.Button(lang_frame, text="EN", width=3, font=('Segoe UI', 9, 'bold'),
                                     relief=tk.FLAT, bd=0, cursor='hand2',
                                     command=lambda: self._set_lang("en"))
        self.lang_btn_en.pack(side=tk.LEFT, padx=1)
        self.lang_btn_en.bind("<Enter>", lambda e: self._lang_btn_hover("en", True))
        self.lang_btn_en.bind("<Leave>", lambda e: self._lang_btn_hover("en", False))

        self.create_left_panel(main_frame)
        self.create_canvas_panel(main_frame)
        self.create_right_panel(main_frame)

        self.apply_localization()

    def _set_lang(self, lang):
        """Cambio lingua istantaneo (modello Live 3D LEDWall Render)."""
        set_language(lang)
        self.apply_localization()

    def _update_lang_toggle_style(self):
        """Evidenzia la lingua attiva nel toggle IT/EN (cyan acceso = attivo)."""
        self._apply_lang_btn_style("it", False)
        self._apply_lang_btn_style("en", False)

    def _lang_btn_hover(self, code, entering):
        """Hover sui pulsanti lingua."""
        self._apply_lang_btn_style(code, entering)

    def _apply_lang_btn_style(self, code, hover):
        """Applica stile al pulsante lingua (attivo = cyan acceso, inattivo = grigio, hover = leggermente più chiaro)."""
        lang = get_language()
        active_bg = self.accent_color
        active_fg = "#0a1929"
        inactive_bg = self.bg_tertiary if hover else self.bg_secondary
        inactive_fg = self.fg_color
        btn = self.lang_btn_it if code == "it" else self.lang_btn_en
        is_active = lang == code
        bg = active_bg if is_active else inactive_bg
        fg = active_fg if is_active else inactive_fg
        btn.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)

    def apply_localization(self):
        """Aggiorna tutte le stringhe UI alla lingua corrente."""
        self.root.title(t("app.title"))
        self._update_lang_toggle_style()
        self.layers_frame.config(text=t("layers.title"))
        self.layer_controls_frame.config(text=t("transform.title"))
        self.zoom_label.config(text=t("transform.scale"))
        self.rotation_label.config(text=t("transform.rotation"))
        self.pan_label.config(text=t("transform.pan"))
        self.tilt_label.config(text=t("transform.tilt"))
        self.size_frame.config(text=t("size.title"))
        self.size_label_w.config(text=t("size.label_w"))
        self.size_label_h.config(text=t("size.label_h"))
        self.output_label_w.config(text=t("size.label_w"))
        self.output_label_h.config(text=t("size.label_h"))
        self.lock_aspect_btn.config(text=t("size.lock") if self.lock_aspect_ratio.get() else t("size.unlock"))
        self.fit_adapt_btn.config(text=t("fit.adapt"))
        self.fit_fill_btn.config(text=t("fit.fill"))
        self.fit_fill_h_btn.config(text=t("fit.fill_h"))
        self.fit_fill_v_btn.config(text=t("fit.fill_v"))
        self.btn_center.config(text=t("btn.center"))
        self.mirror_frame.config(text=t("mirror.title"))
        self.mirror_h_btn.config(text=t("mirror.h"))
        self.mirror_v_btn.config(text=t("mirror.v"))
        self.file_label.config(text=t("canvas.drag_hint"))
        self.instruction_label.config(text=t("canvas.instructions"))
        self.canvas_add_btn.config(text=t("canvas.add_file"))
        self.canvas_remove_btn.config(text=t("canvas.remove_all"))
        self.output_frame.config(text=t("output.title"))
        self.output_preset_label.config(text=t("output.preset"))
        self.output_apply_btn.config(text=t("output.apply"))
        self.bg_frame.config(text=t("bg.title"))
        self.bg_custom_btn.config(text=t("bg.custom"))
        self.image_export_frame.config(text=t("export_img.title") if self.layers else t("export_img.title_disabled"))
        self.export_img_format_label.config(text=t("export_img.format"))
        self.export_img_quality_label.config(text=t("export_img.quality"))
        self.qual_low_rb.config(text=t("export_img.low"))
        self.qual_med_rb.config(text=t("export_img.medium"))
        self.qual_high_rb.config(text=t("export_img.high"))
        self.img_export_btn.config(text=t("export_img.btn"))
        has_vid = any(getattr(l, "is_video", False) for l in self.layers)
        self.video_export_frame.config(text=t("export_vid.title") if has_vid else t("export_vid.title_disabled"))
        self.export_vid_format_label.config(text=t("export_vid.format"))
        self.export_vid_fps_label.config(text=t("export_vid.fps"))
        self.export_vid_quality_label.config(text=t("export_vid.quality"))
        self.vid_qual_low_rb.config(text=t("export_img.low"))
        self.vid_qual_med_rb.config(text=t("export_img.medium"))
        self.vid_qual_high_rb.config(text=t("export_img.high"))
        self.vid_export_btn.config(text=t("export_vid.btn"))
        self.cancel_btn.config(text=t("cancel_export"))
        current = self.preset_combo.get()
        self.preset_combo["values"] = get_preset_values()
        pid = preset_display_to_id(current) if current else "fullhd"
        self.preset_combo.set(t(f"preset.{pid}"))
        self._refresh_dynamic_labels()

    def _refresh_dynamic_labels(self):
        """Aggiorna label che dipendono dallo stato (layer, export)."""
        if not self.layers:
            self.file_label.config(text=t("canvas.add_images_short"))
            self.img_size_label.config(text=t("size.original_empty"))
        else:
            if any(getattr(l, "is_video", False) for l in self.layers):
                vid = next(l for l in self.layers if getattr(l, "is_video", False))
                dur = vid.video_frames / max(1, vid.video_fps)
                self.file_label.config(text=t("canvas.elements_video", len(self.layers), f"{dur:.1f}", f"{vid.video_fps:.0f}"))
            else:
                self.file_label.config(text=t("canvas.elements", len(self.layers)))
            if self.selected_layer:
                ow, oh = self.selected_layer.original_image.size
                self.img_size_label.config(text=t("size.original", f"{ow} x {oh}"))
        w, h = self.output_width.get(), self.output_height.get()
        self.info_label.config(text=t("canvas.output_layers", w, h, len(self.layers)) if self.layers else t("canvas.output", w, h))

    def create_left_panel(self, parent):
        """Pannello sinistro - Layers e controlli immagine selezionata (scrollabile)"""
        # Container esterno
        left_container = ttk.Frame(parent, width=280)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_container.pack_propagate(False)

        # Canvas per scrolling
        self.left_canvas = tk.Canvas(left_container, bg=self.bg_color, highlightthickness=0, width=280)
        self.left_scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.left_canvas.yview)
        self.left_scrollable_frame = ttk.Frame(self.left_canvas)

        self.left_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        )

        self.left_canvas.create_window((0, 0), window=self.left_scrollable_frame, anchor="nw", width=265)
        self.left_canvas.configure(yscrollcommand=self.left_scrollbar.set)

        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind scroll mouse sul pannello sinistro e tutti i suoi figli
        self.left_canvas.bind("<MouseWheel>", self.on_left_panel_scroll)
        self.left_scrollable_frame.bind("<MouseWheel>", self.on_left_panel_scroll)
        # Bind anche su Enter/Leave per propagare scroll a tutti i widget figli (una sola volta)
        self.left_canvas.bind("<Enter>", lambda e: self._bind_scroll_to_children_once(self.left_scrollable_frame))

        left_frame = self.left_scrollable_frame

        # === LAYERS ===
        self.layers_frame = ttk.LabelFrame(left_frame, text=t("layers.title"), padding=10, style="Layers.TLabelframe")
        self.layers_frame.pack(fill=tk.X, pady=(0, 12))

        # Lista layers con stile moderno
        self.layers_listbox = tk.Listbox(self.layers_frame, height=8, bg=self.section_colors['layers'],
                                         fg=self.fg_color, selectbackground=self.accent_color,
                                         selectforeground="#0a1929", font=('Segoe UI', 9),
                                         bd=0, highlightthickness=1, highlightcolor=self.accent_color,
                                         highlightbackground=self.border_color)
        self.layers_listbox.pack(fill=tk.X, pady=(0, 5))
        self.layers_listbox.bind('<<ListboxSelect>>', self.on_layer_select)

        # Pulsanti layer
        btn_frame = ttk.Frame(self.layers_frame)
        btn_frame.pack(fill=tk.X)

        self.btn_add = ttk.Button(btn_frame, text=t("btn.add"), command=self.add_image)
        self.btn_add.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))
        self.btn_remove = ttk.Button(btn_frame, text=t("btn.remove"), command=self.remove_selected_layer)
        self.btn_remove.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2,0))

        btn_frame2 = ttk.Frame(self.layers_frame)
        btn_frame2.pack(fill=tk.X, pady=(3,0))

        ttk.Button(btn_frame2, text="▲", width=4, command=self.move_layer_up).pack(side=tk.LEFT, padx=(0,2))
        ttk.Button(btn_frame2, text="▼", width=4, command=self.move_layer_down).pack(side=tk.LEFT, padx=(2,2))
        self.btn_duplicate = ttk.Button(btn_frame2, text=t("btn.duplicate"), command=self.duplicate_layer)
        self.btn_duplicate.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2,0))

        # === CONTROLLI LAYER SELEZIONATO ===
        self.layer_controls_frame = ttk.LabelFrame(left_frame, text=t("transform.title"), padding=8, style="Transform.TLabelframe")
        self.layer_controls_frame.pack(fill=tk.X, pady=(0, 8))

        # Zoom
        zoom_header = ttk.Frame(self.layer_controls_frame)
        zoom_header.pack(fill=tk.X)
        self.zoom_label = ttk.Label(zoom_header, text=t("transform.scale"))
        self.zoom_label.pack(side=tk.LEFT)
        self.zoom_entry = ttk.Entry(zoom_header, width=6)
        self.zoom_entry.pack(side=tk.RIGHT)
        self.zoom_entry.insert(0, "100")
        self.zoom_entry.bind('<Return>', self.on_zoom_entry)
        ttk.Label(zoom_header, text="%").pack(side=tk.RIGHT)

        self.zoom_var = tk.IntVar(value=100)
        self.zoom_scale = ttk.Scale(self.layer_controls_frame, from_=1, to=1000, variable=self.zoom_var,
                                    orient=tk.HORIZONTAL, command=self.on_zoom_change)
        self.zoom_scale.pack(fill=tk.X, pady=(0,2))

        zoom_btns = ttk.Frame(self.layer_controls_frame)
        zoom_btns.pack(fill=tk.X, pady=(0,5))
        ttk.Button(zoom_btns, text="-", width=3, command=lambda: self.adjust_layer_zoom(-10)).pack(side=tk.LEFT)
        ttk.Button(zoom_btns, text="100%", command=self.reset_layer_zoom).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(zoom_btns, text="+", width=3, command=lambda: self.adjust_layer_zoom(10)).pack(side=tk.RIGHT)

        # Rotazione
        rot_header = ttk.Frame(self.layer_controls_frame)
        rot_header.pack(fill=tk.X)
        self.rotation_label = ttk.Label(rot_header, text=t("transform.rotation"))
        self.rotation_label.pack(side=tk.LEFT)
        self.rotation_entry = ttk.Entry(rot_header, width=6)
        self.rotation_entry.pack(side=tk.RIGHT)
        self.rotation_entry.insert(0, "0")
        self.rotation_entry.bind('<Return>', self.on_rotation_entry)
        ttk.Label(rot_header, text="°").pack(side=tk.RIGHT)

        self.rotation_var = tk.IntVar(value=0)
        self.rotation_scale = ttk.Scale(self.layer_controls_frame, from_=-180, to=180, variable=self.rotation_var,
                                        orient=tk.HORIZONTAL, command=self.on_rotation_change)
        self.rotation_scale.pack(fill=tk.X, pady=(0,2))

        rot_btns = ttk.Frame(self.layer_controls_frame)
        rot_btns.pack(fill=tk.X, pady=(0,5))
        ttk.Button(rot_btns, text="-90°", width=5, command=lambda: self.set_layer_rotation(-90)).pack(side=tk.LEFT)
        ttk.Button(rot_btns, text="0°", command=lambda: self.set_layer_rotation(0)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(rot_btns, text="+90°", width=5, command=lambda: self.set_layer_rotation(90)).pack(side=tk.RIGHT)

        # Posizione X (Pan)
        pos_x_header = ttk.Frame(self.layer_controls_frame)
        pos_x_header.pack(fill=tk.X, pady=(5,0))
        self.pan_label = ttk.Label(pos_x_header, text=t("transform.pan"))
        self.pan_label.pack(side=tk.LEFT)
        self.offset_x_entry = ttk.Entry(pos_x_header, width=7)
        self.offset_x_entry.pack(side=tk.RIGHT)
        self.offset_x_entry.insert(0, "0")
        self.offset_x_entry.bind('<Return>', self.on_position_entry)

        self.offset_x_var = tk.IntVar(value=0)
        self.offset_x_scale = ttk.Scale(self.layer_controls_frame, from_=-1000, to=1000, variable=self.offset_x_var,
                                        orient=tk.HORIZONTAL, command=self.on_position_change)
        self.offset_x_scale.pack(fill=tk.X)

        # Posizione Y (Tilt)
        pos_y_header = ttk.Frame(self.layer_controls_frame)
        pos_y_header.pack(fill=tk.X)
        self.tilt_label = ttk.Label(pos_y_header, text=t("transform.tilt"))
        self.tilt_label.pack(side=tk.LEFT)
        self.offset_y_entry = ttk.Entry(pos_y_header, width=7)
        self.offset_y_entry.pack(side=tk.RIGHT)
        self.offset_y_entry.insert(0, "0")
        self.offset_y_entry.bind('<Return>', self.on_position_entry)

        self.offset_y_var = tk.IntVar(value=0)
        self.offset_y_scale = ttk.Scale(self.layer_controls_frame, from_=-1000, to=1000, variable=self.offset_y_var,
                                        orient=tk.HORIZONTAL, command=self.on_position_change)
        self.offset_y_scale.pack(fill=tk.X)

        # === DIMENSIONI IMMAGINE IN PIXEL ===
        self.size_frame = ttk.LabelFrame(self.layer_controls_frame, text=t("size.title"), padding=5, style="Size.TLabelframe")
        self.size_frame.pack(fill=tk.X, pady=(10,0))

        size_row = ttk.Frame(self.size_frame)
        size_row.pack(fill=tk.X)

        self.size_label_w = ttk.Label(size_row, text=t("size.label_w"), font=('Segoe UI', 9))
        self.size_label_w.pack(side=tk.LEFT)
        self.img_width_entry = ttk.Entry(size_row, width=6)
        self.img_width_entry.pack(side=tk.LEFT, padx=(2, 10))
        self.img_width_entry.insert(0, "0")
        self.img_width_entry.bind('<Return>', self.on_size_entry)

        self.size_label_h = ttk.Label(size_row, text=t("size.label_h"), font=('Segoe UI', 9))
        self.size_label_h.pack(side=tk.LEFT)
        self.img_height_entry = ttk.Entry(size_row, width=6)
        self.img_height_entry.pack(side=tk.LEFT, padx=2)
        self.img_height_entry.insert(0, "0")
        self.img_height_entry.bind('<Return>', self.on_size_entry)

        self.img_size_label = ttk.Label(self.size_frame, text=t("size.original_empty"), font=('Segoe UI', 8))
        self.img_size_label.pack(anchor=tk.W, pady=(1,0))

        # Toggle blocca proporzioni - stile moderno
        lock_frame = ttk.Frame(self.layer_controls_frame)
        lock_frame.pack(fill=tk.X, pady=(5, 3))
        self.lock_aspect_ratio = tk.BooleanVar(value=True)
        self.lock_aspect_btn = ttk.Checkbutton(lock_frame, text=t("size.lock"),
                                                variable=self.lock_aspect_ratio, style="Toggle.TCheckbutton",
                                                command=self.on_lock_toggle)
        self.lock_aspect_btn.pack(fill=tk.X)

        # === ADATTAMENTO LAYER ===
        fit_frame = ttk.LabelFrame(self.layer_controls_frame, text=t("fit.title"), padding=5, style="Fit.TLabelframe")
        fit_frame.pack(fill=tk.X, pady=(10,0))

        # Usa grid per allineare i 4 pulsanti uniformemente
        fit_row1 = ttk.Frame(fit_frame)
        fit_row1.pack(fill=tk.X, pady=(0,3))
        fit_row1.columnconfigure(0, weight=1, uniform="fitbtn")
        fit_row1.columnconfigure(1, weight=1, uniform="fitbtn")
        self.fit_adapt_btn = ttk.Button(fit_row1, text=t("fit.adapt"), command=self.fit_keep_aspect)
        self.fit_adapt_btn.grid(row=0, column=0, sticky="ew", padx=(0,2))
        self.fit_fill_btn = ttk.Button(fit_row1, text=t("fit.fill"), command=self.fit_contain)
        self.fit_fill_btn.grid(row=0, column=1, sticky="ew", padx=(2,0))

        fit_row2 = ttk.Frame(fit_frame)
        fit_row2.pack(fill=tk.X)
        fit_row2.columnconfigure(0, weight=1, uniform="fitbtn")
        fit_row2.columnconfigure(1, weight=1, uniform="fitbtn")
        self.fit_fill_h_btn = ttk.Button(fit_row2, text=t("fit.fill_h"), command=self.fit_fill_horizontal)
        self.fit_fill_h_btn.grid(row=0, column=0, sticky="ew", padx=(0,2))
        self.fit_fill_v_btn = ttk.Button(fit_row2, text=t("fit.fill_v"), command=self.fit_fill_vertical)
        self.fit_fill_v_btn.grid(row=0, column=1, sticky="ew", padx=(2,0))

        # Pulsanti azione
        action_btns = ttk.Frame(self.layer_controls_frame)
        action_btns.pack(fill=tk.X, pady=(10,0))
        self.btn_center = ttk.Button(action_btns, text=t("btn.center"), command=self.center_selected_layer)
        self.btn_center.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))

        # Effetto Specchio
        self.mirror_frame = ttk.LabelFrame(self.layer_controls_frame, text=t("mirror.title"), padding=5, style="Mirror.TLabelframe")
        self.mirror_frame.pack(fill=tk.X, pady=(10,0))

        mirror_btns = ttk.Frame(self.mirror_frame)
        mirror_btns.pack(fill=tk.X)
        self.mirror_h_btn = ttk.Button(mirror_btns, text=t("mirror.h"), command=self.flip_horizontal)
        self.mirror_h_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))
        self.mirror_v_btn = ttk.Button(mirror_btns, text=t("mirror.v"), command=self.flip_vertical)
        self.mirror_v_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2,0))

    def create_canvas_panel(self, parent):
        """Pannello centrale - Canvas"""
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Info con stile moderno
        self.file_label = ttk.Label(canvas_frame, text=t("canvas.drag_hint"),
                                    font=('Segoe UI', 13), style="Header.TLabel")
        self.file_label.pack(pady=(0, 5))

        self.instruction_label = ttk.Label(canvas_frame, text=t("canvas.instructions"),
            font=('Segoe UI', 9), foreground=self.border_color)
        self.instruction_label.pack(pady=(0, 5))

        # Canvas con bordo moderno
        canvas_container = tk.Frame(canvas_frame, bg=self.border_color, bd=0)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_container, bg="#061422", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.draw_empty_canvas()

        # Pulsanti con stile
        btn_frame = ttk.Frame(canvas_frame)
        btn_frame.pack(pady=10)
        self.canvas_add_btn = ttk.Button(btn_frame, text=t("canvas.add_file"), command=self.add_image)
        self.canvas_add_btn.pack(side=tk.LEFT, padx=5)
        self.canvas_remove_btn = ttk.Button(btn_frame, text=t("canvas.remove_all"), command=self.clear_all)
        self.canvas_remove_btn.pack(side=tk.LEFT, padx=5)

        self.info_label = ttk.Label(canvas_frame, text="", font=('Segoe UI', 9))
        self.info_label.pack()

    def create_right_panel(self, parent):
        """Pannello destro - Output e Export"""
        right_frame = ttk.Frame(parent, width=270)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        # === OUTPUT ===
        self.output_frame = ttk.LabelFrame(right_frame, text=t("output.title"), padding=10)
        self.output_frame.pack(fill=tk.X, pady=(0, 10))

        self.output_preset_label = ttk.Label(self.output_frame, text=t("output.preset"))
        self.output_preset_label.pack(anchor=tk.W)
        self.preset_combo = ttk.Combobox(self.output_frame, values=get_preset_values(), state="readonly")
        self.preset_combo.set(t("preset.fullhd"))
        self.preset_combo.pack(fill=tk.X, pady=(2, 10))
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_change)

        size_frame = ttk.Frame(self.output_frame)
        size_frame.pack(fill=tk.X)

        self.output_label_w = ttk.Label(size_frame, text=t("size.label_w"))
        self.output_label_w.grid(row=0, column=0)
        self.width_entry = ttk.Entry(size_frame, textvariable=self.output_width, width=7)
        self.width_entry.grid(row=0, column=1, padx=2)

        self.output_label_h = ttk.Label(size_frame, text=t("size.label_h"))
        self.output_label_h.grid(row=0, column=2, padx=(10,0))
        self.height_entry = ttk.Entry(size_frame, textvariable=self.output_height, width=7)
        self.height_entry.grid(row=0, column=3, padx=2)

        self.output_apply_btn = ttk.Button(self.output_frame, text=t("output.apply"), command=self.apply_resolution)
        self.output_apply_btn.pack(pady=(10, 0))

        # === SFONDO ===
        self.bg_frame = ttk.LabelFrame(right_frame, text=t("bg.title"), padding=10)
        self.bg_frame.pack(fill=tk.X, pady=(0, 10))

        color_grid = ttk.Frame(self.bg_frame)
        color_grid.pack()

        colors = [("#000000", "bg.black"), ("#FFFFFF", "bg.white"), ("#808080", "bg.gray"),
                  ("#FF0000", "bg.red"), ("#00FF00", "bg.green"), ("#0000FF", "bg.blue"),
                  ("#FFFF00", "bg.yellow"), ("#FF00FF", "bg.magenta"), ("#00FFFF", "bg.cyan")]

        for i, (color, key) in enumerate(colors):
            btn = tk.Button(color_grid, bg=color, width=3, height=1, bd=0,
                           activebackground=color, relief=tk.FLAT,
                           command=lambda c=color: self.set_bg_color(c))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)

        self.bg_custom_btn = ttk.Button(self.bg_frame, text=t("bg.custom"), command=self.choose_custom_color)
        self.bg_custom_btn.pack(pady=(10, 0))

        # === ESPORTAZIONE IMMAGINE ===
        self.image_export_frame = ttk.LabelFrame(right_frame, text=t("export_img.title"), padding=12)
        self.image_export_frame.pack(fill=tk.X, pady=(0, 8))

        # Formati in una riga ordinata
        self.export_img_format_label = ttk.Label(self.image_export_frame, text=t("export_img.format"), font=('Segoe UI', 9))
        self.export_img_format_label.pack(anchor=tk.W)
        self.output_format = tk.StringVar(value="png")
        img_fmt_frame = ttk.Frame(self.image_export_frame)
        img_fmt_frame.pack(fill=tk.X, pady=(2, 8))
        for i, fmt in enumerate(["PNG", "JPG", "WebP", "BMP"]):
            ttk.Radiobutton(img_fmt_frame, text=fmt, variable=self.output_format,
                           value=fmt.lower()).grid(row=0, column=i, sticky=tk.W, padx=2)

        # Preset Qualità (Bassa, Media, Alta)
        qual_preset_frame = ttk.Frame(self.image_export_frame)
        qual_preset_frame.pack(fill=tk.X, pady=(0, 5))
        self.export_img_quality_label = ttk.Label(qual_preset_frame, text=t("export_img.quality"), font=('Segoe UI', 9))
        self.export_img_quality_label.pack(side=tk.LEFT)

        self.quality_preset = tk.StringVar(value="media")
        self.qual_low_rb = ttk.Radiobutton(qual_preset_frame, text=t("export_img.low"), variable=self.quality_preset,
                       value="bassa", command=self.on_quality_preset_change)
        self.qual_low_rb.pack(side=tk.LEFT, padx=3)
        self.qual_med_rb = ttk.Radiobutton(qual_preset_frame, text=t("export_img.medium"), variable=self.quality_preset,
                       value="media", command=self.on_quality_preset_change)
        self.qual_med_rb.pack(side=tk.LEFT, padx=3)
        self.qual_high_rb = ttk.Radiobutton(qual_preset_frame, text=t("export_img.high"), variable=self.quality_preset,
                       value="alta", command=self.on_quality_preset_change)
        self.qual_high_rb.pack(side=tk.LEFT, padx=3)

        # Info qualità (DPI, bit depth)
        self.quality_info_label = ttk.Label(self.image_export_frame,
                                            text=t("export_img.dpi", 150, 16, 15),
                                            font=('Segoe UI', 8))
        self.quality_info_label.pack(anchor=tk.W, pady=(0, 8))

        self.img_export_btn = ttk.Button(self.image_export_frame, text=t("export_img.btn"),
                                         style="Green.TButton", command=self.export_image)
        self.img_export_btn.pack(fill=tk.X, ipady=4)

        # === ESPORTAZIONE VIDEO ===
        self.video_export_frame = ttk.LabelFrame(right_frame, text=t("export_vid.title"), padding=12)
        self.video_export_frame.pack(fill=tk.X, pady=(0, 8))

        # Formati video
        self.export_vid_format_label = ttk.Label(self.video_export_frame, text=t("export_vid.format"), font=('Segoe UI', 9))
        self.export_vid_format_label.pack(anchor=tk.W)
        self.video_format = tk.StringVar(value="mp4")
        vid_fmt_frame = ttk.Frame(self.video_export_frame)
        vid_fmt_frame.pack(fill=tk.X, pady=(2, 8))
        for i, fmt in enumerate(["MP4", "AVI", "WebM", "GIF"]):
            ttk.Radiobutton(vid_fmt_frame, text=fmt, variable=self.video_format,
                           value=fmt.lower()).grid(row=0, column=i, sticky=tk.W, padx=2)

        # FPS
        fps_frame = ttk.Frame(self.video_export_frame)
        fps_frame.pack(fill=tk.X, pady=(0, 5))
        self.export_vid_fps_label = ttk.Label(fps_frame, text=t("export_vid.fps"), font=('Segoe UI', 9))
        self.export_vid_fps_label.pack(side=tk.LEFT)
        self.fps_var = tk.IntVar(value=30)
        fps_entry = ttk.Entry(fps_frame, textvariable=self.fps_var, width=4)
        fps_entry.pack(side=tk.LEFT, padx=(2, 15))

        # Preset Qualità Video (Bassa, Media, Alta)
        vid_qual_preset_frame = ttk.Frame(self.video_export_frame)
        vid_qual_preset_frame.pack(fill=tk.X, pady=(0, 5))
        self.export_vid_quality_label = ttk.Label(vid_qual_preset_frame, text=t("export_vid.quality"), font=('Segoe UI', 9))
        self.export_vid_quality_label.pack(side=tk.LEFT)

        self.vid_quality_preset = tk.StringVar(value="media")
        self.vid_qual_low_rb = ttk.Radiobutton(vid_qual_preset_frame, text=t("export_img.low"), variable=self.vid_quality_preset,
                       value="bassa", command=self.on_vid_quality_preset_change)
        self.vid_qual_low_rb.pack(side=tk.LEFT, padx=3)
        self.vid_qual_med_rb = ttk.Radiobutton(vid_qual_preset_frame, text=t("export_img.medium"), variable=self.vid_quality_preset,
                       value="media", command=self.on_vid_quality_preset_change)
        self.vid_qual_med_rb.pack(side=tk.LEFT, padx=3)
        self.vid_qual_high_rb = ttk.Radiobutton(vid_qual_preset_frame, text=t("export_img.high"), variable=self.vid_quality_preset,
                       value="alta", command=self.on_vid_quality_preset_change)
        self.vid_qual_high_rb.pack(side=tk.LEFT, padx=3)

        # Info qualità video
        self.vid_quality = tk.IntVar(value=75)
        self.vid_bitrate = tk.IntVar(value=5000)  # kbps
        self.vid_quality_info_label = ttk.Label(self.video_export_frame,
                                                text=t("export_vid.bitrate", 5000, 23),
                                                font=('Segoe UI', 8))
        self.vid_quality_info_label.pack(anchor=tk.W, pady=(0, 8))

        self.vid_export_btn = ttk.Button(self.video_export_frame, text=t("export_vid.btn"),
                                         style="Blue.TButton", command=self.export_video)
        self.vid_export_btn.pack(fill=tk.X, ipady=4)

        # Progress bar moderna
        self.progress = ttk.Progressbar(right_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(5, 2))

        # Pulsante Annulla export (visibile solo durante export)
        self.cancel_btn = ttk.Button(right_frame, text=t("cancel_export"),
                                     command=self.cancel_export)
        self.cancel_btn.pack(fill=tk.X, pady=(0, 8))
        self.cancel_btn.pack_forget()  # Nascosto di default

        # Stato iniziale: video disabilitato
        self.set_video_export_enabled(False)

    def draw_empty_canvas(self):
        """Disegna canvas vuoto con stile moderno"""
        self.canvas.delete("all")
        self.canvas.update_idletasks()

        w = self.canvas.winfo_width() or 600
        h = self.canvas.winfo_height() or 400

        # Sfondo blu notte
        self.canvas.create_rectangle(0, 0, w, h, fill="#061422", outline="")

        # Area tratteggiata centrale con glow effect
        margin = 60
        self.canvas.create_rectangle(margin, margin, w-margin, h-margin,
                                     outline=self.accent_color, width=2, dash=(8, 4))

        # Icona e testo
        self.canvas.create_text(w//2, h//2 - 30, text="▢",
                               fill=self.accent_color, font=('Segoe UI', 52))
        self.canvas.create_text(w//2, h//2 + 30, text=t("canvas.empty_text"),
                               fill=self.fg_color, font=('Segoe UI', 13))
        self.canvas.create_text(w//2, h//2 + 55, text=t("canvas.empty_sub"),
                               fill=self.fg_secondary, font=('Segoe UI', 10))

    def setup_bindings(self):
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.root.bind("<Control-o>", lambda e: self.add_image())
        self.root.bind("<Control-s>", lambda e: self.export_image())
        self.root.bind("<Delete>", self.on_delete_key)
        self.root.bind("<Escape>", self.on_escape_key)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Motion>", self.on_mouse_hover)

    def setup_drag_and_drop(self):
        """Configura il drag and drop per file esterni.

        Usa windnd (Python puro, nessun subclassing pericoloso).
        Fallback: tkinterdnd2.
        Il setup è ritardato per assicurare che la finestra sia pronta.
        """
        self.drag_drop_enabled = False
        # Ritarda il setup per dare tempo alla finestra di inizializzarsi
        self.root.after(500, self._do_setup_drag_and_drop)

    def _do_setup_drag_and_drop(self):
        """Setup effettivo del drag and drop (chiamato dopo init finestra)"""
        # Tentativo 1: windnd (affidabile su Windows, anche con PyInstaller onefile)
        try:
            import windnd  # type: ignore[import-not-found]
            windnd.hook_dropfiles(self.root, func=self._on_drop_windnd)
            self.drag_drop_enabled = True
            logger.info("Drag & Drop: windnd attivo")
            return
        except ImportError:
            logger.info("windnd non installato, provo tkinterdnd2")
        except Exception as e:
            logger.warning(f"windnd fallito: {e}")

        # Tentativo 2: tkinterdnd2
        try:
            from tkinterdnd2 import DND_FILES  # type: ignore[import-not-found]
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind('<<Drop>>', self._on_drop_tkdnd)
            self.drag_drop_enabled = True
            logger.info("Drag & Drop: tkinterdnd2 attivo")
            return
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"tkinterdnd2 fallito: {e}")

        logger.warning("Drag & Drop non disponibile (installa windnd: pip install windnd)")

    def _process_dropped_files(self, files):
        """Processa la lista di file droppati (chiamato nel main thread Tk).
        Valida dimensione file, estensione, e gestisce PIL.UnidentifiedImageError.
        """
        MAX_IMAGE_SIZE = 500 * 1024 * 1024   # 500 MB warning per immagini
        MAX_VIDEO_SIZE = 4 * 1024 * 1024 * 1024  # 4 GB limite video

        for filepath in files:
            try:
                filepath = str(filepath).strip()
                if not filepath or not os.path.isfile(filepath):
                    logger.warning(f"File non valido nel drop: {filepath}")
                    continue

                ext = Path(filepath).suffix.lower()

                # Controllo dimensione file
                try:
                    file_size = os.path.getsize(filepath)
                except OSError:
                    file_size = 0

                if ext in VIDEO_FORMATS:
                    if file_size > MAX_VIDEO_SIZE:
                        logger.warning(f"File video molto grande ({file_size / 1024**3:.1f} GB): {filepath}")
                        messagebox.showwarning(t("dialog.file_large_title"),
                            t("dialog.file_large_video", f"{file_size / 1024**3:.1f}"))
                    self.load_video(filepath)
                elif ext in IMAGE_FORMATS:
                    if file_size > MAX_IMAGE_SIZE:
                        logger.warning(f"Immagine molto grande ({file_size / 1024**2:.0f} MB): {filepath}")
                        messagebox.showwarning(t("dialog.file_large_title"),
                            t("dialog.file_large_image", f"{file_size / 1024**2:.0f}"))
                    self.load_image(filepath)
                else:
                    logger.info(f"Formato non supportato nel drop: {ext}")
                    messagebox.showwarning(t("dialog.unsupported_title"),
                        t("dialog.unsupported", Path(filepath).name, ', '.join(sorted(IMAGE_FORMATS)), ', '.join(sorted(VIDEO_FORMATS))))
            except Exception as e:
                logger.error(f"Errore elaborazione file droppato: {e}")

    def _on_drop_windnd(self, files):
        """Gestisce il drop di file tramite windnd"""
        processed = []
        for filepath in files:
            try:
                if isinstance(filepath, bytes):
                    try:
                        filepath = filepath.decode('utf-8')
                    except UnicodeDecodeError:
                        filepath = filepath.decode('cp1252', errors='replace')
                processed.append(str(filepath).strip('{}').strip('"').strip("'"))
            except Exception as e:
                logger.error(f"Errore decodifica file windnd: {e}")
        if processed:
            self._process_dropped_files(processed)

    def _on_drop_tkdnd(self, event):
        """Gestisce il drop di file tramite tkinterdnd2"""
        try:
            files = self.root.tk.splitlist(event.data)
            self._process_dropped_files([f.strip('{}') for f in files])
        except Exception as e:
            logger.error(f"Errore on_drop_tkdnd: {e}")

    def init_canvas_preview(self):
        """Inizializza il canvas con la preview della risoluzione di default"""
        self.canvas.update_idletasks()
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            return

        output_w = max(1, self.output_width.get())
        output_h = max(1, self.output_height.get())

        # Scala preview (guard edge case: canvas_w/h = 0)
        canvas_w_safe = max(1, canvas_w)
        canvas_h_safe = max(1, canvas_h)
        self.preview_scale = max(1e-6, min(canvas_w_safe / output_w, canvas_h_safe / output_h) * PREVIEW_SCALE_MARGIN)
        preview_w = max(1, int(output_w * self.preview_scale))
        preview_h = max(1, int(output_h * self.preview_scale))

        # Pulisci e disegna area di output
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, canvas_w, canvas_h, fill="#0a1929", outline="")

        # Posizione canvas output
        canvas_x = (canvas_w - preview_w) // 2
        canvas_y = (canvas_h - preview_h) // 2
        self.canvas_bounds = (canvas_x, canvas_y, preview_w, preview_h)

        # Sfondo output (colore selezionato)
        bg_color = self.bg_color_var.get()
        self.canvas.create_rectangle(canvas_x, canvas_y, canvas_x+preview_w, canvas_y+preview_h,
                                     fill=bg_color, outline=self.border_color, width=2)

        # Testo informativo
        self.canvas.create_text(canvas_x + preview_w//2, canvas_y + preview_h//2 - 15,
                               text=f"{output_w} x {output_h}",
                               fill=self.fg_secondary, font=('Segoe UI', 14, 'bold'))
        self.canvas.create_text(canvas_x + preview_w//2, canvas_y + preview_h//2 + 15,
                               text=t("canvas.add_images"),
                               fill=self.border_color, font=('Segoe UI', 10))

        self.info_label.config(text=t("canvas.output", output_w, output_h))

    def on_quality_preset_change(self):
        """Gestisce il cambio del preset qualità"""
        preset = self.quality_preset.get()

        if preset == "bassa":
            self.export_dpi.set(72)
            self.export_bit_depth.set(8)
            self.img_quality.set(60)
            self.quality_info_label.config(text=t("export_img.dpi", 72, 8, 40))
        elif preset == "media":
            self.export_dpi.set(150)
            self.export_bit_depth.set(16)
            self.img_quality.set(85)
            self.quality_info_label.config(text=t("export_img.dpi", 150, 16, 15))
        else:  # alta
            self.export_dpi.set(300)
            self.export_bit_depth.set(24)
            self.img_quality.set(100)
            self.quality_info_label.config(text=t("export_img.dpi", 300, 24, 0))

    def on_lock_toggle(self):
        """Aggiorna l'icona del toggle quando cambia stato"""
        if self.lock_aspect_ratio.get():
            self.lock_aspect_btn.config(text=t("size.lock"))
        else:
            self.lock_aspect_btn.config(text=t("size.unlock"))

    def on_size_entry(self, event=None):
        """Gestisce il cambio delle dimensioni dell'immagine in pixel"""
        if not self.selected_layer:
            return

        try:
            new_width = int(self.img_width_entry.get())
            new_height = int(self.img_height_entry.get())

            if new_width < 1 or new_height < 1:
                return

            # Calcola il nuovo zoom basato sulla dimensione originale
            orig_w, orig_h = self.selected_layer.original_image.size

            # Determina quale entry è stata modificata
            focused = event.widget if event else None

            if self.lock_aspect_ratio.get():
                # Proporzioni bloccate: calcola l'altra dimensione
                aspect = orig_w / orig_h
                if focused == self.img_width_entry:
                    # Larghezza modificata, calcola altezza
                    new_height = int(new_width / aspect)
                    zoom = (new_width / orig_w) * 100
                else:
                    # Altezza modificata, calcola larghezza
                    new_width = int(new_height * aspect)
                    zoom = (new_height / orig_h) * 100
                new_zoom = int(zoom)
            else:
                # Proporzioni libere: usa la dimensione maggiore
                zoom_w = (new_width / orig_w) * 100
                zoom_h = (new_height / orig_h) * 100
                new_zoom = int(max(zoom_w, zoom_h))

            new_zoom = max(1, min(1000, new_zoom))
            self.selected_layer.zoom = new_zoom
            self.zoom_var.set(new_zoom)
            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, str(new_zoom))

            self.redraw_canvas()
            self.update_size_display()

        except ValueError:
            pass

    def update_size_display(self):
        """Aggiorna la visualizzazione delle dimensioni dell'immagine"""
        if not self.selected_layer:
            self.img_width_entry.delete(0, tk.END)
            self.img_width_entry.insert(0, "0")
            self.img_height_entry.delete(0, tk.END)
            self.img_height_entry.insert(0, "0")
            self.img_size_label.config(text=t("size.original_empty"))
            return

        # Dimensioni originali
        orig_w, orig_h = self.selected_layer.original_image.size
        self.img_size_label.config(text=t("size.original", f"{orig_w} x {orig_h}"))

        # Dimensioni attuali (con zoom)
        zoom = self.selected_layer.zoom / 100.0
        current_w = int(orig_w * zoom)
        current_h = int(orig_h * zoom)

        self.img_width_entry.delete(0, tk.END)
        self.img_width_entry.insert(0, str(current_w))
        self.img_height_entry.delete(0, tk.END)
        self.img_height_entry.insert(0, str(current_h))

    # ==================== LAYER MANAGEMENT ====================

    def add_image(self):
        """Aggiunge una nuova immagine o video al collage"""
        filetypes = [
            (t("filetypes.images_video"), "*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff *.mp4 *.avi *.mov *.mkv *.wmv *.webm"),
            (t("filetypes.images"), "*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff"),
            (t("filetypes.video"), "*.mp4 *.avi *.mov *.mkv *.wmv *.webm"),
            (t("filetypes.all"), "*.*")
        ]

        filepaths = filedialog.askopenfilenames(title=t("dialog.select_files"), filetypes=filetypes)

        for filepath in filepaths:
            ext = Path(filepath).suffix.lower()
            if ext in VIDEO_FORMATS:
                self.load_video(filepath)
            else:
                self.load_image(filepath)

    def load_image(self, filepath):
        """Carica un'immagine come nuovo layer.
        Se l'immagine e' molto piu grande dell'output, crea una working copy ridotta
        per la preview (max 2x output), mantenendo il path originale per l'export.
        """
        try:
            filepath = str(filepath)
            if not os.path.isfile(filepath):
                logger.warning(f"File non trovato: {filepath}")
                return

            img = Image.open(filepath)
            img.load()  # Forza il caricamento e rilascia il file handle
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA')

            name = Path(filepath).stem[:20]
            img_w, img_h = img.size

            if img_w == 0 or img_h == 0:
                logger.warning(f"Immagine con dimensioni zero: {filepath}")
                return

            # Calcola zoom per far stare l'immagine nel canvas
            output_w = max(1, self.output_width.get())
            output_h = max(1, self.output_height.get())

            # Downscale working copy: se l'immagine e' piu grande di 2x l'output,
            # crea una copia ridotta per la preview. L'export ricarica da disco.
            max_working_w = output_w * 2
            max_working_h = output_h * 2
            original_path = None
            if img_w > max_working_w or img_h > max_working_h:
                ds_scale = min(max_working_w / max(1, img_w), max_working_h / max(1, img_h))
                new_w = max(1, int(img_w * ds_scale))
                new_h = max(1, int(img_h * ds_scale))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                original_path = filepath
                logger.info(f"Downscale working copy: {img_w}x{img_h} -> {new_w}x{new_h} (originale salvato per export)")
                img_w, img_h = new_w, new_h

            layer = ImageLayer(img, name)
            layer._original_path = original_path

            # Calcola la scala per contenere l'immagine nell'output
            output_w = max(1, self.output_width.get())
            output_h = max(1, self.output_height.get())
            scale_x = output_w / max(1, img_w)
            scale_y = output_h / max(1, img_h)
            fit_scale = min(scale_x, scale_y)

            # Converti in percentuale zoom (massimo 100% per non ingrandire)
            fit_zoom = int(fit_scale * 100)
            fit_zoom = min(fit_zoom, 100)  # Non ingrandire oltre 100%
            fit_zoom = max(fit_zoom, 10)   # Minimo 10%

            layer.zoom = fit_zoom

            self.layers.append(layer)
            self.update_layers_list()

            # Seleziona il nuovo layer
            self.selected_layer = layer
            self.layers_listbox.selection_clear(0, tk.END)
            self.layers_listbox.selection_set(len(self.layers) - 1)
            self.update_layer_controls()

            self.file_label.config(text=t("canvas.elements", len(self.layers)))
            self.update_export_panels()
            self.redraw_canvas()

            logger.info(f"Immagine caricata: {name} ({img_w}x{img_h}) zoom={fit_zoom}%")

        except UnidentifiedImageError:
            logger.warning(f"UnidentifiedImageError: {filepath}")
            messagebox.showerror(t("dialog.error"), t("error.image_unsupported", Path(filepath).name))
        except Image.DecompressionBombError:
            logger.warning(f"DecompressionBombError: {filepath}")
            messagebox.showerror(t("dialog.error"), t("error.image_too_large", Path(filepath).name))
        except FileNotFoundError:
            logger.warning(f"File not found: {filepath}")
            messagebox.showerror(t("dialog.error"), t("error.image_not_found", Path(filepath).name))
        except PermissionError:
            logger.warning(f"Permission denied: {filepath}")
            messagebox.showerror(t("dialog.error"), t("error.image_permission", Path(filepath).name))
        except OSError as e:
            logger.exception(f"OSError caricamento immagine {filepath}: {e}")
            messagebox.showerror(t("dialog.error"), t("error.image_io", str(e)))
        except Exception as e:
            logger.exception(f"Errore caricamento immagine {filepath}: {e}")
            messagebox.showerror(t("dialog.error"), t("dialog.load_error", Path(filepath).name, str(e)))

    def load_video(self, filepath):
        """Carica un video - salva il percorso e usa il primo frame come anteprima"""
        if not VIDEO_SUPPORT:
            messagebox.showerror(t("dialog.error"), t("dialog.opencv_missing"))
            return

        cap = None
        try:
            filepath = str(filepath)
            if not os.path.isfile(filepath):
                logger.warning(f"File video non trovato: {filepath}")
                return

            cap = cv2.VideoCapture(filepath)
            if not cap.isOpened():
                logger.error(f"VideoCapture.isOpened() False: {filepath}")
                messagebox.showerror(
                    t("dialog.error"),
                    t("error.video_cannot_open", Path(filepath).name)
                )
                return

            # Metadata con guard
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps is None or fps <= 0:
                fps = 30.0  # Fallback sicuro
            frame_count = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1))
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

            if w <= 0 or h <= 0:
                logger.error(f"Video con dimensioni non valide {w}x{h}: {filepath}")
                messagebox.showerror(t("dialog.error"), t("error.video_invalid_dimensions"))
                return

            ret, frame = cap.read()
            if not ret or frame is None:
                logger.error(f"First frame read failed: {filepath}")
                messagebox.showerror(
                    t("dialog.error"),
                    t("error.video_codec_missing", Path(filepath).name)
                )
                return

            # Converti BGR -> RGB -> PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            duration = frame_count / fps if fps > 0 else 0

            cap.release()
            cap = None

            name = f"🎬{Path(filepath).stem[:15]}"
            layer = ImageLayer(img, name)
            layer.video_path = filepath
            layer.video_fps = fps
            layer.video_frames = frame_count
            layer.is_video = True

            # Calcola zoom per far stare nel canvas
            output_w = max(1, self.output_width.get())
            output_h = max(1, self.output_height.get())
            img_w, img_h = img.size

            if img_w == 0 or img_h == 0:
                logger.warning(f"Video con frame di dimensioni zero: {filepath}")
                return

            scale_x = output_w / max(1, img_w)
            scale_y = output_h / max(1, img_h)
            fit_scale = min(scale_x, scale_y)
            fit_zoom = int(fit_scale * 100)
            fit_zoom = min(fit_zoom, 100)
            fit_zoom = max(fit_zoom, 10)
            layer.zoom = fit_zoom

            self.layers.append(layer)
            self.update_layers_list()

            self.selected_layer = layer
            self.layers_listbox.selection_clear(0, tk.END)
            self.layers_listbox.selection_set(len(self.layers) - 1)
            self.update_layer_controls()

            self.file_label.config(text=t("canvas.elements_video", len(self.layers), f"{duration:.1f}", f"{fps:.0f}"))
            self.update_export_panels()
            self.redraw_canvas()

            logger.info(f"Video caricato: {name} ({img_w}x{img_h}) {duration:.1f}s @ {fps:.0f}fps")

        except cv2.error as e:
            logger.exception(f"cv2.error in load_video: {filepath}")
            messagebox.showerror(t("dialog.error"), t("error.video_cv2", str(e)))
        except Exception as e:
            logger.exception(f"Errore caricamento video {filepath}: {e}")
            messagebox.showerror(t("dialog.error"), t("dialog.video_load_error", filepath, str(e)))
        finally:
            if cap is not None:
                cap.release()

    def update_layers_list(self):
        """Aggiorna la lista dei layer"""
        self.layers_listbox.delete(0, tk.END)
        for i, layer in enumerate(self.layers):
            prefix = "▶ " if layer == self.selected_layer else "  "
            self.layers_listbox.insert(tk.END, f"{prefix}{i+1}. {layer.name}")

    def on_layer_select(self, event=None):
        """Gestisce la selezione di un layer dalla lista"""
        selection = self.layers_listbox.curselection()
        if selection:
            idx = selection[0]
            if 0 <= idx < len(self.layers):
                self.selected_layer = self.layers[idx]
                self.update_layer_controls()
                self.update_layers_list()
                self.redraw_canvas()

    def update_layer_controls(self):
        """Aggiorna i controlli con i valori del layer selezionato"""
        if self.selected_layer:
            self.zoom_var.set(self.selected_layer.zoom)
            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, str(self.selected_layer.zoom))
            self.rotation_var.set(self.selected_layer.rotation)
            self.rotation_entry.delete(0, tk.END)
            self.rotation_entry.insert(0, str(self.selected_layer.rotation))
            self.offset_x_var.set(self.selected_layer.offset_x)
            self.offset_x_entry.delete(0, tk.END)
            self.offset_x_entry.insert(0, str(self.selected_layer.offset_x))
            self.offset_y_var.set(self.selected_layer.offset_y)
            self.offset_y_entry.delete(0, tk.END)
            self.offset_y_entry.insert(0, str(self.selected_layer.offset_y))
            # Aggiorna dimensioni in pixel
            self.update_size_display()
        else:
            self.update_size_display()

    def remove_selected_layer(self):
        """Rimuove il layer selezionato e libera risorse"""
        if self.selected_layer and self.selected_layer in self.layers:
            layer_to_remove = self.selected_layer
            idx = self.layers.index(layer_to_remove)
            self.layers.remove(layer_to_remove)
            layer_to_remove.cleanup()  # Libera memoria
            # Seleziona il layer adiacente (precedente se possibile)
            if self.layers:
                new_idx = min(idx, len(self.layers) - 1)
                self.selected_layer = self.layers[new_idx]
            else:
                self.selected_layer = None
            self.update_layers_list()
            self.update_layer_controls()
            self.update_export_panels()
            self.file_label.config(text=t("canvas.elements", len(self.layers)) if self.layers else t("canvas.add_images_short"))
            self.redraw_canvas()

    def move_layer_up(self):
        """Sposta il layer selezionato in alto (sopra gli altri)"""
        if self.selected_layer and self.selected_layer in self.layers:
            idx = self.layers.index(self.selected_layer)
            if idx < len(self.layers) - 1:
                self.layers[idx], self.layers[idx+1] = self.layers[idx+1], self.layers[idx]
                self.update_layers_list()
                self.layers_listbox.selection_set(idx + 1)
                self.redraw_canvas()

    def move_layer_down(self):
        """Sposta il layer selezionato in basso (sotto gli altri)"""
        if self.selected_layer and self.selected_layer in self.layers:
            idx = self.layers.index(self.selected_layer)
            if idx > 0:
                self.layers[idx], self.layers[idx-1] = self.layers[idx-1], self.layers[idx]
                self.update_layers_list()
                self.layers_listbox.selection_set(idx - 1)
                self.redraw_canvas()

    def duplicate_layer(self):
        """Duplica il layer selezionato"""
        if self.selected_layer:
            new_layer = ImageLayer(self.selected_layer.original_image.copy(),
                                   f"{self.selected_layer.name}{t('layer.copy_suffix')}")
            new_layer.zoom = self.selected_layer.zoom
            new_layer.rotation = self.selected_layer.rotation
            new_layer.offset_x = self.selected_layer.offset_x + 50
            new_layer.offset_y = self.selected_layer.offset_y + 50
            new_layer.flip_h = self.selected_layer.flip_h
            new_layer.flip_v = self.selected_layer.flip_v

            self.layers.append(new_layer)
            self.selected_layer = new_layer
            self.update_layers_list()
            self.update_layer_controls()
            self.redraw_canvas()

    def center_selected_layer(self):
        """Centra il layer selezionato"""
        if self.selected_layer:
            self.selected_layer.offset_x = 0
            self.selected_layer.offset_y = 0
            self.offset_x_var.set(0)
            self.offset_y_var.set(0)
            self.offset_x_entry.delete(0, tk.END)
            self.offset_x_entry.insert(0, "0")
            self.offset_y_entry.delete(0, tk.END)
            self.offset_y_entry.insert(0, "0")
            self.redraw_canvas()

    def fit_keep_aspect(self):
        """Adatta il layer mantenendo le proporzioni (fit inside canvas)"""
        if not self.selected_layer:
            return
        orig_w, orig_h = self.selected_layer.original_image.size
        if orig_w == 0 or orig_h == 0:
            return
        output_w = self.output_width.get()
        output_h = self.output_height.get()

        # Calcola zoom per far entrare l'immagine nel canvas mantenendo proporzioni
        zoom_w = (output_w / orig_w) * 100
        zoom_h = (output_h / orig_h) * 100
        new_zoom = int(min(zoom_w, zoom_h))
        new_zoom = max(1, min(1000, new_zoom))

        self._apply_zoom_and_center(new_zoom)

    def fit_contain(self):
        """Adatta il layer per riempire completamente il canvas (cover)"""
        if not self.selected_layer:
            return
        orig_w, orig_h = self.selected_layer.original_image.size
        if orig_w == 0 or orig_h == 0:
            return
        output_w = self.output_width.get()
        output_h = self.output_height.get()

        # Calcola zoom per coprire il canvas (potrebbe tagliare)
        zoom_w = (output_w / orig_w) * 100
        zoom_h = (output_h / orig_h) * 100
        new_zoom = int(max(zoom_w, zoom_h))
        new_zoom = max(1, min(1000, new_zoom))

        self._apply_zoom_and_center(new_zoom)

    def fit_fill_horizontal(self):
        """Adatta il layer per riempire orizzontalmente il canvas"""
        if not self.selected_layer:
            return
        orig_w, orig_h = self.selected_layer.original_image.size
        if orig_w == 0:
            return
        output_w = self.output_width.get()

        # Calcola zoom per riempire in larghezza
        new_zoom = int((output_w / orig_w) * 100)
        new_zoom = max(1, min(1000, new_zoom))

        self._apply_zoom_and_center(new_zoom)

    def fit_fill_vertical(self):
        """Adatta il layer per riempire verticalmente il canvas"""
        if not self.selected_layer:
            return
        orig_w, orig_h = self.selected_layer.original_image.size
        if orig_h == 0:
            return
        output_h = self.output_height.get()

        # Calcola zoom per riempire in altezza
        new_zoom = int((output_h / orig_h) * 100)
        new_zoom = max(1, min(1000, new_zoom))

        self._apply_zoom_and_center(new_zoom)

    def _apply_zoom_and_center(self, new_zoom):
        """Applica lo zoom e centra il layer"""
        self.selected_layer.zoom = new_zoom
        self.selected_layer.offset_x = 0
        self.selected_layer.offset_y = 0

        self.zoom_var.set(new_zoom)
        self.zoom_entry.delete(0, tk.END)
        self.zoom_entry.insert(0, str(new_zoom))
        self.offset_x_var.set(0)
        self.offset_y_var.set(0)
        self.offset_x_entry.delete(0, tk.END)
        self.offset_x_entry.insert(0, "0")
        self.offset_y_entry.delete(0, tk.END)
        self.offset_y_entry.insert(0, "0")

        self.redraw_canvas()
        self.update_size_display()

    # ==================== LAYER CONTROLS ====================

    def on_zoom_change(self, event=None):
        if self.selected_layer:
            self.selected_layer.zoom = int(self.zoom_var.get())
            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, str(self.selected_layer.zoom))
            self.redraw_canvas()
            self.update_size_display()

    def on_zoom_entry(self, event=None):
        if self.selected_layer:
            try:
                value = int(self.zoom_entry.get())
                value = max(1, min(1000, value))
                self.selected_layer.zoom = value
                self.zoom_var.set(value)
                self.zoom_entry.delete(0, tk.END)
                self.zoom_entry.insert(0, str(value))
                self.redraw_canvas()
                self.update_size_display()
            except ValueError:
                pass

    def adjust_layer_zoom(self, delta):
        if self.selected_layer:
            new_zoom = max(1, min(1000, self.selected_layer.zoom + delta))
            self.selected_layer.zoom = new_zoom
            self.zoom_var.set(new_zoom)
            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, str(new_zoom))
            self.redraw_canvas()
            self.update_size_display()

    def reset_layer_zoom(self):
        if self.selected_layer:
            self.selected_layer.zoom = 100
            self.zoom_var.set(100)
            self.zoom_entry.delete(0, tk.END)
            self.zoom_entry.insert(0, "100")
            self.redraw_canvas()
            self.update_size_display()

    def on_rotation_change(self, event=None):
        if self.selected_layer:
            self.selected_layer.rotation = int(self.rotation_var.get())
            self.selected_layer.invalidate_cache()
            self.rotation_entry.delete(0, tk.END)
            self.rotation_entry.insert(0, str(self.selected_layer.rotation))
            self.redraw_canvas()

    def on_rotation_entry(self, event=None):
        if self.selected_layer:
            try:
                value = int(self.rotation_entry.get())
                value = max(-180, min(180, value))
                self.selected_layer.rotation = value
                self.selected_layer.invalidate_cache()
                self.rotation_var.set(value)
                self.rotation_entry.delete(0, tk.END)
                self.rotation_entry.insert(0, str(value))
                self.redraw_canvas()
            except ValueError:
                pass

    def set_layer_rotation(self, angle):
        if self.selected_layer:
            self.selected_layer.rotation = angle
            self.selected_layer.invalidate_cache()
            self.rotation_var.set(angle)
            self.rotation_entry.delete(0, tk.END)
            self.rotation_entry.insert(0, str(angle))
            self.redraw_canvas()

    def on_position_change(self, event=None):
        if self.selected_layer:
            self.selected_layer.offset_x = int(self.offset_x_var.get())
            self.selected_layer.offset_y = int(self.offset_y_var.get())
            self.offset_x_entry.delete(0, tk.END)
            self.offset_x_entry.insert(0, str(self.selected_layer.offset_x))
            self.offset_y_entry.delete(0, tk.END)
            self.offset_y_entry.insert(0, str(self.selected_layer.offset_y))
            self.redraw_canvas()

    def on_position_entry(self, event=None):
        if self.selected_layer:
            try:
                x_val = int(self.offset_x_entry.get())
                y_val = int(self.offset_y_entry.get())
                self.selected_layer.offset_x = x_val
                self.selected_layer.offset_y = y_val
                self.offset_x_var.set(x_val)
                self.offset_y_var.set(y_val)
                self.redraw_canvas()
            except ValueError:
                pass

    def flip_horizontal(self):
        """Applica effetto specchio orizzontale"""
        if self.selected_layer:
            self.selected_layer.flip_h = not self.selected_layer.flip_h
            self.selected_layer.invalidate_cache()
            self.redraw_canvas()

    def flip_vertical(self):
        """Applica effetto specchio verticale"""
        if self.selected_layer:
            self.selected_layer.flip_v = not self.selected_layer.flip_v
            self.selected_layer.invalidate_cache()
            self.redraw_canvas()

    # ==================== CANVAS RENDERING ====================

    def get_layer_bounds(self, layer, output_w, output_h):
        """Calcola i bounds di un layer nell'output"""
        img = layer.get_transformed_image()
        img_w, img_h = img.size

        # Applica zoom
        zoom = layer.zoom / 100.0
        final_w = int(img_w * zoom)
        final_h = int(img_h * zoom)

        # Posizione centrata + offset
        x = (output_w - final_w) // 2 + layer.offset_x
        y = (output_h - final_h) // 2 + layer.offset_y

        return (x, y, final_w, final_h)

    def create_composite_image(self, output_w, output_h, for_export=False, target_size=None):
        """Crea l'immagine composita di tutti i layer

        Args:
            output_w, output_h: dimensioni output (logiche)
            for_export: se True usa LANCZOS per qualità migliore
            target_size: (w, h) - se fornito, crea direttamente a questa dimensione
                        (evita resize successivo, molto più veloce per la preview)
        """
        # Protezione dimensioni minime
        output_w = max(1, output_w)
        output_h = max(1, output_h)

        # Per la preview: crea direttamente a target_size evitando resize enorme
        if target_size:
            target_w, target_h = target_size
            target_w = max(1, target_w)
            target_h = max(1, target_h)
            scale = min(target_w / max(1, output_w), target_h / max(1, output_h))
            out_img = Image.new('RGBA', (target_w, target_h), color=self.bg_color_var.get())
            resample = Image.Resampling.NEAREST  # Veloce per preview
        else:
            scale = 1.0
            out_img = Image.new('RGBA', (output_w, output_h), color=self.bg_color_var.get())
            resample = Image.Resampling.LANCZOS if for_export else Image.Resampling.BILINEAR

        # Disegna ogni layer dal basso verso l'alto
        for layer in self.layers:
            try:
                if target_size:
                    # Preview durante drag: fast_mode=True usa NEAREST (piu' veloce)
                    fast = self.is_dragging
                    img = layer.get_transformed_image(use_cache=not fast, zoom=layer.zoom, fast_mode=fast)
                    if img is None:
                        continue
                    new_w = max(1, int(img.size[0] * scale))
                    new_h = max(1, int(img.size[1] * scale))
                    img = img.resize((new_w, new_h), resample)
                    x = (target_w - new_w) // 2 + int(layer.offset_x * scale)
                    y = (target_h - new_h) // 2 + int(layer.offset_y * scale)
                else:
                    # Export: base + resize con LANCZOS per qualita' massima
                    img = layer.get_transformed_image(use_cache=True, zoom=None, fast_mode=False)
                    if img is None:
                        continue
                    zoom_pct = layer.zoom / 100.0
                    new_w = max(1, int(img.size[0] * zoom_pct))
                    new_h = max(1, int(img.size[1] * zoom_pct))
                    img = img.resize((new_w, new_h), resample)
                    x = (output_w - new_w) // 2 + layer.offset_x
                    y = (output_h - new_h) // 2 + layer.offset_y

                try:
                    out_img.paste(img, (x, y), img)
                except ValueError:
                    try:
                        out_img.paste(img, (x, y))
                    except Exception:
                        pass
            except Exception as e:
                logger.warning(f"Errore rendering layer {layer.name}: {e}")
                continue

        return out_img.convert('RGB')

    def _schedule_redraw(self, delay_ms=16):
        """Schedula un redraw con debounce (evita accumulo eventi durante drag)"""
        if self._redraw_job is not None:
            self.root.after_cancel(self._redraw_job)
        self._redraw_job = self.root.after(delay_ms, self._do_redraw)

    def _do_redraw(self):
        """Esegue il redraw effettivo"""
        self._redraw_job = None
        self._redraw_canvas_internal()

    def redraw_canvas(self, immediate=False):
        """Ridisegna il canvas (con debounce per evitare lag durante interazioni)"""
        if immediate:
            self._redraw_canvas_internal()
        else:
            # Durante drag: 33ms (~30fps) per ridurre carico; altrimenti 16ms (~60fps)
            delay = 33 if self.is_dragging else 16
            self._schedule_redraw(delay)

    def _redraw_canvas_internal(self):
        """Implementazione interna del redraw"""
        if not self.layers:
            self._canvas_persistent_ids = None
            self.draw_empty_canvas()
            return

        # Usa cache dimensioni (aggiornata su Configure); fallback se non valida
        canvas_w, canvas_h = self._cached_canvas_size
        if canvas_w < 10 or canvas_h < 10:
            self.canvas.update_idletasks()
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            self._cached_canvas_size = (canvas_w, canvas_h)

        if canvas_w < 10 or canvas_h < 10:
            return

        output_w = max(1, self.output_width.get())
        output_h = max(1, self.output_height.get())

        # Scala preview (guard edge case: canvas_w/h = 0)
        canvas_w_safe = max(1, canvas_w)
        canvas_h_safe = max(1, canvas_h)
        self.preview_scale = max(1e-6, min(canvas_w_safe / output_w, canvas_h_safe / output_h) * PREVIEW_SCALE_MARGIN)
        preview_w = max(1, int(output_w * self.preview_scale))
        preview_h = max(1, int(output_h * self.preview_scale))

        # Crea composita direttamente a risoluzione preview (evita resize da 4K->preview)
        composite = self.create_composite_image(
            output_w, output_h, for_export=False, target_size=(preview_w, preview_h)
        )
        self.display_image = ImageTk.PhotoImage(composite)

        canvas_x = (canvas_w - preview_w) // 2
        canvas_y = (canvas_h - preview_h) // 2
        self.canvas_bounds = (canvas_x, canvas_y, preview_w, preview_h)

        # Riusa oggetti canvas invece di delete/create ogni frame
        if self._canvas_persistent_ids is None:
            self.canvas.delete("all")
            bg_id = self.canvas.create_rectangle(0, 0, canvas_w, canvas_h, fill="#0a1929", outline="", tags="persistent")
            img_id = self.canvas.create_image(canvas_x, canvas_y, anchor=tk.NW, image=self.display_image, tags="persistent")
            border_id = self.canvas.create_rectangle(canvas_x-1, canvas_y-1, canvas_x+preview_w+1, canvas_y+preview_h+1,
                                                    outline="#666666", width=1, tags="persistent")
            self._canvas_persistent_ids = {"bg": bg_id, "img": img_id, "border": border_id}
        else:
            self.canvas.delete("handles")
            self.canvas.coords(self._canvas_persistent_ids["bg"], 0, 0, canvas_w, canvas_h)
            self.canvas.coords(self._canvas_persistent_ids["img"], canvas_x, canvas_y)
            self.canvas.itemconfig(self._canvas_persistent_ids["img"], image=self.display_image)
            self.canvas.coords(self._canvas_persistent_ids["border"],
                              canvas_x-1, canvas_y-1, canvas_x+preview_w+1, canvas_y+preview_h+1)

        # Calcola e salva bounds di ogni layer nel canvas
        for layer in self.layers:
            bounds = self.get_layer_bounds(layer, output_w, output_h)
            lx = canvas_x + int(bounds[0] * self.preview_scale)
            ly = canvas_y + int(bounds[1] * self.preview_scale)
            lw = int(bounds[2] * self.preview_scale)
            lh = int(bounds[3] * self.preview_scale)
            layer.bounds_in_canvas = (lx, ly, lw, lh)

        # Disegna handle (sempre create fresh, posizioni variabili)
        if self.selected_layer and self.selected_layer.bounds_in_canvas:
            self.draw_selection_handles(self.selected_layer)

        self.info_label.config(text=t("canvas.output_layers", output_w, output_h, len(self.layers)))

    def draw_selection_handles(self, layer):
        """Disegna gli handle di selezione per un layer (tag handles per riuso canvas)"""
        if layer.bounds_in_canvas is None:
            return

        x, y, w, h = layer.bounds_in_canvas

        self.handles.clear()

        # Rettangolo selezione e handle con tag per delete selettivo
        self.canvas.create_rectangle(x, y, x+w, y+h,
                                     outline=HANDLE_COLOR, width=2, dash=(4, 4), tags="handles")

        positions = {
            'nw': (x, y), 'n': (x + w//2, y), 'ne': (x + w, y),
            'e': (x + w, y + h//2), 'se': (x + w, y + h),
            's': (x + w//2, y + h), 'sw': (x, y + h), 'w': (x, y + h//2),
        }
        rotate_x = x + w//2
        rotate_y = y - ROTATION_HANDLE_DISTANCE
        positions['rotate'] = (rotate_x, rotate_y)

        self.canvas.create_line(x + w//2, y, rotate_x, rotate_y, fill=HANDLE_COLOR, width=2, tags="handles")

        for handle_id, (hx, hy) in positions.items():
            self.handles[handle_id] = (hx, hy)
            if handle_id == 'rotate':
                self.canvas.create_oval(hx - HANDLE_SIZE - 2, hy - HANDLE_SIZE - 2,
                                        hx + HANDLE_SIZE + 2, hy + HANDLE_SIZE + 2,
                                        fill="#00aa00", outline="white", width=2, tags="handles")
                self.canvas.create_text(hx, hy, text="↻", fill="white", font=('Segoe UI', 9, 'bold'), tags="handles")
            else:
                hs = HANDLE_SIZE // 2
                self.canvas.create_rectangle(hx - hs, hy - hs, hx + hs, hy + hs,
                                            fill="white", outline=HANDLE_COLOR, width=2, tags="handles")

    # ==================== MOUSE EVENTS ====================

    def get_handle_at(self, x, y):
        """Trova handle alla posizione"""
        for handle_id, (hx, hy) in self.handles.items():
            dist = math.sqrt((x - hx)**2 + (y - hy)**2)
            threshold = HANDLE_SIZE * 2 if handle_id == 'rotate' else HANDLE_SIZE * 1.5
            if dist <= threshold:
                return handle_id
        return None

    def get_layer_at(self, x, y):
        """Trova il layer alla posizione (dall'alto verso il basso)"""
        for layer in reversed(self.layers):
            if layer.bounds_in_canvas:
                lx, ly, lw, lh = layer.bounds_in_canvas
                if lx <= x <= lx + lw and ly <= y <= ly + lh:
                    return layer
        return None

    def on_mouse_down(self, event):
        if not self.layers:
            return

        # Controlla handle del layer selezionato
        if self.selected_layer:
            handle = self.get_handle_at(event.x, event.y)
            if handle:
                self.active_handle = handle
                self.is_dragging = True

                if handle == 'rotate':
                    if self.selected_layer.bounds_in_canvas:
                        bx, by, bw, bh = self.selected_layer.bounds_in_canvas
                        self.rotation_center = (bx + bw//2, by + bh//2)
                        self.rotation_start_angle = math.atan2(event.y - self.rotation_center[1],
                                                               event.x - self.rotation_center[0])
                        self.rotation_start_value = self.selected_layer.rotation
                else:
                    self.resize_start_zoom = self.selected_layer.zoom
                    self.resize_start_pos = (event.x, event.y)
                    if self.selected_layer.bounds_in_canvas:
                        bx, by, bw, bh = self.selected_layer.bounds_in_canvas
                        self.rotation_center = (bx + bw//2, by + bh//2)
                return

        # Controlla click su layer
        clicked_layer = self.get_layer_at(event.x, event.y)

        if clicked_layer:
            self.selected_layer = clicked_layer
            self.is_dragging = True
            self.active_handle = None
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.drag_start_offset_x = clicked_layer.offset_x
            self.drag_start_offset_y = clicked_layer.offset_y

            # Aggiorna selezione nella lista
            idx = self.layers.index(clicked_layer)
            self.layers_listbox.selection_clear(0, tk.END)
            self.layers_listbox.selection_set(idx)
            self.update_layer_controls()
            self.update_layers_list()
            self.redraw_canvas()
        else:
            # Click fuori - deseleziona
            self.selected_layer = None
            self.layers_listbox.selection_clear(0, tk.END)
            self.update_layers_list()
            self.redraw_canvas()

    def on_mouse_move(self, event):
        if not self.is_dragging or not self.selected_layer:
            return

        if self.active_handle == 'rotate':
            # Rotazione
            cx, cy = self.rotation_center
            current_angle = math.atan2(event.y - cy, event.x - cx)
            angle_diff = math.degrees(current_angle - self.rotation_start_angle)

            new_rotation = self.rotation_start_value + angle_diff
            while new_rotation > 180: new_rotation -= 360
            while new_rotation < -180: new_rotation += 360

            self.selected_layer.rotation = int(new_rotation)
            self.rotation_var.set(int(new_rotation))
            self.rotation_entry.delete(0, tk.END)
            self.rotation_entry.insert(0, str(int(new_rotation)))
            self.redraw_canvas()

        elif self.active_handle:
            # Resize
            cx, cy = self.rotation_center
            dx = event.x - cx
            dy = event.y - cy
            current_dist = math.sqrt(dx**2 + dy**2)

            start_dx = self.resize_start_pos[0] - cx
            start_dy = self.resize_start_pos[1] - cy
            start_dist = math.sqrt(start_dx**2 + start_dy**2)

            if start_dist > 5:
                scale = current_dist / start_dist
                new_zoom = max(1, min(1000, int(self.resize_start_zoom * scale)))
                self.selected_layer.zoom = new_zoom
                self.zoom_var.set(new_zoom)
                self.zoom_entry.delete(0, tk.END)
                self.zoom_entry.insert(0, str(new_zoom))
                self.redraw_canvas()
                self.update_size_display()
        else:
            # Spostamento
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y

            scale = 1.0 / self.preview_scale if self.preview_scale > 0 else 1.0

            self.selected_layer.offset_x = self.drag_start_offset_x + int(dx * scale)
            self.selected_layer.offset_y = self.drag_start_offset_y + int(dy * scale)

            self.offset_x_var.set(self.selected_layer.offset_x)
            self.offset_y_var.set(self.selected_layer.offset_y)

            self.redraw_canvas()

    def on_mouse_up(self, event):
        self.is_dragging = False
        self.active_handle = None
        if self.layers:
            self.redraw_canvas()

    def on_mouse_hover(self, event):
        if not self.layers:
            self.canvas.config(cursor="")
            return

        if self.selected_layer:
            handle = self.get_handle_at(event.x, event.y)
            if handle:
                cursors = {
                    'nw': 'size_nw_se', 'se': 'size_nw_se',
                    'ne': 'size_ne_sw', 'sw': 'size_ne_sw',
                    'n': 'size_ns', 's': 'size_ns',
                    'e': 'size_we', 'w': 'size_we',
                    'rotate': 'exchange'
                }
                self.canvas.config(cursor=cursors.get(handle, 'arrow'))
                return

        layer = self.get_layer_at(event.x, event.y)
        if layer:
            self.canvas.config(cursor="fleur" if layer == self.selected_layer else "hand2")
        else:
            self.canvas.config(cursor="")

    def on_mouse_wheel(self, event):
        """Zoom con mouse wheel sul canvas - sensibilità ridotta"""
        if self.selected_layer:
            # Delta più piccolo per zoom più delicato
            delta = 1 if event.delta > 0 else -1
            self.adjust_layer_zoom(delta)

    def on_left_panel_scroll(self, event):
        """Scroll del pannello sinistro con mouse wheel"""
        if event.delta != 0:
            self.left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"  # Previene propagazione

    def _bind_scroll_to_children_once(self, widget):
        """Bind ricorsivo dello scroll a tutti i widget figli (eseguito una sola volta)"""
        if self._scroll_bound:
            return
        self._scroll_bound = True
        self._bind_scroll_to_children(widget)

    def _bind_scroll_to_children(self, widget):
        """Bind ricorsivo dello scroll a tutti i widget figli"""
        for child in widget.winfo_children():
            child.bind("<MouseWheel>", self.on_left_panel_scroll)
            self._bind_scroll_to_children(child)

    def on_canvas_resize(self, event):
        """Gestisce il resize del canvas con debounce per evitare lag"""
        if self._resize_job is not None:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(50, self._do_canvas_resize)

    def _do_canvas_resize(self):
        """Esegue il resize effettivo dopo il debounce"""
        self._resize_job = None
        self._cached_canvas_size = (self.canvas.winfo_width(), self.canvas.winfo_height())
        if self.layers:
            self.redraw_canvas()
        else:
            self.draw_empty_canvas()

    def on_delete_key(self, event=None):
        if self.selected_layer:
            self.remove_selected_layer()

    def on_escape_key(self, event=None):
        self.selected_layer = None
        self.layers_listbox.selection_clear(0, tk.END)
        self.update_layers_list()
        self.redraw_canvas()

    # ==================== OUTPUT SETTINGS ====================

    def on_preset_change(self, event=None):
        preset = self.preset_combo.get()
        pid = preset_display_to_id(preset)
        resolution = preset_id_to_resolution(pid)
        if resolution:
            self.output_width.set(resolution[0])
            self.output_height.set(resolution[1])
            self.redraw_canvas()

    def apply_resolution(self):
        try:
            w = int(self.output_width.get())
            h = int(self.output_height.get())
            if w < 1 or h < 1:
                raise ValueError("Dimensioni non valide")
            self.preset_combo.set(t("preset.custom"))
            self.redraw_canvas()
        except (ValueError, tk.TclError):
            messagebox.showerror(t("dialog.error"), t("dialog.invalid_values"))

    def set_bg_color(self, color):
        self.bg_color_var.set(color)
        self.redraw_canvas()

    def choose_custom_color(self):
        from tkinter import colorchooser
        color = colorchooser.askcolor(title=t("dialog.choose_color"))
        if color[1]:
            self.set_bg_color(color[1])

    def on_img_quality_change(self, event=None):
        """Aggiorna info qualità (usato internamente)"""
        pass  # Info qualità aggiornata tramite preset

    def on_vid_quality_preset_change(self, event=None):
        """Aggiorna i parametri video in base al preset selezionato"""
        preset = self.vid_quality_preset.get()
        if preset == "bassa":
            self.vid_quality.set(50)
            self.vid_bitrate.set(2000)
            info_text = t("export_vid.bitrate", 2000, 28)
        elif preset == "media":
            self.vid_quality.set(75)
            self.vid_bitrate.set(5000)
            info_text = t("export_vid.bitrate", 5000, 23)
        else:  # alta
            self.vid_quality.set(100)
            self.vid_bitrate.set(8000)
            info_text = t("export_vid.bitrate", 8000, 18)
        self.vid_quality_info_label.config(text=info_text)

    def set_video_export_enabled(self, enabled):
        """Abilita/disabilita il box esportazione video"""
        state = 'normal' if enabled else 'disabled'
        for child in self.video_export_frame.winfo_children():
            self._set_widget_state(child, state)
        # Cambia colore del frame
        if enabled:
            self.video_export_frame.config(text=t("export_vid.title"))
        else:
            self.video_export_frame.config(text=t("export_vid.title_disabled"))

    def set_image_export_enabled(self, enabled):
        """Abilita/disabilita il box esportazione immagine"""
        state = 'normal' if enabled else 'disabled'
        for child in self.image_export_frame.winfo_children():
            self._set_widget_state(child, state)
        if enabled:
            self.image_export_frame.config(text=t("export_img.title"))
        else:
            self.image_export_frame.config(text=t("export_img.title_disabled"))

    def _set_widget_state(self, widget, state):
        """Imposta ricorsivamente lo stato di un widget e i suoi figli"""
        try:
            widget.config(state=state)
        except tk.TclError:
            pass  # Widget non supporta state
        except Exception:
            pass
        for child in widget.winfo_children():
            self._set_widget_state(child, state)

    def update_export_panels(self):
        """Aggiorna i pannelli di esportazione in base ai layer presenti"""
        has_videos = any(getattr(layer, 'is_video', False) for layer in self.layers)

        # Se non ci sono layer, disabilita entrambi
        if not self.layers:
            self.set_image_export_enabled(False)
            self.set_video_export_enabled(False)
        else:
            # Immagine sempre abilitata se ci sono layer (può esportare un frame)
            self.set_image_export_enabled(True)
            # Video solo se c'è almeno un video
            self.set_video_export_enabled(has_videos)

    def clear_all(self):
        """Rimuove tutti i layer e libera risorse"""
        if self.layers:
            if messagebox.askyesno(t("dialog.confirm"), t("dialog.confirm_clear")):
                for layer in self.layers:
                    layer.cleanup()
                self.layers.clear()
                self.selected_layer = None
                self.update_layers_list()
                self.update_export_panels()
                self.file_label.config(text=t("canvas.add_images_full"))
                self.redraw_canvas()

    def on_closing(self):
        """Gestisce la chiusura della finestra: cancella export in corso, libera risorse."""
        # Segnala a eventuali thread di export di fermarsi
        self._export_cancelled.set()

        # Cancella job debounce pendenti
        if self._redraw_job is not None:
            try:
                self.root.after_cancel(self._redraw_job)
            except Exception:
                pass
        if self._resize_job is not None:
            try:
                self.root.after_cancel(self._resize_job)
            except Exception:
                pass

        # Cleanup tutti i layer
        for layer in self.layers:
            try:
                layer.cleanup()
            except Exception:
                pass
        self.layers.clear()

        gc.collect()
        logger.info("Applicazione chiusa - risorse liberate")
        self.root.destroy()

    # ==================== EXPORT ====================

    def _start_export(self):
        """Prepara UI per export: mostra progress bar e pulsante Annulla."""
        self._export_cancelled.clear()
        self.progress.start()
        self.cancel_btn.pack(fill=tk.X, pady=(0, 8))

    def _stop_export(self):
        """Ripristina UI dopo export: nasconde progress bar e pulsante Annulla."""
        self.progress.stop()
        self.cancel_btn.pack_forget()

    def cancel_export(self):
        """Annulla l'export in corso."""
        self._export_cancelled.set()
        logger.info("Export annullato dall'utente")
        self.root.after(0, self._stop_export)
        self.root.after(0, lambda: self.info_label.config(text=t("export_cancelled")))

    def export_image(self):
        """Esporta come immagine"""
        if not self.layers:
            messagebox.showwarning(t("dialog.warning"), t("dialog.add_one_image"))
            return

        fmt = self.output_format.get()
        ext = f".{fmt}"

        filepath = filedialog.asksaveasfilename(
            title=t("dialog.save_collage"),
            defaultextension=ext,
            initialfile=f"collage{ext}",
            filetypes=[(fmt.upper(), f"*{ext}")]
        )

        if not filepath:
            return

        self._start_export()
        thread = threading.Thread(target=self._do_export_image, args=(filepath,), daemon=True)
        thread.start()

    def export_video(self):
        """Esporta come video"""
        if not VIDEO_SUPPORT:
            messagebox.showerror(t("dialog.error"), t("dialog.opencv_missing"))
            return

        # Trova video nei layer
        video_layers = [layer for layer in self.layers if hasattr(layer, 'is_video') and layer.is_video]
        if not video_layers:
            messagebox.showwarning(t("dialog.warning"), t("dialog.no_video"))
            return

        fmt = self.video_format.get()
        ext = f".{fmt}"

        filepath = filedialog.asksaveasfilename(
            title=t("dialog.save_video"),
            defaultextension=ext,
            initialfile=f"video_output{ext}",
            filetypes=[(fmt.upper(), f"*{ext}")]
        )

        if not filepath:
            return

        self._start_export()
        thread = threading.Thread(target=self._do_export_video, args=(filepath, video_layers[0]), daemon=True)
        thread.start()

    def _do_export_image(self, filepath):
        """Esporta come immagine a piena risoluzione.
        Per i layer con _original_path (working copy ridotta), ricarica da disco
        l'immagine originale ad alta risoluzione prima del compositing.
        """
        restored_images = {}
        try:
            # Snapshot dei valori dal thread principale (thread-safety)
            # NOTA: .get() su IntVar/StringVar e' thread-safe in Tkinter CPython
            output_w = self.output_width.get()
            output_h = self.output_height.get()
            quality = self.img_quality.get()

            logger.info(f"Export immagine: {output_w}x{output_h} -> {filepath}")

            # Sostituisci temporaneamente le working copy con gli originali ad alta risoluzione
            for layer in self.layers:
                if layer._original_path and os.path.isfile(layer._original_path):
                    try:
                        orig = Image.open(layer._original_path)
                        orig.load()
                        if orig.mode not in ('RGB', 'RGBA'):
                            orig = orig.convert('RGBA')
                        restored_images[layer.id] = layer.original_image
                        layer.original_image = orig
                        layer.invalidate_cache()
                        logger.info(f"Export: ripristinata immagine originale {layer.name} ({orig.size[0]}x{orig.size[1]})")
                    except Exception as e:
                        logger.warning(f"Export: impossibile ricaricare originale per {layer.name}: {e}")
                        # Fallback: usa working copy gia' in memoria

            # Usa for_export=True per qualita' massima (LANCZOS)
            img = self.create_composite_image(output_w, output_h, for_export=True)
            ext = Path(filepath).suffix.lower()

            if ext in ['.jpg', '.jpeg']:
                img.convert('RGB').save(filepath, 'JPEG', quality=quality, optimize=True)
            elif ext == '.png':
                img.save(filepath, 'PNG', optimize=True)
            elif ext == '.webp':
                img.save(filepath, 'WEBP', quality=quality)
            else:
                img.save(filepath)

            if self._export_cancelled.is_set():
                logger.info("Export immagine annullato")
                self.root.after(0, self._stop_export)
                return

            file_size = Path(filepath).stat().st_size
            logger.info(f"Export completato: {file_size / 1024:.1f} KB")

            self.root.after(0, self._stop_export)
            self.root.after(0, lambda: messagebox.showinfo(t("dialog.success"), t("dialog.collage_saved", filepath)))
        except Exception as ex:
            logger.error(f"Errore export immagine: {ex}")
            self.root.after(0, self._stop_export)
            self.root.after(0, lambda err=str(ex): messagebox.showerror(t("dialog.error"), err))
        finally:
            # Ripristina sempre le working copy per la preview
            for layer in self.layers:
                if layer.id in restored_images:
                    layer.original_image = restored_images[layer.id]
                    layer.invalidate_cache()
            gc.collect()

    def _do_export_video(self, filepath, video_layer):
        """Esporta video con tutte le trasformazioni applicate"""
        cap = None
        out = None
        cancelled = False
        try:
            output_w = max(1, self.output_width.get())
            output_h = max(1, self.output_height.get())
            fps = max(1, self.fps_var.get())
            ext = Path(filepath).suffix.lower()

            logger.info(f"Export video: {output_w}x{output_h} @ {fps}fps -> {filepath}")

            cap = cv2.VideoCapture(video_layer.video_path)
            if not cap.isOpened():
                raise Exception("Impossibile aprire il video sorgente")

            total_frames = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1))

            # Pre-calcola trasformazioni costanti (snapshot thread-safe)
            needs_flip_h = video_layer.flip_h
            needs_flip_v = video_layer.flip_v
            rotation = video_layer.rotation
            zoom = video_layer.zoom / 100.0
            offset_x = video_layer.offset_x
            offset_y = video_layer.offset_y
            bg_color = self.bg_color_var.get()

            # Codec in base al formato
            if ext == '.mp4':
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            elif ext == '.avi':
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
            elif ext == '.webm':
                fourcc = cv2.VideoWriter_fourcc(*'VP80')
            elif ext == '.gif':
                # Per GIF: processa a blocchi per limitare uso memoria
                frames = []
                frame_count = 0
                while frame_count < MAX_GIF_FRAMES:
                    if self._export_cancelled.is_set():
                        cancelled = True
                        break
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_frame = Image.fromarray(frame_rgb)
                    processed = self._process_video_frame_optimized(
                        pil_frame, output_w, output_h,
                        needs_flip_h, needs_flip_v, rotation, zoom,
                        offset_x, offset_y, bg_color
                    )

                    # Quantizza subito per risparmiare memoria (~75% in meno per frame)
                    frames.append(processed.quantize(colors=256, method=Image.Quantize.MEDIANCUT))
                    del processed, pil_frame  # Rilascio esplicito
                    frame_count += 1

                    if frame_count % 10 == 0:
                        progress_pct = int((frame_count / max(total_frames, 1)) * 100)
                        self.root.after(0, lambda p=progress_pct:
                                       self.info_label.config(text=t("export_gif_progress", p)))

                cap.release()
                cap = None

                if self._export_cancelled.is_set():
                    del frames
                    gc.collect()
                    logger.info("Export GIF annullato")
                    self.root.after(0, self._stop_export)
                    self.root.after(0, lambda: self.info_label.config(text=t("export_cancelled")))
                    return

                if frames:
                    frames[0].save(filepath, save_all=True, append_images=frames[1:],
                                   duration=int(1000 / max(fps, 1)), loop=0, optimize=True)
                    # Rilascia memoria GIF
                    del frames
                    gc.collect()

                logger.info(f"GIF esportata: {frame_count} frames")
                self.root.after(0, self._stop_export)
                self.root.after(0, lambda: self.info_label.config(text=""))
                self.root.after(0, lambda: messagebox.showinfo(t("dialog.success"), t("dialog.gif_saved", filepath, frame_count)))
                return
            else:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')

            out = cv2.VideoWriter(filepath, fourcc, fps, (output_w, output_h))
            if not out.isOpened():
                raise Exception("Impossibile creare il file video di output")

            frame_count = 0

            while True:
                if self._export_cancelled.is_set():
                    cancelled = True
                    break
                ret, frame = cap.read()
                if not ret:
                    break

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_frame = Image.fromarray(frame_rgb)

                processed = self._process_video_frame_optimized(
                    pil_frame, output_w, output_h,
                    needs_flip_h, needs_flip_v, rotation, zoom,
                    offset_x, offset_y, bg_color
                )

                output_frame = cv2.cvtColor(np.array(processed), cv2.COLOR_RGB2BGR)
                out.write(output_frame)

                frame_count += 1

                # Rilascio esplicito ogni 100 frame per video lunghi
                if frame_count % 100 == 0:
                    del pil_frame, processed, output_frame, frame_rgb
                    gc.collect()

                if frame_count % 10 == 0:
                    progress_pct = int((frame_count / total_frames) * 100)
                    self.root.after(0, lambda p=progress_pct, fc=frame_count, tf=total_frames:
                                   self.info_label.config(text=t("export_video_progress_frames", fc, tf, p)))

            if cancelled:
                logger.info(f"Export video annullato dall'utente al frame {frame_count}/{total_frames}")
                self.root.after(0, self._stop_export)
                self.root.after(0, lambda: self.info_label.config(text=t("export_cancelled")))
            else:
                logger.info(f"Video esportato: {frame_count} frames")
                self.root.after(0, self._stop_export)
                self.root.after(0, lambda: self.info_label.config(text=""))
                self.root.after(0, lambda: messagebox.showinfo(t("dialog.success"), t("dialog.video_saved", filepath, frame_count)))

        except Exception as ex:
            logger.exception(f"Errore export video: {ex}")
            self.root.after(0, self._stop_export)
            self.root.after(0, lambda: self.info_label.config(text=""))
            self.root.after(0, lambda err=str(ex): messagebox.showerror(t("dialog.error"), err))
        finally:
            # Release risorse OpenCV (vincolo sacro #6)
            if out is not None:
                try:
                    out.release()
                except Exception:
                    logger.exception("out.release() fallito")
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    logger.exception("cap.release() fallito")
            gc.collect()
            # Rimuovi file parziale se l'export è stato cancellato
            if cancelled and filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    logger.info(f"File parziale rimosso: {filepath}")
                except OSError as e:
                    logger.warning(f"Impossibile rimuovere file parziale {filepath}: {e}")
            # Stop export SEMPRE (evita progress bar bloccata su eccezione)
            try:
                self.root.after(0, self._stop_export)
            except Exception:
                pass

    def _process_video_frame_optimized(self, frame, output_w, output_h,
                                        flip_h, flip_v, rotation, zoom,
                                        offset_x, offset_y, bg_color):
        """Processa un singolo frame video (versione ottimizzata con parametri pre-calcolati)"""
        # Crea sfondo
        output = Image.new('RGB', (output_w, output_h), color=bg_color)

        img = frame
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Applica flip
        if flip_h:
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if flip_v:
            img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        # Applica rotazione
        if rotation != 0:
            img = img.rotate(-rotation, resample=Image.Resampling.BILINEAR, expand=True)

        # Applica zoom
        new_w = max(1, int(img.size[0] * zoom))
        new_h = max(1, int(img.size[1] * zoom))
        img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)

        # Posizione
        x = (output_w - new_w) // 2 + offset_x
        y = (output_h - new_h) // 2 + offset_y

        # Incolla
        output.paste(img, (x, y), img)

        return output

    def _process_video_frame(self, frame, video_layer, output_w, output_h):
        """Processa un singolo frame video con le trasformazioni del layer (legacy)"""
        return self._process_video_frame_optimized(
            frame, output_w, output_h,
            video_layer.flip_h, video_layer.flip_v, video_layer.rotation,
            video_layer.zoom / 100.0, video_layer.offset_x, video_layer.offset_y,
            self.bg_color_var.get()
        )


def main():
    init_language()
    root = tk.Tk()

    if _LICENSE_ENABLED:
        # Build installer: mostra gate licenza prima dell'app principale.
        # L'app viene avviata solo dopo conferma licenza valida.
        root.withdraw()  # Nascondi la finestra principale durante il gate

        def _start_app():
            root.deiconify()
            _center_window(root)
            _app = LiveVideoComposer(root)  # noqa: F841

        from license.gate import show_license_gate
        show_license_gate(root, _start_app)
    else:
        # Build portable: avvio diretto senza gate licenza.
        _app = LiveVideoComposer(root)  # noqa: F841
        _center_window(root)

    root.mainloop()


def _center_window(root: tk.Tk) -> None:
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    main()
