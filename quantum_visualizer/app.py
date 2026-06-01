import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from quantum_visualizer.education import ExplanationService
from quantum_visualizer.exporters import ExportService
from quantum_visualizer.noise import NoiseService
from quantum_visualizer.parser import CustomStateParser
from quantum_visualizer.plotting import FigureFactory
from quantum_visualizer.states import QuantumStateService


class QuantumStateVisualiserApp:
    """
    Tkinter UI composition root.

    SOLID:
    - UI knows how to connect widgets and services.
    - Quantum logic, noise, plotting, export, and explanations are delegated.
    """

    HINTON_VIEW = "Hinton diagram (density matrix)"
    CIRCLE_VIEW = "Adaptive circle notation (state vector)"
    COMBINED_VIEW = "Combined view"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Quantum State Visualiser")
        self.root.geometry("1450x880")

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
        self.show_phase_details = tk.BooleanVar(value=False)
        self.compare_ideal_noisy = tk.BooleanVar(value=False)
        self.auto_update = tk.BooleanVar(value=True)

        self._update_job: str | None = None
        self.canvas: FigureCanvasTkAgg | None = None
        self.toolbar: NavigationToolbar2Tk | None = None
        self.current_fig = None
        self.current_rho = None
        self.current_state_vector = None

        self._build_ui()
        self.update_plot()
        self.root.after(500, self.show_welcome_tutorial)

    def _build_ui(self) -> None:
        self.control_frame = ttk.Frame(self.root, padding=12)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.plot_frame = ttk.Frame(self.root, padding=8)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        title = ttk.Label(self.control_frame, text="Quantum State Visualiser", font=("Arial", 16, "bold"))
        title.pack(anchor="w", pady=(0, 8))

        ttk.Button(
            self.control_frame,
            text="Beginner tutorial / How to read this",
            command=self.show_welcome_tutorial,
        ).pack(anchor="w", fill=tk.X, pady=(0, 8))

        ttk.Label(
            self.control_frame,
            text="Recommended start: Product state → Superposition → Bell state → add noise.",
            foreground="dimgray",
            wraplength=390,
        ).pack(anchor="w", pady=(0, 12))

        self._add_learning_controls()
        self._add_state_controls()
        self._add_visualisation_controls()
        self._add_noise_controls()
        self._add_action_controls()
        self._add_explanation_panel()

    def _add_learning_controls(self) -> None:
        ttk.Label(self.control_frame, text="Learning mode:").pack(anchor="w")
        mode_menu = ttk.Combobox(
            self.control_frame,
            textvariable=self.learning_mode,
            values=["Beginner mode", "Advanced mode"],
            state="readonly",
            width=58,
        )
        mode_menu.pack(anchor="w", pady=(4, 8))
        mode_menu.bind("<<ComboboxSelected>>", lambda _event: self.schedule_update())

        ttk.Checkbutton(
            self.control_frame,
            text="Show phase details",
            variable=self.show_phase_details,
            command=self.schedule_update,
        ).pack(anchor="w", pady=(0, 4))

        ttk.Checkbutton(
            self.control_frame,
            text="Compare ideal vs noisy state",
            variable=self.compare_ideal_noisy,
            command=self.schedule_update,
        ).pack(anchor="w", pady=(0, 14))

    def _add_state_controls(self) -> None:
        ttk.Label(self.control_frame, text="1. Choose quantum state:").pack(anchor="w")
        state_menu = ttk.Combobox(
            self.control_frame,
            textvariable=self.state_choice,
            values=self.state_service.preset_names() + ["Custom state vector"],
            state="readonly",
            width=58,
        )
        state_menu.pack(anchor="w", pady=(4, 10))
        state_menu.bind("<<ComboboxSelected>>", lambda _event: self.schedule_update())

        ttk.Label(self.control_frame, text="Custom vector:").pack(anchor="w")
        custom_entry = ttk.Entry(self.control_frame, textvariable=self.custom_state, width=61)
        custom_entry.pack(anchor="w", pady=(4, 10))
        custom_entry.bind("<KeyRelease>", lambda _event: self.schedule_update(delay_ms=700))

        ttk.Label(
            self.control_frame,
            text="Example: 1/sqrt(2), 0, 0, i/sqrt(2)",
            foreground="gray",
        ).pack(anchor="w", pady=(0, 12))

    def _add_visualisation_controls(self) -> None:
        ttk.Label(self.control_frame, text="2. Choose visualisation:").pack(anchor="w")
        visualisation_menu = ttk.Combobox(
            self.control_frame,
            textvariable=self.visualisation_choice,
            values=[self.HINTON_VIEW, self.CIRCLE_VIEW, self.COMBINED_VIEW],
            state="readonly",
            width=58,
        )
        visualisation_menu.pack(anchor="w", pady=(4, 12))
        visualisation_menu.bind("<<ComboboxSelected>>", lambda _event: self.schedule_update())

        ttk.Label(self.control_frame, text="3. Hinton matrix part:").pack(anchor="w")
        part_menu = ttk.Combobox(
            self.control_frame,
            textvariable=self.part_choice,
            values=["Real and imaginary", "Real part only", "Imaginary part only"],
            state="readonly",
            width=58,
        )
        part_menu.pack(anchor="w", pady=(4, 12))
        part_menu.bind("<<ComboboxSelected>>", lambda _event: self.schedule_update())

    def _add_noise_controls(self) -> None:
        ttk.Label(self.control_frame, text="4. Add noise:").pack(anchor="w")
        noise_menu = ttk.Combobox(
            self.control_frame,
            textvariable=self.noise_choice,
            values=self.noise_service.models(),
            state="readonly",
            width=58,
        )
        noise_menu.pack(anchor="w", pady=(4, 8))
        noise_menu.bind("<<ComboboxSelected>>", lambda _event: self.schedule_update())

        ttk.Label(self.control_frame, text="Noise strength:").pack(anchor="w")
        ttk.Scale(
            self.control_frame,
            from_=0.0,
            to=1.0,
            variable=self.noise_strength,
            orient="horizontal",
            length=360,
            command=self._on_noise_slider_change,
        ).pack(anchor="w", pady=(4, 2))

        self.noise_value_label = ttk.Label(self.control_frame, text="0.00")
        self.noise_value_label.pack(anchor="w", pady=(0, 12))

    def _add_action_controls(self) -> None:
        ttk.Checkbutton(
            self.control_frame,
            text="Show numeric values where readable",
            variable=self.show_values,
            command=self.schedule_update,
        ).pack(anchor="w", pady=(0, 12))

        ttk.Button(self.control_frame, text="Update visualisation now", command=self.update_plot).pack(
            anchor="w", fill=tk.X, pady=(4, 8)
        )

        ttk.Checkbutton(
            self.control_frame,
            text="Auto-update when settings change",
            variable=self.auto_update,
        ).pack(anchor="w", pady=(0, 8))

        ttk.Button(self.control_frame, text="Export visualisation as PNG", command=self.export_png).pack(
            anchor="w", fill=tk.X, pady=(0, 8)
        )

        ttk.Button(self.control_frame, text="Export density matrix as CSV", command=self.export_csv).pack(
            anchor="w", fill=tk.X, pady=(0, 14)
        )

    def _add_explanation_panel(self) -> None:
        ttk.Label(self.control_frame, text="Explanation:", font=("Arial", 11, "bold")).pack(anchor="w")

        self.explanation_box = tk.Text(self.control_frame, width=52, height=18, wrap="word")
        self.explanation_box.pack(anchor="w", pady=(4, 10))
        self.explanation_box.configure(state="disabled")

        ttk.Label(
            self.control_frame,
            text=(
                "How to read it:\n"
                "Hinton view:\n"
                "• Bigger circle = larger matrix value\n"
                "• Diagonal = probabilities\n"
                "• Off-diagonal = coherence relationships\n\n"
                "Adaptive circle notation:\n"
                "• Inner radius = |α|\n"
                "• Filled area = |α|² probability\n"
                "• Gauge line = complex phase\n"
                "• More qubits → less detail, cleaner layout"
            ),
            justify="left",
            wraplength=390,
        ).pack(anchor="w")

    def _on_noise_slider_change(self, value: str) -> None:
        self.noise_value_label.config(text=f"{float(value):.2f}")
        self.schedule_update(delay_ms=250)

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
            noisy_rho = self.noise_service.apply(ideal_rho, self.noise_choice.get(), self.noise_strength.get())

            if self.noise_choice.get() == NoiseService.NO_NOISE:
                display_state_vector = original_state_vector
            else:
                display_state_vector = self.noise_service.dominant_state_from_density_matrix(noisy_rho)

            beginner_mode = self.learning_mode.get() == "Beginner mode"
            show_phase = self.show_phase_details.get() or self.learning_mode.get() == "Advanced mode"
            effective_show_values = self.show_values.get() and not beginner_mode

            self.current_rho = noisy_rho
            self.current_state_vector = display_state_vector

            if self.compare_ideal_noisy.get() and self.noise_choice.get() != NoiseService.NO_NOISE:
                fig = self.figure_factory.create_ideal_vs_noisy(
                    ideal_rho,
                    noisy_rho,
                    original_state_vector,
                    display_state_vector,
                    effective_show_values,
                    show_phase,
                )
            elif self.visualisation_choice.get() == self.HINTON_VIEW:
                fig = self.figure_factory.create_hinton(noisy_rho, self.part_choice.get(), effective_show_values)
            elif self.visualisation_choice.get() == self.CIRCLE_VIEW:
                fig = self.figure_factory.create_circle(display_state_vector, effective_show_values, show_phase)
            else:
                fig = self.figure_factory.create_combined(
                    noisy_rho,
                    display_state_vector,
                    self.part_choice.get(),
                    effective_show_values,
                    show_phase,
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
            self._set_explanation(explanation)

        except Exception as error:
            messagebox.showerror("Visualisation error", str(error))

    def _render_figure(self, fig) -> None:
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

        if self.toolbar is not None:
            self.toolbar.destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()

    def _set_explanation(self, text: str) -> None:
        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("1.0", tk.END)
        self.explanation_box.insert(tk.END, text)
        self.explanation_box.configure(state="disabled")

    def export_png(self) -> None:
        if self.current_fig is None:
            messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            title="Save visualisation as PNG",
        )

        if path:
            self.export_service.export_figure_png(self.current_fig, path)
            messagebox.showinfo("Export complete", f"Saved visualisation to:\n{path}")

    def export_csv(self) -> None:
        if self.current_rho is None:
            messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            title="Save density matrix as CSV",
        )

        if path:
            self.export_service.export_density_matrix_csv(self.current_rho, path)
            messagebox.showinfo("Export complete", f"Saved density matrix to:\n{path}")

    def show_welcome_tutorial(self) -> None:
        messagebox.showinfo("Beginner tutorial", self.explanation_service.welcome_text())


def main() -> None:
    root = tk.Tk()
    QuantumStateVisualiserApp(root)
    root.mainloop()
