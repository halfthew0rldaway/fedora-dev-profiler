import os
from gi.repository import GLib

APP_ID = "org.fedoraproject.DevProfiler"

def get_cache_dir() -> str:
    """Return the XDG cache path for the application."""
    path = os.path.join(GLib.get_user_cache_dir(), APP_ID)
    os.makedirs(path, exist_ok=True)
    return path

def get_config_dir() -> str:
    """Return the XDG config path for the application."""
    path = os.path.join(GLib.get_user_config_dir(), APP_ID)
    os.makedirs(path, exist_ok=True)
    return path

def get_data_dir() -> str:
    """Return the XDG data path for the application."""
    path = os.path.join(GLib.get_user_data_dir(), APP_ID)
    os.makedirs(path, exist_ok=True)
    return path
