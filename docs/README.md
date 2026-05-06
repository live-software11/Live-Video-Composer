# Documentazione - Live Video Composer

> **Indice canonico** della documentazione tecnica e di prodotto.
> **Ultima revisione:** 6 maggio 2026.
>
> Il vecchio `docs/README.md` (documento di vendita IT/EN) e' stato rinominato `docs/PRODOTTO_VENDITA.md` con `git mv` (history preservata).

---

## Ripresa veloce

1. **[`../AGENTS.md`](../AGENTS.md)** - Entry-point standard 2026 per Cursor / Codex / Continue. **Prima fonte** per agenti automatici.
2. **[`../CLAUDE.md`](../CLAUDE.md)** - Sintesi viva per Claude Desktop / Code (gemello di `AGENTS.md`).
3. **[`ARCHITETTURA_Live_Video_Composer.md`](./ARCHITETTURA_Live_Video_Composer.md)** - Architettura completa: stack, data model, rendering, export, build, changelog. **Single source of truth tecnico.**
4. **[`PRODOTTO_VENDITA.md`](./PRODOTTO_VENDITA.md)** - Documento di vendita IT/EN (descrizione marketing).
5. **[`../README.md`](../README.md)** - README repository (overview).

---

## Documentazione tecnica

| File | Contenuto | Quando aggiornarlo |
| --- | --- | --- |
| [`ARCHITETTURA_Live_Video_Composer.md`](./ARCHITETTURA_Live_Video_Composer.md) | Stack Python, data model `ImageLayer`, rendering compositing, export immagine/video, drag&drop, build dual-spec PyInstaller, changelog | Ogni modifica strutturale |
| [`BugFix_Refactor_Implementazioni_Live_Video_Composer.md`](./BugFix_Refactor_Implementazioni_Live_Video_Composer.md) | Tracciamento bug, refactor, implementazioni future | Ogni bug fix / refactor / nuova feature |
| [`GUIDA_INTEGRAZIONE_LICENZA_APP.md`](./GUIDA_INTEGRAZIONE_LICENZA_APP.md) | Integrazione client API LiveWorks (endpoint, fingerprint, T-04 HMAC runtime env var) | Ogni cambio contratto API |

## Audit e sign-off

| File | Tipo | Esito |
| --- | --- | --- |
| [`AUDIT_PRE_VENDITA.md`](./AUDIT_PRE_VENDITA.md) | Audit pre-vendita (security, stabilita) | **VERDE - pronto per la vendita** (Aprile 2026, **zero superficie attacco rete**) |
| [`TASK_BATCH_2026-04-15.md`](./TASK_BATCH_2026-04-15.md) | Task batch storico (runtime guard 3.10, thread safety export, build hardening) | Eseguito 15/04/2026 |

## Documentazione utente / vendita

| File | Lingua | Note |
| --- | --- | --- |
| [`PRODOTTO_VENDITA.md`](./PRODOTTO_VENDITA.md) | IT + EN | Documento di vendita / marketing (ex `docs/README.md`, rinominato 06/05/2026) |

## AI assistant

| File | Destinatario | Ruolo |
| --- | --- | --- |
| [`../AGENTS.md`](../AGENTS.md) | Cursor / Codex / Continue | **Entry-point standard 2026** (prima fonte) |
| [`../CLAUDE.md`](../CLAUDE.md) | Claude Desktop / Code | Sintesi viva (gemello AGENTS) |
| [`Istruzioni_Progetto_Claude_Live_Video_Composer.md`](./Istruzioni_Progetto_Claude_Live_Video_Composer.md) | Claude Desktop (architetto) | System prompt - **legacy**, ancora valido per chat profonde |
| [`Primo_Prompt_Avvio_Chat_Claude_Desktop_Live_Video_Composer.md`](./Primo_Prompt_Avvio_Chat_Claude_Desktop_Live_Video_Composer.md) | Claude Desktop (architetto) | Primo prompt avvio chat - **legacy** |

> **Precedenza:** `AGENTS.md` > `ARCHITETTURA_Live_Video_Composer.md` > `CLAUDE.md` > legacy.

## Configurazione AI / MCP

- **Cursor rules modulari** in [`../.cursor/rules/`](../.cursor/rules/) - 10 file `.mdc`:
  - `project.mdc`, `main-py.mdc`, `build.mdc`
  - `installer-modern.mdc`, `i18n-installer.mdc`
  - `ecosystem-context.mdc`, `doc-sync.mdc`
  - `git-autonomy.mdc`, `github-account-live-software11.mdc`
  - `cli.json`
- **Claude Code config** in [`../.claude/`](../.claude/).

---

## Storia overhaul docs

| Data | Cosa |
| --- | --- |
| **6 maggio 2026** | Audit completo: creati `AGENTS.md` + `CLAUDE.md` + questo indice. Vecchio `docs/README.md` (documento vendita IT/EN) rinominato `docs/PRODOTTO_VENDITA.md` via `git mv` (history preservata). Aggiornata ARCHITETTURA a v1.5.0 con changelog audit pre-vendita + T-04 HMAC. Cursor rules `ecosystem-context`, `doc-sync` aggiornate. |
| 24/04/2026 | T-04 LiveWorks App Challenge HMAC: runtime env var `LIVEWORKS_APP_CHALLENGE_SECRET`. |
| 15/04/2026 | TASK BATCH: runtime guard Python 3.10+, thread safety export con snapshot, log rotation, build hardening (cd /d %~dp0). |
| 14/04/2026 | Sistema licenze LiveWorks integrato; PyInstaller dual build; Inno Setup upgrade. |
| Aprile 2026 | Audit pre-vendita chiuso (VERDE): DnD thread safety, fingerprint strict, pending cifrato Fernet. |
| 18/03/2026 | Versione 1.4.1: stack Pillow 12.1.1 / OpenCV 4.13. |

---

> **Regola d'oro:** la documentazione e' parte del codice. Ogni modifica significativa al codebase richiede aggiornamento del file canonico corrispondente nello stesso commit (regola `.cursor/rules/doc-sync.mdc`).
