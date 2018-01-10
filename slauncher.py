import applications
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


global_apps = applications.list()


class AppButton(Gtk.Button):
    def __init__(self, app):
        super().__init__(label=app.name)

        self.app = app

        self.connect('notify::is-focus', self.on_is_focus)
        self.connect('clicked', self.on_clicked)

    def set_selected(self, is_selected):
        style = Gtk.STYLE_CLASS_SUGGESTED_ACTION
        has_style = self.get_style_context().has_class(style)

        if is_selected and not has_style:
            self.get_style_context().add_class(style)
        elif not is_selected and has_style:
            self.get_style_context().remove_class(style)

    def on_is_focus(self, button, x):
        if self.is_focus():
            app_bar = self.get_parent()
            app_bar.selected = self.app
            app_bar.refresh_selected()

    def on_clicked(self, button):
        self.run()

    def run(self):
        self.app.run()
        Gtk.main_quit()


class AppBar(Gtk.Box):
    selected = None

    def __init__(self, search):
        super().__init__()

        query = search.get_text().lower()
        apps = global_apps
        apps = list(filter(lambda a: query in a.name.lower(), apps))
        self.apps = apps
        self.search = search

        if self.apps:
            self.selected = self.apps[0]

        self.get_style_context().add_class(Gtk.STYLE_CLASS_LINKED)

        for app in self.apps:
            self.add(AppButton(app))

        self.refresh_selected()

        self.connect('focus', self.on_focus)

        self.show_all()

    def get_selected_button(self):
        for button in self.get_children():
            if button.app == self.selected:
                return button
        return None

    def refresh_selected(self):
        for button in self.get_children():
            button.set_selected(False)
        selected_button = self.get_selected_button()
        if selected_button:
            selected_button.set_selected(True)

    def on_focus(self, box, x):
        if self.search.is_focus():
            selected_button = self.get_selected_button()
            if selected_button:
                selected_button.grab_focus()
            return True
        return False

    def run(self):
        selected_button = self.get_selected_button()
        if selected_button:
            selected_button.run()


class Window(Gtk.Window):
    app_bar = None

    def __init__(self):
        super().__init__()

        self.set_title('SLauncher')

        self.search = Gtk.SearchEntry()
        self.search.connect('changed', self.on_search_changed)
        self.search.connect('activate', self.on_search_activate)

        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
            margin=6
        )
        self.box.add(self.search)
        self.add(self.box)

        self.refresh_app_bar()

        self.show_all()

    def on_search_changed(self, search):
        self.refresh_app_bar()

    def refresh_app_bar(self):
        if (self.app_bar):
            self.box.remove(self.app_bar)
            self.app_bar.destroy()

        self.app_bar = AppBar(self.search)
        self.box.add(self.app_bar)

    def on_search_activate(self, search):
        self.app_bar.run()
        

win = Window()
win.connect('delete-event', Gtk.main_quit)
Gtk.main()
