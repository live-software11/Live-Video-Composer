"""
Localization for Live Video Composer - IT/EN support.
Model: Live 3D LEDWall Render - instant language switch from header.
"""

import json
import os
from pathlib import Path

# Storage key for persisted language
_STORAGE_KEY = "live-video-composer-lang"
_CURRENT_LANG = "en"

# Translation dictionaries
_TRANSLATIONS = {
    "it": {
        "app.title": "Live Video Composer  •  Image & Video Editor",
        # Layers
        "layers.title": "⭐ Layers",
        "btn.add": "➕ Aggiungi",
        "btn.remove": "➖ Rimuovi",
        "btn.duplicate": "⧉ Duplica",
        "btn.center": "◎ Centra",
        # Transform
        "transform.title": "⚙️ Trasformazioni",
        "transform.scale": "🔍 Scala:",
        "transform.rotation": "🔄 Rotazione:",
        "transform.pan": "↔️ Pan (X):",
        "transform.tilt": "↕️ Tilt (Y):",
        # Size
        "size.title": "📐 Dimensioni (px)",
        "size.original": "Originale: {0}",
        "size.original_empty": "Originale: -",
        "size.lock": "🔒 Proporzioni bloccate",
        "size.unlock": "🔓 Proporzioni libere",
        "size.label_w": "L:",
        "size.label_h": "A:",
        # Fit
        "fit.title": "⬛ Adattamento",
        "fit.adapt": "📐 Adatta (contain)",
        "fit.fill": "⬛ Riempi (cover)",
        "fit.fill_h": "↔ Riempi orizzontale",
        "fit.fill_v": "↕ Riempi verticale",
        # Mirror
        "mirror.title": "⟷ Specchio",
        "mirror.h": "⇆ Orizzontale",
        "mirror.v": "⇅ Verticale",
        # Canvas
        "canvas.drag_hint": "⬚ Trascina qui le tue immagini",
        "canvas.instructions": "Click = Seleziona  •  Canc = Elimina  •  Trascina = Sposta  •  Handle = Ridimensiona/Ruota",
        "canvas.add_file": "⊕ Aggiungi File",
        "canvas.remove_all": "⊗ Rimuovi Tutto",
        "canvas.empty_text": "Trascina qui immagini o video",
        "canvas.empty_sub": "oppure clicca 'Aggiungi File'",
        "canvas.add_images": "Aggiungi immagini per iniziare",
        "canvas.elements": "📚 {0} elementi nel collage",
        "canvas.elements_video": "📚 {0} elementi | Video: {1}s @ {2}fps",
        "canvas.add_images_short": "📁 Aggiungi immagini",
        "canvas.add_images_full": "📁 Aggiungi immagini per creare un collage",
        "canvas.output": "Output: {0}x{1}",
        "canvas.output_layers": "Output: {0}x{1} | Layers: {2}",
        # Output
        "output.title": "⬡ Dimensioni Output",
        "output.preset": "Preset:",
        "output.apply": "✓ Applica",
        # Background
        "bg.title": "◐ Sfondo",
        "bg.custom": "⊞ Colore personalizzato",
        "bg.black": "Nero",
        "bg.white": "Bianco",
        "bg.gray": "Grigio",
        "bg.red": "Rosso",
        "bg.green": "Verde",
        "bg.blue": "Blu",
        "bg.yellow": "Giallo",
        "bg.magenta": "Magenta",
        "bg.cyan": "Ciano",
        # Export Image
        "export_img.title": "◳ Esporta Immagine",
        "export_img.title_disabled": "🖼️ Esporta Immagine (nessuna immagine)",
        "export_img.format": "Formato:",
        "export_img.quality": "Qualità:",
        "export_img.low": "Bassa",
        "export_img.medium": "Media",
        "export_img.high": "Alta",
        "export_img.btn": "▶ ESPORTA IMMAGINE",
        "export_img.dpi": "DPI: {0} | Bit: {1} | Compressione: {2}%",
        # Export Video
        "export_vid.title": "▷ Esporta Video",
        "export_vid.title_disabled": "🎬 Esporta Video (nessun video)",
        "export_vid.format": "Formato:",
        "export_vid.fps": "FPS:",
        "export_vid.quality": "Qualità:",
        "export_vid.btn": "▶ ESPORTA VIDEO",
        "export_vid.bitrate": "Bitrate: {0} kbps | CRF: {1}",
        # Cancel
        "cancel_export": "⊗ Annulla Export",
        "export_cancelled": "Export annullato",
        "export_gif_progress": "Esportazione GIF: {0}%",
        "export_video_progress": "Esportazione video: {0}%",
        # Dialogs
        "dialog.select_files": "Seleziona immagini o video",
        "dialog.save_collage": "Salva collage",
        "dialog.save_video": "Salva video",
        "dialog.choose_color": "Seleziona colore di sfondo",
        "dialog.confirm_clear": "Rimuovere tutti gli elementi?",
        "dialog.confirm": "Conferma",
        "dialog.warning": "Avviso",
        "dialog.error": "Errore",
        "dialog.success": "Successo",
        "dialog.file_large_video": "Il video è molto grande ({0} GB).\nL'esportazione potrebbe richiedere molto tempo.",
        "dialog.file_large_image": "L'immagine è molto grande ({0} MB).\nVerrà creata una copia di lavoro ridotta per la preview.",
        "dialog.file_large_title": "File grande",
        "dialog.unsupported": "Il file '{0}' non è un formato supportato.\nImmagini: {1}\nVideo: {2}",
        "dialog.unsupported_title": "Formato non supportato",
        "dialog.add_one_image": "Aggiungi almeno un'immagine",
        "dialog.no_video": "Nessun video caricato. Per esportare video carica almeno un file video.",
        "dialog.invalid_values": "Valori non validi",
        "dialog.load_error": "Impossibile caricare:\n{0}\n{1}",
        "dialog.video_load_error": "Impossibile caricare video:\n{0}\n{1}",
        "dialog.opencv_missing": "OpenCV non installato. Installare con: pip install opencv-python-headless",
        "dialog.collage_saved": "Collage salvato:\n{0}",
        "dialog.gif_saved": "GIF salvata:\n{0}\n{1} frames",
        "dialog.video_saved": "Video salvato:\n{0}\n{1} frames",
        "dialog.image_format_error": "Formato immagine non riconosciuto o file corrotto.",
        # Errori granulari (caricamento file)
        "error.image_unsupported": "Formato immagine non supportato o file corrotto:\n{0}",
        "error.image_too_large": "Immagine troppo grande (limite di sicurezza Pillow superato):\n{0}",
        "error.image_not_found": "File non trovato:\n{0}",
        "error.image_permission": "Permesso negato in lettura:\n{0}",
        "error.image_io": "Errore I/O lettura immagine: {0}",
        "error.video_cannot_open": "Impossibile aprire il video: {0}",
        "error.video_codec_missing": "Codec non disponibile per {0}.\nInstalla K-Lite Codec Pack.",
        "error.video_invalid_dimensions": "Dimensioni video non valide",
        "error.video_cv2": "Errore OpenCV: {0}",
        "export_video_progress_frames": "Esportazione video: {0}/{1} frame ({2}%)",
        # File types
        "filetypes.images_video": "Immagini e Video",
        "filetypes.images": "Immagini",
        "filetypes.video": "Video",
        "filetypes.all": "Tutti i file",
        # Resolution presets
        "preset.custom": "Personalizzato",
        "preset.fullhd": "1920x1080 (Full HD 16:9)",
        "preset.hd": "1280x720 (HD 16:9)",
        "preset.4k": "3840x2160 (4K 16:9)",
        "preset.vertical": "1080x1920 (Full HD 9:16 Verticale)",
        "preset.square": "1080x1080 (Quadrato 1:1)",
        "preset.banner": "1200x400 (Banner 3:1)",
        "preset.twitter": "1500x500 (Twitter Header 3:1)",
        "preset.facebook": "820x312 (Facebook Cover)",
        "preset.youtube": "1280x720 (YouTube Thumbnail)",
        "preset.instagram": "1080x608 (Instagram Landscape)",
        "preset.43a": "800x600 (4:3)",
        "preset.43b": "1024x768 (4:3)",
        # Default layer name
        "layer.default_name": "Immagine",
        "layer.copy_suffix": "_copia",
        # License gate
        "license.window_title": "Attivazione Licenza — Live Video Composer",
        "license.activation_required": "Licenza richiesta per utilizzare questa applicazione",
        "license.checking": "Verifica licenza in corso...",
        "license.verifying_online": "Verifica online in corso...",
        "license.enter_key": "Inserisci la chiave di licenza:",
        "license.enter_key_hint": "Inserisci la tua chiave di licenza per continuare.",
        "license.activate_btn": "▶ Attiva",
        "license.activating": "Attivazione...",
        "license.key_required": "Inserisci la chiave di licenza.",
        "license.invalid_key_format": "Formato chiave non valido. Usa: LIVE-XXXX-XXXX-XXXX-XXXX",
        "license.activation_failed": "Attivazione non riuscita. Controlla la chiave e riprova.",
        "license.network_error": "Impossibile contattare il server. Verifica la connessione.",
        "license.offline_hint": "Puoi continuare offline se la licenza era già attiva su questo PC.",
        "license.verify_failed": "Verifica fallita. Inserisci di nuovo la chiave.",
        "license.pending_approval": "⏳ In attesa di approvazione dell'amministratore...",
        "license.pending_hint": "L'attivazione è in attesa di approvazione. Verrà verificata automaticamente ogni 30 secondi.",
        "license.unexpected_error": "Errore imprevisto. Riprova o contatta il supporto.",
        "license.deactivate_confirm_title": "Disattiva Licenza",
        "license.deactivate_confirm": "Disattivare la licenza su questo PC?\n\nLa chiave potrà essere riusata su un altro PC.",
    },
    "en": {
        "app.title": "Live Video Composer  •  Image & Video Editor",
        "layers.title": "⭐ Layers",
        "btn.add": "➕ Add",
        "btn.remove": "➖ Remove",
        "btn.duplicate": "⧉ Duplicate",
        "btn.center": "◎ Center",
        "transform.title": "⚙️ Transform",
        "transform.scale": "🔍 Scale:",
        "transform.rotation": "🔄 Rotation:",
        "transform.pan": "↔️ Pan (X):",
        "transform.tilt": "↕️ Tilt (Y):",
        "size.title": "📐 Size (px)",
        "size.original": "Original: {0}",
        "size.original_empty": "Original: -",
        "size.lock": "🔒 Lock aspect ratio",
        "size.unlock": "🔓 Unlock aspect ratio",
        "size.label_w": "W:",
        "size.label_h": "H:",
        "fit.title": "⬛ Fit",
        "fit.adapt": "📐 Fit (contain)",
        "fit.fill": "⬛ Fill (cover)",
        "fit.fill_h": "↔ Fill horizontal",
        "fit.fill_v": "↕ Fill vertical",
        "mirror.title": "⟷ Mirror",
        "mirror.h": "⇆ Horizontal",
        "mirror.v": "⇅ Vertical",
        "canvas.drag_hint": "⬚ Drag your images here",
        "canvas.instructions": "Click = Select  •  Del = Delete  •  Drag = Move  •  Handle = Resize/Rotate",
        "canvas.add_file": "⊕ Add File",
        "canvas.remove_all": "⊗ Remove All",
        "canvas.empty_text": "Drag images or video here",
        "canvas.empty_sub": "or click 'Add File'",
        "canvas.add_images": "Add images to get started",
        "canvas.elements": "📚 {0} elements in collage",
        "canvas.elements_video": "📚 {0} elements | Video: {1}s @ {2}fps",
        "canvas.add_images_short": "📁 Add images",
        "canvas.add_images_full": "📁 Add images to create a collage",
        "canvas.output": "Output: {0}x{1}",
        "canvas.output_layers": "Output: {0}x{1} | Layers: {2}",
        "output.title": "⬡ Output Size",
        "output.preset": "Preset:",
        "output.apply": "✓ Apply",
        "bg.title": "◐ Background",
        "bg.custom": "⊞ Custom color",
        "bg.black": "Black",
        "bg.white": "White",
        "bg.gray": "Gray",
        "bg.red": "Red",
        "bg.green": "Green",
        "bg.blue": "Blue",
        "bg.yellow": "Yellow",
        "bg.magenta": "Magenta",
        "bg.cyan": "Cyan",
        "export_img.title": "◳ Export Image",
        "export_img.title_disabled": "🖼️ Export Image (no images)",
        "export_img.format": "Format:",
        "export_img.quality": "Quality:",
        "export_img.low": "Low",
        "export_img.medium": "Medium",
        "export_img.high": "High",
        "export_img.btn": "▶ EXPORT IMAGE",
        "export_img.dpi": "DPI: {0} | Bit: {1} | Compression: {2}%",
        "export_vid.title": "▷ Export Video",
        "export_vid.title_disabled": "🎬 Export Video (no video)",
        "export_vid.format": "Format:",
        "export_vid.fps": "FPS:",
        "export_vid.quality": "Quality:",
        "export_vid.btn": "▶ EXPORT VIDEO",
        "export_vid.bitrate": "Bitrate: {0} kbps | CRF: {1}",
        "cancel_export": "⊗ Cancel Export",
        "export_cancelled": "Export cancelled",
        "export_gif_progress": "Exporting GIF: {0}%",
        "export_video_progress": "Exporting video: {0}%",
        "dialog.select_files": "Select images or video",
        "dialog.save_collage": "Save collage",
        "dialog.save_video": "Save video",
        "dialog.choose_color": "Select background color",
        "dialog.confirm_clear": "Remove all elements?",
        "dialog.confirm": "Confirm",
        "dialog.warning": "Warning",
        "dialog.error": "Error",
        "dialog.success": "Success",
        "dialog.file_large_video": "The video is very large ({0} GB).\nExport may take a long time.",
        "dialog.file_large_image": "The image is very large ({0} MB).\nA reduced working copy will be created for preview.",
        "dialog.file_large_title": "Large file",
        "dialog.unsupported": "The file '{0}' is not a supported format.\nImages: {1}\nVideo: {2}",
        "dialog.unsupported_title": "Unsupported format",
        "dialog.add_one_image": "Add at least one image",
        "dialog.no_video": "No video loaded. To export video, load at least one video file.",
        "dialog.invalid_values": "Invalid values",
        "dialog.load_error": "Cannot load:\n{0}\n{1}",
        "dialog.video_load_error": "Cannot load video:\n{0}\n{1}",
        "dialog.opencv_missing": "OpenCV not installed. Install with: pip install opencv-python-headless",
        "dialog.collage_saved": "Collage saved:\n{0}",
        "dialog.gif_saved": "GIF saved:\n{0}\n{1} frames",
        "dialog.video_saved": "Video saved:\n{0}\n{1} frames",
        "dialog.image_format_error": "Unrecognized image format or corrupted file.",
        # Granular errors (file loading)
        "error.image_unsupported": "Unsupported image format or corrupted file:\n{0}",
        "error.image_too_large": "Image too large (Pillow safety limit exceeded):\n{0}",
        "error.image_not_found": "File not found:\n{0}",
        "error.image_permission": "Permission denied when reading:\n{0}",
        "error.image_io": "I/O error reading image: {0}",
        "error.video_cannot_open": "Cannot open video: {0}",
        "error.video_codec_missing": "Codec missing for {0}.\nInstall K-Lite Codec Pack.",
        "error.video_invalid_dimensions": "Invalid video dimensions",
        "error.video_cv2": "OpenCV error: {0}",
        "export_video_progress_frames": "Exporting video: {0}/{1} frames ({2}%)",
        "filetypes.images_video": "Images and Video",
        "filetypes.images": "Images",
        "filetypes.video": "Video",
        "filetypes.all": "All files",
        "preset.custom": "Custom",
        "preset.fullhd": "1920x1080 (Full HD 16:9)",
        "preset.hd": "1280x720 (HD 16:9)",
        "preset.4k": "3840x2160 (4K 16:9)",
        "preset.vertical": "1080x1920 (Full HD 9:16 Vertical)",
        "preset.square": "1080x1080 (Square 1:1)",
        "preset.banner": "1200x400 (Banner 3:1)",
        "preset.twitter": "1500x500 (Twitter Header 3:1)",
        "preset.facebook": "820x312 (Facebook Cover)",
        "preset.youtube": "1280x720 (YouTube Thumbnail)",
        "preset.instagram": "1080x608 (Instagram Landscape)",
        "preset.43a": "800x600 (4:3)",
        "preset.43b": "1024x768 (4:3)",
        "layer.default_name": "Image",
        "layer.copy_suffix": "_copy",
        # License gate
        "license.window_title": "License Activation — Live Video Composer",
        "license.activation_required": "A license is required to use this application",
        "license.checking": "Checking license...",
        "license.verifying_online": "Verifying online...",
        "license.enter_key": "Enter your license key:",
        "license.enter_key_hint": "Enter your license key to continue.",
        "license.activate_btn": "▶ Activate",
        "license.activating": "Activating...",
        "license.key_required": "Please enter your license key.",
        "license.invalid_key_format": "Invalid key format. Use: LIVE-XXXX-XXXX-XXXX-XXXX",
        "license.activation_failed": "Activation failed. Check your key and try again.",
        "license.network_error": "Cannot reach the server. Check your internet connection.",
        "license.offline_hint": "You can continue offline if the license was already active on this PC.",
        "license.verify_failed": "Verification failed. Please re-enter your key.",
        "license.pending_approval": "⏳ Waiting for admin approval...",
        "license.pending_hint": "Your activation is awaiting approval. It will be checked automatically every 30 seconds.",
        "license.unexpected_error": "Unexpected error. Please retry or contact support.",
        "license.deactivate_confirm_title": "Deactivate License",
        "license.deactivate_confirm": "Deactivate the license on this PC?\n\nThe key can then be used on another PC.",
    },
}

