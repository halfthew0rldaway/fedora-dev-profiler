import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio, GLib, Gtk, Adw

class ProfilerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='org.fedoraproject.DevProfiler',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
    def do_startup(self):
        Adw.Application.do_startup(self)
        
        # Setup App Actions mapping to the GTK primary menu
        action_about = Gio.SimpleAction.new("about", None)
        action_about.connect("activate", self.on_about_action)
        self.add_action(action_about)
        
        action_export = Gio.SimpleAction.new("export", None)
        action_export.connect("activate", self.on_export_action)
        self.add_action(action_export)

        action_how = Gio.SimpleAction.new("how_it_works", None)
        action_how.connect("activate", self.on_how_it_works_action)
        self.add_action(action_how)
        
    def do_activate(self):
        # We only import the window when activating to avoid loading GTK UI during testing
        from fedora_dev_profiler.ui.main_window import MainWindow
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()
        
    def on_about_action(self, action, param):
        about = Adw.AboutWindow(
            application=self,
            application_icon='fedora-dev-profiler',
            application_name='Fedora Dev Profiler',
            developer_name='Fedora User',
            version='0.1.0',
            website='https://github.com/example/fedora-dev-profiler',
            issue_url='https://github.com/example/fedora-dev-profiler/issues',
        )
        about.present()
        
    def on_export_action(self, action, param):
        from fedora_dev_profiler.analysis.correlator import generate_json_export
        from gi.repository import Gtk
        
        json_dump = generate_json_export()
        
        dialog = Gtk.MessageDialog(
            transient_for=self.props.active_window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="JSON Export Generated",
        )
        dialog.format_secondary_text("The following JSON contains a safe, deterministic read-only dump of your current system profile.")
        
        text_view = Gtk.TextView()
        text_view.get_buffer().set_text(json_dump)
        text_view.set_editable(False)
        text_view.set_monospace(True)
        text_view.set_top_margin(12)
        text_view.set_bottom_margin(12)
        text_view.set_left_margin(12)
        text_view.set_right_margin(12)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(400)
        scroll.set_child(text_view)
        
        dialog.get_content_area().append(scroll)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()
        
    def on_how_it_works_action(self, action, param):
        dialog = Gtk.MessageDialog(
            transient_for=self.props.active_window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="How Detection Works",
        )
        details = (
            "This application uses native Linux and Fedora utilities to observe "
            "your system state without making any modifications.\n\n"
            "• Signals Observed: Systemd units via D-Bus, process paths via standard memory, "
            "package metadata via RPM, and standard filesystem access times.\n\n"
            "• Heuristics: Classifications such as 'Active' or 'Idle' are heuristic-based, "
            "inferred by checking if tools have been accessed within the past 30 days or "
            "if related background daemons are running.\n\n"
            "• Results may vary depending on your unique usage patterns and desktop environment."
        )
        dialog.format_secondary_text(details)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()

def main():
    app = ProfilerApp()
    return app.run(sys.argv)
