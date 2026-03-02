import os
import psutil

# Common prefixes for well-known desktop environment processes/services
DE_SERVICE_PREFIXES = {
    'gnome': ['gnome-', 'mutter', 'gdm', 'evolution-'],
    'kde': ['plasma-', 'kwin', 'sddm', 'kdeconnect'],
    'hyprland': ['hyprland', 'waybar', 'swaybg', 'hyprpaper'],
    'xfce': ['xfce4-', 'xfwm4', 'xfdesktop'],
    'cinnamon': ['cinnamon', 'muffin', 'nemo'],
    'mate': ['mate-', 'marco', 'caja'],
}

def get_active_de() -> str:
    """
    Returns the name of the currently active Desktop Environment using standard agnostic environment variables.
    Falls back to 'unknown_or_tty' if completely headless.
    """
    xdg_current = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    if xdg_current:
        for de in DE_SERVICE_PREFIXES.keys():
            if de in xdg_current:
                return de
                
    desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
    if desktop_session:
        for de in DE_SERVICE_PREFIXES.keys():
            if de in desktop_session:
                return de
                
    return 'unknown_or_tty'

def is_de_service(unit_name: str, active_de: str) -> bool:
    """
    Checks if a given systemd unit or daemon is likely tied to the user's desktop session.
    It checks against both the current DE and other common DE prefixes to catch stragglers
    (e.g., someone running KDE apps in GNOME).
    """
    name_lower = unit_name.lower()
    
    # We always consider generic X11/Wayland/Polkit stuff as DE/User Session
    generic_session_prefixes = ['xdg-', 'dbus-', 'polkit-', 'pipewire', 'wireplumber', 'pulseaudio', 'at-spi']
    if any(name_lower.startswith(p) for p in generic_session_prefixes):
        return True
        
    for prefixes in DE_SERVICE_PREFIXES.values():
        if any(name_lower.startswith(p) for p in prefixes):
            return True
            
    return False
