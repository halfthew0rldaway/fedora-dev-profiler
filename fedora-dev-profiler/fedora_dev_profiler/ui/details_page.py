import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from fedora_dev_profiler.analysis.heuristics import explain_stack

def create_details_page(profile: dict, activity: dict) -> Adw.NavigationPage:
    page = Adw.NavigationPage(title=profile['name'], tag=f"details_{profile['name']}")
    
    toolbar = Adw.ToolbarView()
    page.set_child(toolbar)
    
    header = Adw.HeaderBar()
    toolbar.add_top_bar(header)
    
    scroll = Gtk.ScrolledWindow()
    toolbar.set_content(scroll)
    
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    box.set_margin_top(24)
    box.set_margin_bottom(24)
    box.set_margin_start(24)
    box.set_margin_end(24)
    scroll.set_child(box)
    
    exps = explain_stack(profile)
    
    # 1. Plain-language summary
    summary_group = Adw.PreferencesGroup()
    box.append(summary_group)
    row = Adw.ActionRow(title=exps['summary'])
    row.set_title_lines(3)
    row.add_prefix(Gtk.Image.new_from_icon_name("dialog-information-symbolic"))
    summary_group.add(row)
        
    # 2. Why it is detected
    detected_group = Adw.PreferencesGroup(title="Why is this detected?")
    box.append(detected_group)
    row = Adw.ActionRow(title=exps['why_detected'])
    row.set_title_lines(4)
    detected_group.add(row)
    
    # 3. Why it is classified active/idle
    activity_group = Adw.PreferencesGroup(title=f"Activity Classification: {activity['status']}")
    box.append(activity_group)
    for reason in activity['reasons']:
        row = Adw.ActionRow(title=reason)
        activity_group.add(row)
        
    # 4. Related Packages
    if profile['packages']:
        pkg_group = Adw.PreferencesGroup(title="Related RPM Packages", description="Read-only view of installed files.")
        box.append(pkg_group)
        for pkg in profile['packages'][:10]:
            row = Adw.ActionRow(title=pkg)
            pkg_group.add(row)
        if len(profile['packages']) > 10:
            row = Adw.ActionRow(title=f"... and {len(profile['packages']) - 10} more.")
            pkg_group.add(row)
            
    # 5. Related Services / Processes
    if profile['processes'] or profile['systemd_system'] or profile['systemd_user']:
        svc_group = Adw.PreferencesGroup(title="Associated Background Processes", description="Daemons or active processes managed by this stack.")
        box.append(svc_group)
        for proc in profile['processes']:
            cmd = " ".join(proc.get('cmdline', [])) or proc.get('exe', proc['name'])
            row = Adw.ActionRow(title=proc['name'], subtitle=cmd)
            row.set_subtitle_lines(2)
            svc_group.add(row)
        for unit in profile['systemd_system'] + profile['systemd_user']:
            row = Adw.ActionRow(title=unit['unit'], subtitle=f"{unit['description']} (Active: {unit['active_state']})")
            svc_group.add(row)

    return page

def create_generic_list_page(title: str, units: list) -> Adw.NavigationPage:
    from fedora_dev_profiler.analysis.heuristics import explain_de_service, explain_system_service
    page = Adw.NavigationPage(title=title, tag=f"generic_{title}")
    
    toolbar = Adw.ToolbarView()
    page.set_child(toolbar)
    
    header = Adw.HeaderBar()
    toolbar.add_top_bar(header)
    
    scroll = Gtk.ScrolledWindow()
    toolbar.set_content(scroll)
    
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    box.set_margin_top(24)
    box.set_margin_bottom(24)
    box.set_margin_start(24)
    box.set_margin_end(24)
    scroll.set_child(box)
    
    # Explanation
    banner_group = Adw.PreferencesGroup()
    box.append(banner_group)
    
    explanation = explain_system_service() if "System" in title else explain_de_service()
    row = Adw.ActionRow(title=explanation)
    row.set_title_lines(4)
    banner_group.add(row)
    
    # Units list
    unit_group = Adw.PreferencesGroup(title=f"{len(units)} Units")
    box.append(unit_group)
    
    for u in units:
        row = Adw.ActionRow(title=u['unit'], subtitle=u['description'])
        unit_group.add(row)
        
    return page
