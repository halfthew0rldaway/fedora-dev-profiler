import os
import time

def evaluate_activity(stack_profile: dict) -> dict:
    """
    Evaluate if a stack is active or inactive based on heuristics (running processes,
    services, and recent file access). Returns neutral phrasing.
    """
    is_active = False
    reasons = []
    
    # 1. Check running processes
    if stack_profile['processes']:
        is_active = True
        reasons.append("Active background processes observed.")
        
    # 2. Check active systemd services
    active_sys_units = [u for u in stack_profile['systemd_system'] if u.get('active_state') == 'active']
    active_user_units = [u for u in stack_profile['systemd_user'] if u.get('active_state') == 'active']
    
    if active_sys_units or active_user_units:
        is_active = True
        reasons.append("Running system or user services associated with this stack detected.")
        
    # 3. Check access time of main binaries (heuristic: 30 days for beginner neutrality)
    recent_access = False
    now = time.time()
    for b in stack_profile['binaries']:
        try:
            stat = os.stat(b['path'])
            if (now - stat.st_atime) < (30 * 24 * 3600):
                recent_access = True
                reasons.append("Tools in this stack were executed or accessed recently (within 30 days).")
                break
        except OSError:
            pass
            
    if recent_access:
        is_active = True

    if not is_active:
        reasons.append("No recent activity or running background services detected.")
        
    return {
        'status': 'Active' if is_active else 'Idle',
        'reasons': reasons
    }

def explain_stack(stack_profile: dict) -> dict:
    """
    Provide neutral explanations broken out for the 5-part layout.
    Returns: { summary, why_detected, why_active }
    """
    name = stack_profile['name']
    
    summary = f"The {name} development toolchain is installed on this system."
    
    why_detected = f"Found associated files installed on the system (e.g., binaries in standard system paths like /usr/bin or /usr/local/bin)."
    if stack_profile['packages']:
        why_detected += f" This is managed by {len(stack_profile['packages'])} installed RPM packages."
        
    return {
        'summary': summary,
        'why_detected': why_detected
    }

def explain_de_service() -> str:
    """Provides a desktop-agnostic, reassuring explanation for User Session Services."""
    return "These background services support your current desktop experience (like GNOME, KDE, or Wayland) and handle tasks like audio or session management. Their presence is completely normal and expected."

def explain_system_service() -> str:
    """Provides a reassuring explanation for core OS System Services."""
    return "These are essential, OS-level background services responsible for networking, hardware, and security. The amount shown here represents the expected baseline for a modern Fedora Workstation."
