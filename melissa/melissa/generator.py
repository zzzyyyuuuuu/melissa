import os
import json

# Hazır temalar
THEMES = {
    "Dark Minimal": {
        "background": "#1e1e2e",
        "foreground": "#cdd6f4",
        "accent": "#89b4fa",
        "hover": "#313244"
    },
    "Nord": {
        "background": "#2e3440",
        "foreground": "#eceff4",
        "accent": "#88c0d0",
        "hover": "#434c5e"
    },
    "Catppuccin": {
        "background": "#1e1e28",
        "foreground": "#d7dae0",
        "accent": "#f5c2e7",
        "hover": "#302d41"
    },
    "Gruvbox": {
        "background": "#282828",
        "foreground": "#ebdbb2",
        "accent": "#fabd2f",
        "hover": "#3c3836"
    }
}

def generate_config(modules, positions, bar_pos, font, matugen, wm, size, theme):
    config_dir = os.path.expanduser("~/.config/waybar")
    os.makedirs(config_dir, exist_ok=True)

    # Modülleri konumlarına göre ayır
    modules_left, modules_center, modules_right = [], [], []
    for m in modules:
        pos = positions.get(m, "left")
        if pos == "left":
            modules_left.append(m)
        elif pos == "center":
            modules_center.append(m)
        else:
            modules_right.append(m)

    # 🔥 WM parametresini stringe çeviriyoruz
    wm_str = wm if isinstance(wm, str) else "hyprland"
    wm_str = wm_str.lower()

    # 🔥 WM'ye göre workspace modülü
    if wm_str == "hyprland":
        workspace_module = "hyprland/workspaces"
    elif wm_str == "sway":
        workspace_module = "sway/workspaces"
    else:
        workspace_module = "wlr/workspaces"

    # Workspace'i solun başına ekle
    modules_left.insert(0, workspace_module)

    # Bar config
    bar_config = {
        "layer": "top",
        "position": bar_pos,
        "modules-left": modules_left,
        "modules-center": modules_center,
        "modules-right": modules_right,
    }

    # Bar boyutu
    if bar_pos in ["top", "bottom"]:
        bar_config["height"] = size
    else:
        bar_config["width"] = size

    # Workspace modül ayarları
    bar_config[workspace_module] = {
        "format": "{name}",
        "on-click": "activate",
        "disable-scroll": False,
        "active-only": False,
        "sort-by-number": True
    }

    # JSON array olarak yaz
    config = [bar_config]
    with open(os.path.join(config_dir, "config"), "w") as f:
        json.dump(config, f, indent=4)

    # 🔥 CSS theme
    selected_theme = THEMES.get(theme, THEMES["Dark Minimal"])
    style_css = f"""
* {{
    background: {selected_theme['background']};
    color: {selected_theme['foreground']};
    font-family: "{font}";
    font-size: 13px;
}}

#workspaces {{
    margin: 6px 4px;
}}

#workspaces button {{
    padding: 4px 10px;
    border-radius: 8px;
    margin: 2px;
    background: transparent;
}}

#workspaces button.active {{
    background: {selected_theme['accent']};
    color: {selected_theme['background']};
}}

#workspaces button.urgent {{
    background: #f38ba8;
}}

#clock, #cpu, #memory, #battery, #network {{
    padding: 4px 10px;
    margin: 4px;
    border-radius: 8px;
    background: {selected_theme['hover']};
}}

window#waybar {{
    background: {selected_theme['background']};
}}
"""
    with open(os.path.join(config_dir, "style.css"), "w") as f:
        f.write(style_css)
