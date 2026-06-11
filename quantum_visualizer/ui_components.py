
import tkinter as tk
from tkinter import ttk
from typing import Callable


class ScrollableFrame(ttk.Frame):
    """Reusable scrollable frame for sidebars and long forms."""

    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = ttk.Frame(self.canvas)

        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_content_configure(self, _event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _on_mousewheel(self, event) -> None:
        # Windows/macOS friendly scrolling.
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class Card(ttk.Frame):
    """Simple reusable card container."""

    def __init__(self, master, title: str | None = None, *args, **kwargs) -> None:
        super().__init__(master, style="Surface.TFrame", padding=12, *args, **kwargs)
        if title:
            ttk.Label(self, text=title, style="Heading.Surface.TLabel").pack(anchor="w", pady=(0, 8))


class LabeledCombobox(ttk.Frame):
    """Label + readonly combobox with consistent spacing."""

    def __init__(self, master, label: str, variable: tk.StringVar, values: list[str], command: Callable | None = None) -> None:
        super().__init__(master, style="Surface.TFrame")
        ttk.Label(self, text=label, style="Surface.TLabel").pack(anchor="w", pady=(0, 3))
        self.combobox = ttk.Combobox(self, textvariable=variable, values=values, state="readonly")
        self.combobox.pack(fill="x")
        if command:
            self.combobox.bind("<<ComboboxSelected>>", lambda _event: command())


class LabeledSlider(ttk.Frame):
    """Label + slider + value display."""

    def __init__(self, master, label: str, variable: tk.DoubleVar, command: Callable | None = None) -> None:
        super().__init__(master, style="Surface.TFrame")
        self.label = ttk.Label(self, text=label, style="Surface.TLabel")
        self.label.pack(anchor="w", pady=(0, 3))
        self.value_label = ttk.Label(self, text=f"{variable.get():.2f}", style="Muted.Surface.TLabel")
        self.value_label.pack(anchor="w")
        self.scale = ttk.Scale(self, from_=0.0, to=1.0, variable=variable, orient="horizontal", command=self._changed)
        self.scale.pack(fill="x", pady=(3, 0))
        self.variable = variable
        self.command = command

    def _changed(self, value: str) -> None:
        self.value_label.config(text=f"{float(value):.2f}")
        if self.command:
            self.command()
