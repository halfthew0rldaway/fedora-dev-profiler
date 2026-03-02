import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import threading

from fedora_dev_profiler.analysis.correlator import analyze_system
from fedora_dev_profiler.analysis.heuristics import evaluate_activity
from fedora_dev_profiler.ui.details_page import create_details_page

class OverviewPage(Adw.NavigationPage):
    def __init__(self, **kwargs):
        super().__init__(title="Overview", tag="overview", **kwargs)
        
        self.toolbar = Adw.ToolbarView()
        self.set_child(self.toolbar)
        
        header = Adw.HeaderBar()
        self.toolbar.add_top_bar(header)
        
        # Primary Menu Setup
        menu_builder = Gtk.Builder.new_from_string("""
        <interface>
          <menu id="primary-menu">
            <section>
              <item>
                <attribute name="label" translatable="yes">How Detection Works</attribute>
                <attribute name="action">app.how_it_works</attribute>
              </item>
              <item>
                <attribute name="label" translatable="yes">Export JSON Report</attribute>
                <attribute name="action">app.export</attribute>
              </item>
            </section>
            <section>
              <item>
                <attribute name="label" translatable="yes">_About</attribute>
                <attribute name="action">app.about</attribute>
              </item>
            </section>
          </menu>
        </interface>
        """, -1)
        
        menu_model = menu_builder.get_object("primary-menu")
        menu_button = Gtk.MenuButton()
        menu_button.set_menu_model(menu_model)
        menu_button.set_icon_name("open-menu-symbolic")
        header.pack_end(menu_button)
        
        title = Adw.WindowTitle(title="Dev Environment Profiler", subtitle="Read-only Observational Mode")
        header.set_title_widget(title)
        
        self.spinner = Gtk.Spinner(spinning=True, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        self.spinner.set_size_request(48, 48)
        self.toolbar.set_content(self.spinner)
        
        # Load data in background
        threading.Thread(target=self._load_data_thread, daemon=True).start()
        
    def _load_data_thread(self):
        profile = analyze_system()
        GLib.idle_add(self._on_data_loaded, profile)
        
    def _on_data_loaded(self, profiles):
        self.spinner.stop()
        
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        
        # 1. Primary Observation Banner
        banner = Adw.Banner(title="Observation Mode: No changes will be made to your system.")
        banner.set_revealed(True)
        self.toolbar.add_top_bar(banner)
        
        # 2. Error / Partial Data Banners
        if profiles.get('errors'):
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            for err in profiles['errors']:
                err_banner = Adw.Banner(title=f"Partial Data ({err.subsystem}): {err.message}")
                err_banner.set_revealed(True)
                # Keep it neutral: no red backgrounds.
                error_box.append(err_banner)
            self.toolbar.add_top_bar(error_box)
            
        if not profiles['dev_stacks'] and not profiles['system_daemons'] and not profiles['user_session_services']:
            empty = Adw.StatusPage(
                icon_name="system-search-symbolic",
                title="No Data Found",
                description="Could not detect any stacks or services."
            )
            box.append(empty)
        else:
            # -- TOP LEVEL SUMMARY --
            dev_stacks_total = len(profiles['dev_stacks'])
            active_count = 0
            dev_stacks_enriched = []
            
            for p in profiles['dev_stacks']:
                from fedora_dev_profiler.analysis.heuristics import evaluate_activity
                activity = evaluate_activity(p)
                dev_stacks_enriched.append((p, activity))
                if activity['status'] == 'Active':
                    active_count = active_count + 1
                    
            idle_count = dev_stacks_total - active_count
            total_daemons = len(profiles['system_daemons']) + len(profiles['user_session_services'])
            
            summary_group = Adw.PreferencesGroup(title="System Summary")
            box.append(summary_group)
            
            sum_row1 = Adw.ActionRow(title=f"{dev_stacks_total} Development Toolchains Detected", subtitle=f"{active_count} Active, {idle_count} Idle")
            sum_row1.add_prefix(Gtk.Image.new_from_icon_name("applications-development-symbolic"))
            summary_group.add(sum_row1)
            
            sum_row2 = Adw.ActionRow(title=f"{total_daemons} Background Services Observed", subtitle="Expected baseline for this system.")
            sum_row2.add_prefix(Gtk.Image.new_from_icon_name("system-run-symbolic"))
            summary_group.add(sum_row2)
            
            # 1. Dev Stacks
            if dev_stacks_enriched:
                group = Adw.PreferencesGroup(title="Development Toolchains", description="Installed development environments.")
                box.append(group)
                
                for p, activity in dev_stacks_enriched:
                    status_text = activity['status']
                    # Use the primary reason as the short explanatory subtitle
                    reason_sub = activity['reasons'][0] if activity['reasons'] else "Status observed."
                    
                    row = Adw.ActionRow(title=p['name'], subtitle=f"{status_text} — {reason_sub}")
                    row.set_activatable(True)
                    row.connect("activated", self._on_row_activated, p, activity)
                    
                    # Neutral symbolic icons only
                    icon_name = "media-playback-start-symbolic" if status_text == "Active" else "media-playback-pause-symbolic"
                    icon = Gtk.Image.new_from_icon_name(icon_name)
                    icon.set_margin_end(12)
                    row.add_prefix(icon)
                    
                    nav_icon = Gtk.Image.new_from_icon_name("go-next-symbolic")
                    row.add_suffix(nav_icon)
                    group.add(row)

            # 2. User / DE Services
            if profiles['user_session_services']:
                de_group = Adw.PreferencesGroup(
                    title="User Session Services", 
                    description="Background tasks associated with your desktop environment."
                )
                box.append(de_group)
                
                row = Adw.ActionRow(title=f"{len(profiles['user_session_services'])} Session Services")
                row.set_activatable(True)
                row.connect("activated", self._on_generic_row_activated, "User Session Services", profiles['user_session_services'])
                nav_icon = Gtk.Image.new_from_icon_name("go-next-symbolic")
                row.add_suffix(nav_icon)
                de_group.add(row)
                
            # 3. System Services
            if profiles['system_daemons']:
                sys_group = Adw.PreferencesGroup(
                    title="Core System Daemons", 
                    description="OS-level services required for core functions."
                )
                box.append(sys_group)
                
                row = Adw.ActionRow(title=f"{len(profiles['system_daemons'])} Core Daemons")
                row.set_activatable(True)
                row.connect("activated", self._on_generic_row_activated, "System Daemons", profiles['system_daemons'])
                nav_icon = Gtk.Image.new_from_icon_name("go-next-symbolic")
                row.add_suffix(nav_icon)
                sys_group.add(row)
                
        scroll.set_child(box)
        self.toolbar.set_content(scroll)

    def _on_row_activated(self, row, profile, activity):
        nav_view = self.get_parent()
        if nav_view:
            details_page = create_details_page(profile, activity)
            nav_view.push(details_page)
            
    def _on_generic_row_activated(self, row, title, units):
        nav_view = self.get_parent()
        if nav_view:
            from fedora_dev_profiler.ui.details_page import create_generic_list_page
            page = create_generic_list_page(title, units)
            nav_view.push(page)
