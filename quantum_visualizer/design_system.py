
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk


@dataclass(frozen=True)
class AppTheme:
    """Central design tokens for the dashboard UI."""
    name: str
    background: str
    surface: str
    surface_alt: str
    text: str
    muted_text: str
    accent: str
    accent_dark: str
    warning: str
    border: str
    success: str
    font_family: str = "Segoe UI"


LIGHT_THEME = AppTheme(
    name="Clean Light",
    background="#EEF3F8",
    surface="#FFFFFF",
    surface_alt="#DDE7F1",
    text="#102033",
    muted_text="#5A677A",
    accent="#2563EB",
    accent_dark="#1D4ED8",
    warning="#B45309",
    border="#C8D4E3",
    success="#047857",
)

HIGH_CONTRAST_THEME = AppTheme(
    name="High Contrast",
    background="#0B1220",
    surface="#111827",
    surface_alt="#1F2937",
    text="#F8FAFC",
    muted_text="#CBD5E1",
    accent="#60A5FA",
    accent_dark="#3B82F6",
    warning="#FBBF24",
    border="#334155",
    success="#34D399",
)


class ThemeService:
    """
    Applies a consistent ttk style.

    SOLID:
    - Single Responsibility: styling only.
    - Open/Closed: add themes without changing UI logic.
    """

    THEMES = {
        LIGHT_THEME.name: LIGHT_THEME,
        HIGH_CONTRAST_THEME.name: HIGH_CONTRAST_THEME,
    }

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.style = ttk.Style(root)
        self.current_theme = LIGHT_THEME

    def theme_names(self) -> list[str]:
        return list(self.THEMES.keys())

    def apply(self, theme_name: str) -> AppTheme:
        self.current_theme = self.THEMES.get(theme_name, LIGHT_THEME)
        theme = self.current_theme

        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.root.configure(bg=theme.background)

        base_font = (theme.font_family, 10)
        heading_font = (theme.font_family, 12, "bold")
        title_font = (theme.font_family, 17, "bold")

        self.style.configure(".", font=base_font, background=theme.background, foreground=theme.text)
        self.style.configure("TFrame", background=theme.background)
        self.style.configure("Surface.TFrame", background=theme.surface, relief="flat")
        self.style.configure("AltSurface.TFrame", background=theme.surface_alt, relief="flat")
        self.style.configure("TLabel", background=theme.background, foreground=theme.text)
        self.style.configure("Surface.TLabel", background=theme.surface, foreground=theme.text)
        self.style.configure("Muted.Surface.TLabel", background=theme.surface, foreground=theme.muted_text)
        self.style.configure("Title.Surface.TLabel", background=theme.surface, foreground=theme.text, font=title_font)
        self.style.configure("Heading.Surface.TLabel", background=theme.surface, foreground=theme.text, font=heading_font)
        self.style.configure("TButton", padding=(10, 6))
        self.style.configure("Accent.TButton", padding=(10, 7), foreground="#FFFFFF", background=theme.accent)
        self.style.map("Accent.TButton", background=[("active", theme.accent_dark)])
        self.style.configure("TCheckbutton", background=theme.background, foreground=theme.text)
        self.style.configure("Surface.TCheckbutton", background=theme.surface, foreground=theme.text)
        self.style.configure("TCombobox", padding=4)
        self.style.configure("Horizontal.TScale", background=theme.surface)
        self.style.configure("TNotebook", background=theme.background, borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=(12, 7), background=theme.surface_alt, foreground=theme.text)
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", theme.surface), ("active", theme.surface)],
            foreground=[("selected", theme.accent_dark), ("active", theme.accent_dark)],
        )
        self.style.configure("Vertical.TScrollbar", background=theme.surface_alt)

        return theme
