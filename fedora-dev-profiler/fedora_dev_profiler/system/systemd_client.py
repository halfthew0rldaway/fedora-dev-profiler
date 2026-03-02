import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

import logging
from fedora_dev_profiler.system.cache import cache
from fedora_dev_profiler.system.errors import ErrorData

logger = logging.getLogger(__name__)

def _get_units(connection: Gio.DBusConnection, bus_name: str, object_path: str) -> list[dict]:
    try:
        proxy = Gio.DBusProxy.new_sync(
            connection,
            Gio.DBusProxyFlags.NONE,
            None,
            bus_name,
            object_path,
            "org.freedesktop.systemd1.Manager",
            None
        )
        # ListUnits returns an array of tuples. We only want systemd structures
        # Structure: (string id, string description, string load_state, string active_state, string sub_state, ...)
        units_variant = proxy.call_sync(
            "ListUnits",
            None,
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )
        
        result = []
        if units_variant:
            # Unpack the tuple containing the array
            units_array = units_variant.unpack()[0]
            for unit in units_array:
                # unit is a tuple
                result.append({
                    'unit': unit[0],
                    'description': unit[1],
                    'load_state': unit[2],
                    'active_state': unit[3],
                    'sub_state': unit[4]
                })
        return result
    except GLib.Error as e:
        logger.error(f"D-Bus error accessing systemd: {e.message}")
        if not cache.has('system_errors'):
            cache.set('system_errors', [])
        cache.get('system_errors').append(ErrorData('Systemd DBus', f"Failed to query units: {e.message}"))
        return []
    except Exception as e:
        logger.exception(f"Unexpected error in systemd_client: {e}")
        return []

def get_systemd_units() -> list[dict]:
    """Retrieve all loaded units from the system instance."""
    if cache.has('systemd_system_units'):
        return cache.get('systemd_system_units')
        
    try:
        bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        units = _get_units(bus, "org.freedesktop.systemd1", "/org/freedesktop/systemd1")
        cache.set('systemd_system_units', units)
        return units
    except Exception as e:
        logger.error(f"Failed to get SYSTEM bus: {e}")
        return []

def get_user_units() -> list[dict]:
    """Retrieve all loaded units from the user instance."""
    if cache.has('systemd_user_units'):
        return cache.get('systemd_user_units')
        
    try:
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        units = _get_units(bus, "org.freedesktop.systemd1", "/org/freedesktop/systemd1")
        cache.set('systemd_user_units', units)
        return units
    except Exception as e:
        logger.error(f"Failed to get SESSION bus: {e}")
        return []

