import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gdk
from melissa.generator import generate_config

MODULES = ["clock", "cpu", "memory", "battery", "network"]
POSITIONS = ["Left", "Center", "Right"]
BAR_POSITIONS = ["top", "bottom", "left", "right"]
WAYLAND_WMS = ["sway", "hyprland", "river", "qtile"]

class MelissaWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Melissa - Waybar Config Builder")
        self.set_default_size(550, 750)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(15)
        main_box.set_margin_bottom(15)
        main_box.set_margin_start(15)
        main_box.set_margin_end(15)
        self.set_content(main_box)

        # Title
        title = Gtk.Label(label="Waybar Config Builder")
        title.add_css_class("title")
        main_box.append(title)

        # Window Manager selection
        wm_label = Gtk.Label(label="Window Manager (Wayland only)")
        wm_label.set_xalign(0)
        main_box.append(wm_label)
        self.wm_combo = Gtk.DropDown.new_from_strings(WAYLAND_WMS)
        main_box.append(self.wm_combo)

        # Bar position
        bar_label = Gtk.Label(label="Bar Position")
        bar_label.set_xalign(0)
        main_box.append(bar_label)
        self.bar_pos_combo = Gtk.DropDown.new_from_strings(BAR_POSITIONS)
        main_box.append(self.bar_pos_combo)

        # Bar size
        size_box = Gtk.Box(spacing=10)
        size_box.append(Gtk.Label(label="Bar Size (px):"))
        self.bar_size_spin = Gtk.SpinButton.new_with_range(20, 200, 1)
        self.bar_size_spin.set_value(30)  # default 30px
        size_box.append(self.bar_size_spin)
        main_box.append(size_box)

        # Matugen mode
        self.matugen_switch = Gtk.Switch()
        matugen_box = Gtk.Box(spacing=10)
        matugen_box.append(Gtk.Label(label="Matugen Mode"))
        matugen_box.append(self.matugen_switch)
        main_box.append(matugen_box)

        # Module checkboxes and position
        self.module_boxes = {}
        self.module_positions = {}
        for mod in MODULES:
            box = Gtk.Box(spacing=10)
            cb = Gtk.CheckButton(label=mod)
            combo = Gtk.DropDown.new_from_strings(POSITIONS)
            combo.set_selected(0)  # default Left
            box.append(cb)
            box.append(combo)
            main_box.append(box)
            self.module_boxes[mod] = cb
            self.module_positions[mod] = combo

        # Colors
        main_box.append(Gtk.Label(label="Select Colors:"))
        self.bg_color = Gtk.ColorButton(title="Bar Background")
        self.fg_color = Gtk.ColorButton(title="Text Color")
        self.hover_color = Gtk.ColorButton(title="Hover Color")
        self.caret_color = Gtk.ColorButton(title="Cursor Color")
        for btn in [self.bg_color, self.fg_color, self.hover_color, self.caret_color]:
            main_box.append(btn)

        # Font chooser using Gtk.FontChooserDialog
        font_box = Gtk.Box(spacing=10)
        font_box.append(Gtk.Label(label="Font:"))
        self.font_button = Gtk.Button(label="Choose Font")
        self.selected_font = "Monospace 10"
        self.font_button.connect("clicked", self.on_font_clicked)
        font_box.append(self.font_button)
        main_box.append(font_box)

        # Buttons
        btn_box = Gtk.Box(spacing=10)
        generate_btn = Gtk.Button(label="Generate")
        generate_btn.add_css_class("suggested-action")
        generate_btn.connect("clicked", self.on_generate_clicked)
        reset_btn = Gtk.Button(label="Reset")
        reset_btn.connect("clicked", self.on_reset_clicked)
        btn_box.append(generate_btn)
        btn_box.append(reset_btn)
        main_box.append(btn_box)

        # Status label
        self.status_label = Gtk.Label(label="")
        main_box.append(self.status_label)

    def on_font_clicked(self, button):
        dialog = Gtk.FontChooserDialog(title="Select Font", transient_for=self)
        dialog.set_font(self.selected_font)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.selected_font = dialog.get_font()
            button.set_label(f"Font: {self.selected_font}")
        dialog.destroy()

    def on_generate_clicked(self, button):
        modules = []
        positions = {}
        for mod in MODULES:
            if self.module_boxes[mod].get_active():
                modules.append(mod)
                positions[mod] = self.module_positions[mod].get_selected_item().get_string().lower()
        bar_pos = self.bar_pos_combo.get_selected_item().get_string().lower()
        bar_size = int(self.bar_size_spin.get_value())
        wm = self.wm_combo.get_selected_item().get_string()
        colors = {
            "background": self.get_color_hex(self.bg_color),
            "foreground": self.get_color_hex(self.fg_color),
            "hover": self.get_color_hex(self.hover_color),
            "caret": self.get_color_hex(self.caret_color)
        }
        font = self.selected_font
        matugen = self.matugen_switch.get_active()

        try:
            generate_config(modules, positions, bar_pos, colors, font, matugen, wm, bar_size)
            self.status_label.set_label("Waybar config generated successfully!")
        except Exception as e:
            self.status_label.set_label(f"Error: {str(e)}")

    def on_reset_clicked(self, button):
        for mod in MODULES:
            self.module_boxes[mod].set_active(False)
            self.module_positions[mod].set_selected(0)
        self.bar_pos_combo.set_selected(0)
        self.bar_size_spin.set_value(30)
        self.wm_combo.set_selected(0)
        self.matugen_switch.set_active(False)
        # default colors
        self.bg_color.set_rgba(Gdk.RGBA(0.157,0.172,0.204,1))  # #282c34
        self.fg_color.set_rgba(Gdk.RGBA(0.671,0.694,0.749,1))  # #abb2bf
        self.hover_color.set_rgba(Gdk.RGBA(0.380,0.686,0.937,1))  # #61afef
        self.caret_color.set_rgba(Gdk.RGBA(0.878,0.424,0.459,1))  # #e06c75
        self.selected_font = "Monospace 10"
        self.font_button.set_label("Choose Font")
        self.status_label.set_label("")

    def get_color_hex(self, color_button):
        c = color_button.get_rgba()
        return f"#{int(c.red*255):02x}{int(c.green*255):02x}{int(c.blue*255):02x}"

class MelissaApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.melissa.waybar")

    def do_activate(self):
        win = MelissaWindow(self)
        win.present()

if __name__ == "__main__":
    app = MelissaApp()
    app.run()
