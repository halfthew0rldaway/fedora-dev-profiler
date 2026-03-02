from fedora_dev_profiler.system.stack_detector import detect_stacks
from fedora_dev_profiler.system.systemd_client import get_systemd_units, get_user_units
from fedora_dev_profiler.system.process_monitor import get_running_processes
from fedora_dev_profiler.system.package_mgr import get_installed_packages
from fedora_dev_profiler.system.de_detector import get_active_de, is_de_service

# Typical systemd service prefixes for stacks
STACK_SERVICES = {
    'Docker/Podman': ['docker', 'podman', 'containerd'],
    'Node.js': [],
    'Python': [],
    'Java': [],
    'Rust': [],
    'Go': []
}

# Typical RPM package prefixes for stacks
STACK_PACKAGES = {
    'Python': ['python3', 'python3-pip', 'poetry'],
    'Node.js': ['nodejs', 'npm', 'yarn'],
    'Java': ['java-', 'maven', 'gradle'],
    'Rust': ['rust', 'cargo'],
    'Go': ['golang'],
    'Docker/Podman': ['docker', 'podman', 'containerd']
}

def analyze_system() -> dict[str, list]:
    """
    Correlates raw system data into stack profiles and strictly separates DE/OS services.
    Returns:
       {
           'dev_stacks': [...list of stack profiles...],
           'system_daemons': [...list of OS level units...],
           'user_session_services': [...list of DE specific units...]
       }
    """
    stacks = detect_stacks()
    sys_units = get_systemd_units()
    user_units = get_user_units()
    processes = get_running_processes()
    packages = get_installed_packages()
    
    active_de = get_active_de()
    dev_profiles = []
    
    # 1. Dev Stacks
    for stack_name, details in stacks.items():
        if not details['installed']:
            continue
            
        srv_prefixes = STACK_SERVICES.get(stack_name, [])
        related_sys_units = [u for u in sys_units if any(u['unit'].startswith(p) for p in srv_prefixes)]
        related_user_units = [u for u in user_units if any(u['unit'].startswith(p) for p in srv_prefixes)]
        
        binaries = [b['binary'] for b in details['binaries']]
        related_procs = []
        for p in processes:
            if p['name'] in binaries or any(b in (p.get('exe') or '') for b in binaries):
                related_procs.append(p)
                
        pkg_prefixes = STACK_PACKAGES.get(stack_name, [])
        related_pkgs = [pkg for pkg in packages if any(pkg.startswith(p) for p in pkg_prefixes)]
        
        dev_profiles.append({
            'name': stack_name,
            'binaries': details['binaries'],
            'systemd_system': related_sys_units,
            'systemd_user': related_user_units,
            'processes': related_procs,
            'packages': related_pkgs
        })
        
    # 2. System vs User/DE Separation
    # We collect any active system/user units that ARE NOT part of a dev stack
    all_dev_units = set()
    for profile in dev_profiles:
        all_dev_units.update([u['unit'] for u in profile['systemd_system']])
        all_dev_units.update([u['unit'] for u in profile['systemd_user']])
        
    system_daemons = []
    for u in sys_units:
        if u['unit'] not in all_dev_units and u['active_state'] == 'active':
            # Is it deeply tied to a DE despite being a system service? (e.g. gdm, sddm)
            if not is_de_service(u['unit'], active_de):
                system_daemons.append(u)
                
    user_session_services = []
    # Both active DE services from userspace AND system space belong here
    for u in user_units:
        if u['unit'] not in all_dev_units and u['active_state'] == 'active':
            if is_de_service(u['unit'], active_de):
                user_session_services.append(u)
                
    from fedora_dev_profiler.system.cache import cache
    
    return {
        'dev_stacks': dev_profiles,
        'system_daemons': system_daemons,
        'user_session_services': user_session_services,
        'errors': cache.get('system_errors') or []
    }

def generate_json_export() -> str:
    """Generate a clean, deterministic JSON dump of the current session cache."""
    import json
    from fedora_dev_profiler.system.cache import cache
    from fedora_dev_profiler.analysis.heuristics import evaluate_activity
    
    # We must run analyze_system at least once first to populate caches.
    profiles = analyze_system()
    
    # Clean up the output so it's readable
    export_data = {
        'metadata': {
            'disclaimer': 'Fedora Development Environment Profiler - Read-Only Diagnostic',
            'version': '0.1.0'
        },
        'errors': [{'subsystem': e.subsystem, 'message': e.message} for e in profiles['errors']],
        'dev_stacks': [],
        'system_daemons': [s['unit'] for s in profiles['system_daemons']],
        'user_session_services': [s['unit'] for s in profiles['user_session_services']]
    }
    
    for stack in profiles['dev_stacks']:
        status = evaluate_activity(stack)
        export_data['dev_stacks'].append({
            'name': stack['name'],
            'status': status['status'],
            'heuristics': status['reasons'],
            'installed_packages': len(stack['packages']),
            'associated_daemons': [s['unit'] for s in stack['systemd_system'] + stack['systemd_user']],
            'running_processes': [p['name'] for p in stack['processes']]
        })
        
    return json.dumps(export_data, indent=2)