# Resolution presets: preset_id -> (width, height) or None for custom
RESOLUTION_PRESETS = {
    "custom": None,
    "fullhd": (1920, 1080),
    "hd": (1280, 720),
    "4k": (3840, 2160),
    "vertical": (1080, 1920),
    "square": (1080, 1080),
    "banner": (1200, 400),
    "twitter": (1500, 500),
    "facebook": (820, 312),
    "youtube": (1280, 720),
    "instagram": (1080, 608),
    "43a": (800, 600),
    "43b": (1024, 768),
}

PRESET_ORDER = ["fullhd", "hd", "4k", "vertical", "square", "banner", "twitter",
                "facebook", "youtube", "instagram", "43a", "43b", "custom"]


def _get_storage_path():
    """Return path for storing language preference."""
    if os.name == "nt":
        appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        base = Path(appdata) / "LiveVideoComposer"
    else:
        base = Path.home() / ".live-video-composer"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError:
        base = Path.home()
    return base / "lang.json"


def get_language():
    """Get current language (it or en)."""
    global _CURRENT_LANG
    return _CURRENT_LANG


def set_language(lang: str):
    """Set language and persist to storage."""
    global _CURRENT_LANG
    if lang in ("en", "it"):
        _CURRENT_LANG = lang
        try:
            path = _get_storage_path()
            path.write_text(json.dumps({"lang": lang}), encoding="utf-8")
        except OSError:
            pass


def init_language():
    """Load language from storage or use default (en for first launch)."""
    global _CURRENT_LANG
    try:
        path = _get_storage_path()
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("lang") in ("it", "en"):
                _CURRENT_LANG = data["lang"]
        # else: keep default "en" for first launch
    except (OSError, json.JSONDecodeError):
        pass


def t(key: str, *args) -> str:
    """Get translated string. Use {0}, {1} for placeholders."""
    lang = get_language()
    s = _TRANSLATIONS.get(lang, _TRANSLATIONS["it"]).get(key, key)
    if args:
        try:
            return s.format(*args)
        except (KeyError, ValueError):
            return s
    return s


def get_preset_values():
    """Return list of preset display names for current language."""
    return [t(f"preset.{pid}") for pid in PRESET_ORDER]


def preset_display_to_id(display: str) -> str:
    """Map display string to preset id."""
    for pid in PRESET_ORDER:
        if t(f"preset.{pid}") == display:
            return pid
    return "custom"


def preset_id_to_resolution(pid: str):
    """Get (w, h) or None for preset id."""
    return RESOLUTION_PRESETS.get(pid, RESOLUTION_PRESETS["custom"])
