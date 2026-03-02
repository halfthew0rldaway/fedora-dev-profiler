import subprocess
import json
import logging
from fedora_dev_profiler.system.cache import cache
from fedora_dev_profiler.system.errors import ErrorData

logger = logging.getLogger(__name__)

def get_installed_packages() -> list[str]:
    """
    Returns a list of all installed RPM packages using native tools.
    Fully read-only.
    """
    if cache.has('rpm_packages'):
        return cache.get('rpm_packages')
        
    try:
        # Fast query of all package names without formatting fluff
        result = subprocess.run(
            ['rpm', '-qa', '--qf', '%{NAME}\n'],
            capture_output=True,
            text=True,
            check=True
        )
        # Split lines and remove empty strings
        packages = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        cache.set('rpm_packages', packages)
        return packages
    except subprocess.CalledProcessError as e:
        logger.error(f"RPM query failed: {e.stderr}")
        if not cache.has('system_errors'):
            cache.set('system_errors', [])
        cache.get('system_errors').append(ErrorData('RPM Database', f"Failed to list packages: {e.stderr}"))
        return []
    except FileNotFoundError:
        logger.error("RPM command not found. Is this a Fedora system?")
        if not cache.has('system_errors'):
            cache.set('system_errors', [])
        cache.get('system_errors').append(ErrorData('RPM Database', "RPM command not found on host."))
        return []

def query_package_info(package_name: str) -> dict | None:
    """
    Query basic informational metadata about an installed package.
    Using `rpm -qi` to avoid DNF caches or downloading metadata.
    """
    try:
        cmd = ["rpm", "-qi", package_name]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = {}
        for line in result.stdout.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                info[key.strip()] = val.strip()
        return info
    except subprocess.CalledProcessError:
        return None
