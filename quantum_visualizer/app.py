import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from quantum_visualizer.design_system import ThemeService
from quantum_visualizer.education import ExplanationService
from quantum_visualizer.exporters import ExportService
from quantum_visualizer.noise import NoiseService
from quantum_visualizer.parser import CustomStateParser
from quantum_visualizer.plotting import FigureFactory
from quantum_visualizer.states import QuantumStateService
from quantum_visualizer.ui_components import Card, LabeledCombobox, LabeledSlider, ScrollableFrame


class QuantumStateVisualizerApp:
    """Dashboard-style Tkinter UI composition root."""

    HINTON_VIEW = "Hinton diagram (density matrix)"
    CIRCLE_VIEW = "Adaptive circle notation (state vector)"
    COMBINED_VIEW = "Combined view"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Quantum State Visualizer Dashboard")
        self.root.geometry("1500x900")
        self.root.minsize(1120, 720)

        self.theme_service = ThemeService(root)
        self.current_theme_name = tk.StringVar(value="Clean Light")
        self.theme = self.theme_service.apply(self.current_theme_name.get())

        self.state_service = QuantumStateService()
        self.noise_service = NoiseService()
        self.parser = CustomStateParser()
        self.figure_factory = FigureFactory()
        self.explanation_service = ExplanationService()
        self.export_service = ExportService()

        self.state_choice = tk.StringVar(value="Product state |00>")
        self.visualisation_choice = tk.StringVar(value=self.COMBINED_VIEW)
        self.part_choice = tk.StringVar(value="Real and imaginary")
        self.noise_choice = tk.StringVar(value=NoiseService.NO_NOISE)
        self.noise_strength = tk.DoubleVar(value=0.0)
        self.custom_state = tk.StringVar(value="1/sqrt(2), 0, 0, i/sqrt(2)")
        self.show_values = tk.BooleanVar(value=False)
        self.learning_mode = tk.StringVar(value="Beginner mode")
        self.show_phase_details = tk.BooleanVar(value=True)
        self.compare_ideal_noisy = tk.BooleanVar(value=False)
        self.auto_update = tk.BooleanVar(value=True)

        self._update_job: str | None = None
        self.canvas: FigureCanvasTkAgg | None = None
        self.toolbar: NavigationToolbar2Tk | None = None
        self.current_fig = None
        self.current_rho = None
        self.current_state_vector = None

        self.status_text = tk.StringVar(value="Ready")
        self.hover_text = tk.StringVar(value="Hover over a Hinton circle or adaptive circle to inspect its meaning.")

        self._build_ui()
        self.update_plot()
        self.root.after(500, self.show_welcome_tutorial)

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self._build_top_toolbar()
        self._build_main_dashboard()
        self._build_status_bar()

    def _build_top_toolbar(self) -> None:
        toolbar = ttk.Frame(self.root, padding=(12, 9), style="Surface.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(1, weight=1)

        ttk.Label(toolbar, text="Quantum State Visualizer", style="Title.Surface.TLabel").grid(row=0, column=0, sticky="w")

        quick = ttk.Frame(toolbar, style="Surface.TFrame")
        quick.grid(row=0, column=2, sticky="e")
        ttk.Button(quick, text="Tutorial", command=self.show_welcome_tutorial).pack(side="left", padx=3)
        ttk.Button(quick, text="Update", style="Accent.TButton", command=self.update_plot).pack(side="left", padx=3)
        ttk.Button(quick, text="Export PNG", command=self.export_png).pack(side="left", padx=3)
        ttk.Button(quick, text="Export CSV", command=self.export_csv).pack(side="left", padx=3)

    def _build_main_dashboard(self) -> None:
        self.main_pane = ttk.PanedWindow(self.root, orient="horizontal")
        self.main_pane.grid(row=1, column=0, sticky="nsew")

        self.sidebar_container = ttk.Frame(self.main_pane, padding=8)
        self.visual_container = ttk.Frame(self.main_pane, padding=8)
        self.main_pane.add(self.sidebar_container, weight=0)
        self.main_pane.add(self.visual_container, weight=1)

        self._build_sidebar()
        self._build_visual_area()

    def _build_sidebar(self) -> None:
        self.sidebar_container.rowconfigure(0, weight=1)
        self.sidebar_container.columnconfigure(0, weight=1)

        self.sidebar_tabs = ttk.Notebook(self.sidebar_container)
        self.sidebar_tabs.grid(row=0, column=0, sticky="nsew")

        self.state_tab = ScrollableFrame(self.sidebar_tabs)
        self.visual_tab = ScrollableFrame(self.sidebar_tabs)
        self.noise_tab = ScrollableFrame(self.sidebar_tabs)
        self.education_tab = ScrollableFrame(self.sidebar_tabs)
        self.help_tab = ScrollableFrame(self.sidebar_tabs)

        self.sidebar_tabs.add(self.state_tab, text="State")
        self.sidebar_tabs.add(self.visual_tab, text="Visuals")
        self.sidebar_tabs.add(self.noise_tab, text="Noise")
        self.sidebar_tabs.add(self.education_tab, text="Learn")
        self.sidebar_tabs.add(self.help_tab, text="Guide")

        self._build_state_tab(self.state_tab.content)
        self._build_visual_tab(self.visual_tab.content)
        self._build_noise_tab(self.noise_tab.content)
        self._build_education_tab(self.education_tab.content)
        self._build_help_tab(self.help_tab.content)

    def _build_state_tab(self, parent) -> None:
        card = Card(parent, "1. Choose a quantum state")
        card.pack(fill="x", padx=4, pady=4)

        LabeledCombobox(
            card,
            "Quantum state preset",
            self.state_choice,
            self.state_service.preset_names() + ["Custom state vector"],
            self.schedule_update,
        ).pack(fill="x", pady=5)

        ttk.Label(card, text="Custom state vector", style="Surface.TLabel").pack(anchor="w", pady=(8, 3))
        entry = ttk.Entry(card, textvariable=self.custom_state)
        entry.pack(fill="x")
        entry.bind("<KeyRelease>", lambda _event: self.schedule_update(delay_ms=700))
        ttk.Label(card, text="Example: 1/sqrt(2), 0, 0, i/sqrt(2)", style="Muted.Surface.TLabel").pack(anchor="w", pady=(3, 8))

        quick = Card(parent, "Quick learning path")
        quick.pack(fill="x", padx=4, pady=4)
        ttk.Button(quick, text="1. Product state |00>", command=lambda: self.apply_scenario("Product state |00>", NoiseService.NO_NOISE, 0.0)).pack(fill="x", pady=3)
        ttk.Button(quick, text="2. Superposition 2 qubits", command=lambda: self.apply_scenario("Superposition 2 qubits = all basis states", NoiseService.NO_NOISE, 0.0)).pack(fill="x", pady=3)
        ttk.Button(quick, text="3. Bell state", command=lambda: self.apply_scenario("Bell state |Φ+> = (|00> + |11>) / √2", NoiseService.NO_NOISE, 0.0)).pack(fill="x", pady=3)
        ttk.Button(quick, text="4. Bell state with phase", command=lambda: self.apply_scenario("Bell state with phase = (|00> + i|11>) / √2", NoiseService.NO_NOISE, 0.0)).pack(fill="x", pady=3)
        ttk.Button(quick, text="5. Grover 2 qubits", command=lambda: self.apply_scenario("Grover 2 qubits = search target |11>", NoiseService.NO_NOISE, 0.0)).pack(fill="x", pady=3)
        ttk.Button(quick, text="6. Grover 3 qubits", command=lambda: self.apply_scenario("Grover 3 qubits = search target |111>", NoiseService.NO_NOISE, 0.0)).pack(fill="x", pady=3)
        ttk.Button(quick, text="7. GHZ 3 qubits", command=lambda: self.apply_scenario("GHZ state 3 qubits = (|000> + |111>) / √2", NoiseService.NO_NOISE, 0.0)).pack(fill="x", pady=3)
        ttk.Button(quick, text="8. Sparse 4 qubits", command=lambda: self.apply_scenario("Sparse 4 qubits = |0000> + i|1111>", NoiseService.NO_NOISE, 0.0)).pack(fill="x", pady=3)

    def _build_visual_tab(self, parent) -> None:
        display = Card(parent, "2. Choose the visual output")
        display.pack(fill="x", padx=4, pady=4)

        LabeledCombobox(
            display,
            "Visualisation type",
            self.visualisation_choice,
            [self.HINTON_VIEW, self.CIRCLE_VIEW, self.COMBINED_VIEW],
            self.schedule_update,
        ).pack(fill="x", pady=5)

        LabeledCombobox(
            display,
            "Hinton matrix part",
            self.part_choice,
            ["Real and imaginary", "Real part only", "Imaginary part only"],
            self.schedule_update,
        ).pack(fill="x", pady=5)

        options = Card(parent, "Display options")
        options.pack(fill="x", padx=4, pady=4)
        ttk.Checkbutton(options, text="Show numeric values where readable", variable=self.show_values, command=self.schedule_update, style="Surface.TCheckbutton").pack(anchor="w", pady=3)
        ttk.Checkbutton(options, text="Always show phase gauges", variable=self.show_phase_details, command=self.schedule_update, style="Surface.TCheckbutton").pack(anchor="w", pady=3)
        ttk.Checkbutton(options, text="Auto-update", variable=self.auto_update, style="Surface.TCheckbutton").pack(anchor="w", pady=3)

        style_card = Card(parent, "Interface style")
        style_card.pack(fill="x", padx=4, pady=4)
        LabeledCombobox(
            style_card,
            "Theme",
            self.current_theme_name,
            self.theme_service.theme_names(),
            self.change_theme,
        ).pack(fill="x", pady=5)

        ttk.Label(
            style_card,
            text="Controls are grouped by task: State → Visuals → Noise → Learn. This keeps the testing flow easier for participants.",
            style="Muted.Surface.TLabel",
            wraplength=330,
        ).pack(anchor="w", pady=(8, 0))

    def _build_noise_tab(self, parent) -> None:
        card = Card(parent, "3. Configure quantum noise")
        card.pack(fill="x", padx=4, pady=4)

        LabeledCombobox(
            card,
            "Noise model",
            self.noise_choice,
            self.noise_service.models(),
            self.schedule_update,
        ).pack(fill="x", pady=5)

        LabeledSlider(card, "Noise strength", self.noise_strength, lambda: self.schedule_update(delay_ms=250)).pack(fill="x", pady=8)

        ttk.Checkbutton(card, text="Compare ideal vs noisy state", variable=self.compare_ideal_noisy, command=self.schedule_update, style="Surface.TCheckbutton").pack(anchor="w", pady=3)

        ttk.Label(
            card,
            text=(
                "Tip: start with a Bell or GHZ state, then increase noise slowly. "
                "The noisy circle view keeps phase gauges visible, but they are approximate phase hints. "
                "Use the Hinton real/imaginary views for exact density-matrix structure."
            ),
            style="Muted.Surface.TLabel",
            wraplength=330,
        ).pack(anchor="w", pady=(8, 0))

        quick = Card(parent, "Noise scenarios")
        quick.pack(fill="x", padx=4, pady=4)
        ttk.Button(quick, text="Bell state + no noise", command=lambda: self.apply_scenario("Bell state |Φ+> = (|00> + |11>) / √2", NoiseService.NO_NOISE, 0.0)).pack(fill="x", pady=3)
        ttk.Button(quick, text="Bell state + depolarizing noise", command=lambda: self.apply_scenario("Bell state |Φ+> = (|00> + |11>) / √2", NoiseService.DEPOLARIZING, 0.35)).pack(fill="x", pady=3)
        ttk.Button(quick, text="Grover 3 qubits + noise", command=lambda: self.apply_scenario("Grover 3 qubits = search target |111>", NoiseService.DEPOLARIZING, 0.25)).pack(fill="x", pady=3)
        ttk.Button(quick, text="GHZ + medium noise", command=lambda: self.apply_scenario("GHZ state 3 qubits = (|000> + |111>) / √2", NoiseService.DEPOLARIZING, 0.35)).pack(fill="x", pady=3)
        ttk.Button(quick, text="4-qubit sparse + noise", command=lambda: self.apply_scenario("Sparse 4 qubits = |0000> + i|1111>", NoiseService.DEPOLARIZING, 0.25)).pack(fill="x", pady=3)

    def _build_education_tab(self, parent) -> None:
        concept_card = Card(parent, "What the visualisations mean")
        concept_card.pack(fill="x", padx=4, pady=4)

        text = (
            "Hinton diagram values:\n"
            "• The number inside a Hinton circle is the density-matrix value.\n"
            "• On the diagonal, this is usually a measurement probability.\n"
            "• Off the diagonal, this represents coherence between two basis states.\n"
            "• White circles mean positive values; black circles mean negative values.\n"
            "• Larger circles mean larger absolute values.\n\n"
            "Adaptive circle notation:\n"
            "• Blue area shows probability.\n"
            "• Gauge line shows phase.\n"
            "• For pure states, phase is exact from the state vector.\n"
            "• For noisy states, probability is exact from the density matrix diagonal.\n"
            "• For noisy states, phase is an approximate dominant-state hint.\n\n"
            "Grover examples:\n"
            "• Grover states show amplitude amplification.\n"
            "• The marked answer should become visually dominant.\n"
            "• Add noise to see whether the answer becomes less clear.\n\n"
            "Important: for noisy/mixed states, the Hinton real and imaginary views are the most faithful view of coherence."
        )
        body = tk.Text(concept_card, height=18, wrap="word", relief="flat")
        body.insert("1.0", text)
        body.configure(state="disabled")
        body.pack(fill="both", expand=True)

        interaction_card = Card(parent, "Interactive interpretation")
        interaction_card.pack(fill="x", padx=4, pady=4)

        ttk.Label(interaction_card, text="Hover feedback:", style="Heading.Surface.TLabel").pack(anchor="w", pady=(0, 4))
        self.hover_label = ttk.Label(
            interaction_card,
            textvariable=self.hover_text,
            style="Muted.Surface.TLabel",
            wraplength=330,
            justify="left",
        )
        self.hover_label.pack(fill="x", pady=(0, 8))

        ttk.Label(interaction_card, text="Current interpretation:", style="Heading.Surface.TLabel").pack(anchor="w", pady=(6, 4))
        self.explanation_box = tk.Text(interaction_card, height=13, wrap="word", relief="flat")
        self.explanation_box.pack(fill="both", expand=True)
        self.explanation_box.configure(state="disabled")

    def _build_help_tab(self, parent) -> None:
        card = Card(parent, "Participant guide")
        card.pack(fill="both", expand=True, padx=4, pady=4)

        help_text = (
            "Recommended testing flow:\n"
            "1. State tab: choose Product state |00>.\n"
            "2. State tab: try Superposition 2 qubits.\n"
            "3. State tab: try Bell state and Bell state with phase.\n"
            "4. State tab: try Grover 2 and 3 qubit search states.\n"
            "5. State tab: try GHZ and W states.\n"
            "6. Visuals tab: compare Hinton, Circle, and Combined view.\n"
            "7. Noise tab: add noise gradually.\n"
            "8. Noise tab: enable ideal-vs-noisy comparison.\n"
            "9. Learn tab: read hover explanations and interpretation.\n\n"
            "Ask yourself:\n"
            "• Which visualisation is easiest to understand?\n"
            "• Which visualisation shows noise most clearly?\n"
            "• Does adaptive layout help when qubits increase?\n"
            "• Do hover explanations help you understand the values?"
        )
        text = tk.Text(card, height=26, wrap="word", relief="flat")
        text.insert("1.0", help_text)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True)

    def _build_visual_area(self) -> None:
        self.visual_container.rowconfigure(0, weight=1)
        self.visual_container.columnconfigure(0, weight=1)
        self.plot_card = Card(self.visual_container)
        self.plot_card.grid(row=0, column=0, sticky="nsew")
        self.plot_card.rowconfigure(0, weight=1)
        self.plot_card.columnconfigure(0, weight=1)

    def _build_status_bar(self) -> None:
        status = ttk.Frame(self.root, padding=(10, 4), style="AltSurface.TFrame")
        status.grid(row=2, column=0, sticky="ew")
        ttk.Label(status, textvariable=self.status_text).pack(side="left")

    def change_theme(self) -> None:
        self.theme = self.theme_service.apply(self.current_theme_name.get())
        self.schedule_update(delay_ms=100)

    def apply_scenario(self, state: str, noise: str, strength: float) -> None:
        self.state_choice.set(state)
        self.noise_choice.set(noise)
        self.noise_strength.set(strength)
        self.visualisation_choice.set(self.COMBINED_VIEW)
        self.update_plot()

    def schedule_update(self, delay_ms: int = 250) -> None:
        if not self.auto_update.get():
            return
        if self._update_job is not None:
            self.root.after_cancel(self._update_job)
        self._update_job = self.root.after(delay_ms, self.update_plot)

    def _get_selected_state_vector(self) -> np.ndarray:
        if self.state_choice.get() == "Custom state vector":
            return self.parser.parse_state_vector(self.custom_state.get())
        return self.state_service.create_preset(self.state_choice.get())

    def update_plot(self) -> None:
        self._update_job = None

        try:
            original_state_vector = self._get_selected_state_vector()
            number_of_qubits = QuantumStateService.number_of_qubits(original_state_vector)

            ideal_rho = self.state_service.ket_to_density_matrix(original_state_vector)
            noisy_rho = self.noise_service.apply(
                ideal_rho,
                self.noise_choice.get(),
                self.noise_strength.get(),
            )

            beginner_mode = self.learning_mode.get() == "Beginner mode"
            show_phase = True  # phase gauge is intentionally always visible
            effective_show_values = self.show_values.get() and not beginner_mode

            noise_is_active = (
                self.noise_choice.get() != NoiseService.NO_NOISE
                and self.noise_strength.get() > 0.001
            )

            self.current_rho = noisy_rho
            self.current_state_vector = original_state_vector

            if self.compare_ideal_noisy.get() and noise_is_active:
                fig = self.figure_factory.create_ideal_vs_noisy(
                    ideal_rho=ideal_rho,
                    noisy_rho=noisy_rho,
                    ideal_state_vector=original_state_vector,
                    show_values=effective_show_values,
                    show_phase=show_phase,
                )
            elif self.visualisation_choice.get() == self.HINTON_VIEW:
                fig = self.figure_factory.create_hinton(
                    rho=noisy_rho,
                    selected_part=self.part_choice.get(),
                    show_values=effective_show_values,
                )
            elif self.visualisation_choice.get() == self.CIRCLE_VIEW:
                fig = self.figure_factory.create_circle(
                    state_vector=original_state_vector,
                    rho=noisy_rho,
                    show_values=effective_show_values,
                    show_phase=show_phase,
                    use_density_probabilities=noise_is_active,
                )
            else:
                fig = self.figure_factory.create_combined(
                    rho=noisy_rho,
                    state_vector=original_state_vector,
                    selected_part=self.part_choice.get(),
                    show_values=effective_show_values,
                    show_phase=show_phase,
                    use_density_probabilities=noise_is_active,
                )

            self.current_fig = fig
            self._render_figure(fig)

            explanation = self.explanation_service.explain(
                self.state_choice.get(),
                self.visualisation_choice.get(),
                self.noise_choice.get(),
                self.noise_strength.get(),
                number_of_qubits,
                self.learning_mode.get(),
                self.compare_ideal_noisy.get(),
            )

            if noise_is_active:
                explanation += (
                    "\n\nImportant phase note:\n"
                    "The noisy circle view keeps phase gauges visible. The probabilities come directly from "
                    "the density-matrix diagonal. The phase gauge is an approximate dominant-state phase hint, "
                    "because a mixed noisy state does not have one unique pure-state phase per basis state. "
                    "For exact noisy coherence, inspect the real and imaginary Hinton diagrams."
                )

            self._set_explanation(explanation)
            self.hover_text.set("Hover over a Hinton circle or adaptive circle to inspect its meaning.")
            self.status_text.set(
                f"{number_of_qubits} qubit(s) | {2 ** number_of_qubits} basis states | "
                f"{self.visualisation_choice.get()} | {self.noise_choice.get()}"
            )

        except Exception as error:
            messagebox.showerror("Visualisation error", str(error))
            self.status_text.set(f"Error: {error}")

    def _render_figure(self, fig) -> None:
        for child in self.plot_card.winfo_children():
            child.destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_card)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas.mpl_connect("motion_notify_event", self._on_plot_hover)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_card, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=1, column=0, sticky="ew")

    def _on_plot_hover(self, event) -> None:
        if event.inaxes is None or event.xdata is None or event.ydata is None:
            self.hover_text.set("Hover over a Hinton circle or adaptive circle to inspect its meaning.")
            return

        hover_items = getattr(event.inaxes, "_qv_hover_items", [])
        for item in hover_items:
            dx = float(event.xdata) - float(item["x"])
            dy = float(event.ydata) - float(item["y"])
            radius = float(item.get("radius", 0.25))
            if dx * dx + dy * dy <= radius * radius:
                self.hover_text.set(item["text"])
                self.status_text.set(item["text"])
                return

        self.hover_text.set("Hover over a Hinton circle or adaptive circle to inspect its meaning.")

    def _set_explanation(self, text: str) -> None:
        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("1.0", tk.END)
        self.explanation_box.insert(tk.END, text)
        self.explanation_box.configure(state="disabled")

    def export_png(self) -> None:
        if self.current_fig is None:
            messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image", "*.png")], title="Save visualisation as PNG")
        if path:
            self.export_service.export_figure_png(self.current_fig, path)
            messagebox.showinfo("Export complete", f"Saved visualisation to:\n{path}")

    def export_csv(self) -> None:
        if self.current_rho is None:
            messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv")], title="Save density matrix as CSV")
        if path:
            self.export_service.export_density_matrix_csv(self.current_rho, path)
            messagebox.showinfo("Export complete", f"Saved density matrix to:\n{path}")

    def show_welcome_tutorial(self) -> None:
        messagebox.showinfo("Beginner tutorial", self.explanation_service.welcome_text())


def main() -> None:
    root = tk.Tk()
    QuantumStateVisualizerApp(root)
    root.mainloop()
