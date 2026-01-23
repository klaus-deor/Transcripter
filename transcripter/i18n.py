"""Internationalization support for Transcripter."""

import locale
import os
from typing import Dict, Optional

# Translation dictionaries
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Tray menu
        "start_recording": "Start Recording",
        "stop_recording": "Stop Recording",
        "settings": "Settings",
        "history": "History",
        "about": "About",
        "quit": "Quit",
        "status_idle": "Idle",
        "status_recording": "Recording...",
        "status_transcribing": "Transcribing...",

        # Settings window
        "settings_title": "Deor Transcripter Settings",
        "provider": "Provider",
        "api_key": "API Key",
        "save": "Save",
        "cancel": "Cancel",
        "language": "Language",
        "hotkey": "Hotkey",
        "audio_device": "Audio Device",
        "general": "General",
        "providers": "Providers",
        "audio": "Audio",
        "hotkeys": "Hotkeys",
        "show_notifications": "Show notifications",
        "auto_copy": "Auto copy to clipboard",
        "fallback_provider": "Fallback Provider",
        "none": "None",

        # History window
        "history_title": "Transcription History",
        "copy": "Copy",
        "delete": "Delete",
        "clear_all": "Clear All",
        "no_history": "No transcription history",

        # Notifications
        "recording_started": "Recording started",
        "recording_stopped": "Recording stopped",
        "transcription_complete": "Transcription complete",
        "copied_to_clipboard": "Copied to clipboard",
        "error": "Error",

        # Wayland warning
        "wayland_detected": "Wayland detected!",
        "wayland_warning": "Global hotkeys are blocked by Wayland. Use the tray menu or configure a system shortcut.",

        # Errors
        "no_api_key": "No API key configured",
        "transcription_failed": "Transcription failed",
        "recording_failed": "Recording failed",

        # Settings labels
        "ui_language": "Interface Language",
        "transcription_language": "Transcription Language",
        "auto_detect": "Auto-detect",
        "microphone": "Microphone",
        "system_default": "System Default",
        "start_on_login": "Start on system login",
        "max_history_items": "Maximum history items",
        "enable_history": "Enable history",
        "toggle_mode": "Toggle mode (same key to start/stop)",
        "wayland_warning_settings": "On Wayland, configure shortcut in System Settings > Keyboard",
    },

    "pt": {
        # Menu da bandeja
        "start_recording": "Iniciar Gravação",
        "stop_recording": "Parar Gravação",
        "settings": "Configurações",
        "history": "Histórico",
        "about": "Sobre",
        "quit": "Sair",
        "status_idle": "Aguardando",
        "status_recording": "Gravando...",
        "status_transcribing": "Transcrevendo...",

        # Janela de configurações
        "settings_title": "Configurações - Deor Transcripter",
        "provider": "Provedor",
        "api_key": "Chave API",
        "save": "Salvar",
        "cancel": "Cancelar",
        "language": "Idioma",
        "hotkey": "Atalho",
        "audio_device": "Dispositivo de Áudio",
        "general": "Geral",
        "providers": "Provedores",
        "audio": "Áudio",
        "hotkeys": "Atalhos",
        "show_notifications": "Mostrar notificações",
        "auto_copy": "Copiar automaticamente",
        "fallback_provider": "Provedor Reserva",
        "none": "Nenhum",

        # Janela de histórico
        "history_title": "Histórico de Transcrições",
        "copy": "Copiar",
        "delete": "Excluir",
        "clear_all": "Limpar Tudo",
        "no_history": "Nenhum histórico de transcrição",

        # Notificações
        "recording_started": "Gravação iniciada",
        "recording_stopped": "Gravação parada",
        "transcription_complete": "Transcrição completa",
        "copied_to_clipboard": "Copiado para a área de transferência",
        "error": "Erro",

        # Aviso Wayland
        "wayland_detected": "Wayland detectado!",
        "wayland_warning": "Atalhos globais são bloqueados pelo Wayland. Use o menu da bandeja ou configure um atalho no sistema.",

        # Erros
        "no_api_key": "Nenhuma chave API configurada",
        "transcription_failed": "Falha na transcrição",
        "recording_failed": "Falha na gravação",

        # Labels de configurações
        "ui_language": "Idioma da Interface",
        "transcription_language": "Idioma da Transcrição",
        "auto_detect": "Detectar automaticamente",
        "microphone": "Microfone",
        "system_default": "Padrão do Sistema",
        "start_on_login": "Iniciar com o sistema",
        "max_history_items": "Máximo de itens no histórico",
        "enable_history": "Habilitar histórico",
        "toggle_mode": "Modo alternar (mesma tecla para iniciar/parar)",
        "wayland_warning_settings": "No Wayland, configure o atalho em Configurações > Teclado",
    },

    "es": {
        # Menú de bandeja
        "start_recording": "Iniciar Grabación",
        "stop_recording": "Detener Grabación",
        "settings": "Configuración",
        "history": "Historial",
        "about": "Acerca de",
        "quit": "Salir",
        "status_idle": "Inactivo",
        "status_recording": "Grabando...",
        "status_transcribing": "Transcribiendo...",

        # Ventana de configuración
        "settings_title": "Configuración - Deor Transcripter",
        "provider": "Proveedor",
        "api_key": "Clave API",
        "save": "Guardar",
        "cancel": "Cancelar",
        "language": "Idioma",
        "hotkey": "Atajo",
        "audio_device": "Dispositivo de Audio",
        "general": "General",
        "providers": "Proveedores",
        "audio": "Audio",
        "hotkeys": "Atajos",
        "show_notifications": "Mostrar notificaciones",
        "auto_copy": "Copiar automáticamente",
        "fallback_provider": "Proveedor de Respaldo",
        "none": "Ninguno",

        # Ventana de historial
        "history_title": "Historial de Transcripciones",
        "copy": "Copiar",
        "delete": "Eliminar",
        "clear_all": "Limpiar Todo",
        "no_history": "Sin historial de transcripción",

        # Notificaciones
        "recording_started": "Grabación iniciada",
        "recording_stopped": "Grabación detenida",
        "transcription_complete": "Transcripción completa",
        "copied_to_clipboard": "Copiado al portapapeles",
        "error": "Error",

        # Aviso Wayland
        "wayland_detected": "¡Wayland detectado!",
        "wayland_warning": "Los atajos globales están bloqueados por Wayland. Use el menú de la bandeja o configure un atajo del sistema.",

        # Errores
        "no_api_key": "No hay clave API configurada",
        "transcription_failed": "Falló la transcripción",
        "recording_failed": "Falló la grabación",

        # Etiquetas de configuración
        "ui_language": "Idioma de la Interfaz",
        "transcription_language": "Idioma de Transcripción",
        "auto_detect": "Detectar automáticamente",
        "microphone": "Micrófono",
        "system_default": "Predeterminado del Sistema",
        "start_on_login": "Iniciar con el sistema",
        "max_history_items": "Máximo de elementos en historial",
        "enable_history": "Habilitar historial",
        "toggle_mode": "Modo alternar (misma tecla para iniciar/parar)",
        "wayland_warning_settings": "En Wayland, configure el atajo en Configuración > Teclado",
    },
}

