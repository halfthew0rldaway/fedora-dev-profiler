import psutil
import logging
from fedora_dev_profiler.system.cache import cache
from fedora_dev_profiler.system.errors import ErrorData

logger = logging.getLogger(__name__)

def get_running_processes() -> list[dict]:
    """
    Returns a list of running processes with basic metadata.
    Avoids reading environment variables to prevent permission errors.
    """
    if cache.has('running_processes'):
        return cache.get('running_processes')
        
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        cache.set('running_processes', processes)
        return processes
    except Exception as e:
        logger.exception(f"Unexpected error in process_monitor: {e}")
        if not cache.has('system_errors'):
            cache.set('system_errors', [])
        cache.get('system_errors').append(ErrorData('Process Monitor', f"Failed to inspect processes: {str(e)}"))
        return processes

def is_process_running(executable_name: str) -> bool:
    """Check if any process matching the executable name is running."""
    for p in psutil.process_iter(['name']):
        try:
            if p.info['name'] == executable_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False
