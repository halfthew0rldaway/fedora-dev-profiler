import gi
import gettext

# Setup basic i18n hooks
gettext.bindtextdomain('fedora-dev-profiler', '/usr/share/locale')
gettext.textdomain('fedora-dev-profiler')
_ = gettext.gettext

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from fedora_dev_profiler.ui.overview_page import OverviewPage

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("Fedora Development Status"))
        
        # Responsive sizing for tiling WMs
        self.set_default_size(800, 600)
        self.set_size_request(360, 400) # Minimum viable width/height
        
        self.nav_view = Adw.NavigationView()
        self.set_content(self.nav_view)
        
        # Load the overview page
        self.overview_page = OverviewPage()
        self.nav_view.push(self.overview_page)