# Current language
_current_lang: str = "en"


def detect_system_language() -> str:
    """Detect the system language."""
    try:
        # Try to get from environment
        lang = os.environ.get('LANG', '') or os.environ.get('LANGUAGE', '')
        if lang:
            lang = lang.split('.')[0].split('_')[0].lower()
            if lang in TRANSLATIONS:
                return lang

        # Try locale
        lang = locale.getdefaultlocale()[0]
        if lang:
            lang = lang.split('_')[0].lower()
            if lang in TRANSLATIONS:
                return lang
    except Exception:
        pass

    return "en"


def set_language(lang: str) -> None:
    """Set the current language."""
    global _current_lang
    if lang in TRANSLATIONS:
        _current_lang = lang
    else:
        _current_lang = "en"


def get_language() -> str:
    """Get the current language."""
    return _current_lang


def get_available_languages() -> Dict[str, str]:
    """Get available languages with their display names."""
    return {
        "en": "English",
        "pt": "Português",
        "es": "Español",
    }


def t(key: str) -> str:
    """Get translated string for key."""
    translations = TRANSLATIONS.get(_current_lang, TRANSLATIONS["en"])
    return translations.get(key, TRANSLATIONS["en"].get(key, key))


# Initialize with system language
set_language(detect_system_language())
