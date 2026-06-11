import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.patches import Circle, Rectangle

from quantum_visualizer.config import AdaptiveCircleConfigFactory, CircleViewConfig
from quantum_visualizer.layouts import BasisLayoutService
from quantum_visualizer.states import QuantumStateService


class HintonPlotter:
    """
    Draws circle-based Hinton diagrams for density matrices.

    The number displayed in a Hinton circle is the actual matrix value being
    plotted. For the real-part plot it is Re(rho[i,j]); for the imaginary-part
    plot it is Im(rho[i,j]). Diagonal values are probabilities. Off-diagonal
    values represent coherence relationships.
    """

    def plot_matrix(self, ax: Axes, matrix: np.ndarray, title: str, show_values: bool = False) -> None:
        values = np.asarray(matrix, dtype=float)
        size = values.shape[0]
        labels = QuantumStateService.basis_labels(size)

        max_value = float(np.max(np.abs(values))) if np.max(np.abs(values)) > 0 else 1.0

        ax.clear()
        ax.set_title(title, fontsize=12, pad=8)
        ax.set_aspect("equal")
        ax.set_xlim(-0.5, size - 0.5)
        ax.set_ylim(size - 0.5, -0.5)
        ax.set_facecolor("#E8EDF3")

        ax.set_xticks(range(size))
        ax.set_yticks(range(size))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels)

        ax.set_xticks(np.arange(-0.5, size, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, size, 1), minor=True)
        ax.grid(which="minor", linewidth=0.5, alpha=0.35, color="#94A3B8")

        hover_items: list[dict] = []
        adaptive_show_values = show_values and size <= 8

        for row in range(size):
            for col in range(size):
                value = float(values[row, col])
                if abs(value) < 1e-12:
                    continue

                magnitude = abs(value) / max_value
                radius = np.sqrt(magnitude) * 0.43
                color = "#FFFFFF" if value >= 0 else "#111827"

                circle = Circle(
                    (col, row),
                    radius,
                    facecolor=color,
                    edgecolor="#1F2937",
                    linewidth=1.15,
                    zorder=3,
                )
                ax.add_patch(circle)

                value_type = "measurement probability" if row == col else "coherence relationship"
                sign_text = "positive" if value >= 0 else "negative"
                hover_items.append(
                    {
                        "type": "hinton",
                        "x": float(col),
                        "y": float(row),
                        "radius": float(max(radius, 0.18)),
                        "text": (
                            f"Hinton value rho[{labels[row]}, {labels[col]}] = {value:.4f}. "
                            f"This is a {sign_text} {value_type}. "
                            "Circle size shows absolute magnitude; colour shows sign."
                        ),
                    }
                )

                if adaptive_show_values:
                    text_color = "#111827" if value >= 0 else "#FFFFFF"
                    ax.text(
                        col,
                        row,
                        f"{value:.2f}",
                        ha="center",
                        va="center",
                        fontsize=8,
                        color=text_color,
                        zorder=4,
                    )

        ax._qv_hover_items = hover_items


class AdaptiveCirclePlotter:
    """
    Draws adaptive circle notation.

    Pure state mode:
    - outer circle = basis state container
    - blue radius = |alpha|
    - blue area = |alpha|^2 probability
    - gauge line = phase

    Noisy/mixed mode:
    - blue radius/area still comes from the density-matrix diagonal probability
    - phase gauge is shown as an approximate dominant-state phase, because users
      requested phase to remain visible. The Hinton real/imaginary plots remain
      the more faithful representation of coherence under noise.
    """

    def __init__(self) -> None:
        self._layout_service = BasisLayoutService()
        self._config_factory = AdaptiveCircleConfigFactory()

    def plot_state(
        self,
        ax: Axes,
        state_vector: np.ndarray,
        title: str,
        show_values: bool = False,
        show_phase: bool = True,
    ) -> None:
        vector = QuantumStateService.normalize(state_vector)
        self._plot_vector_like(
            ax=ax,
            vector=vector,
            title=title,
            show_values=show_values,
            show_phase=True,
            mode="amplitude",
        )

    def plot_density_probabilities_with_phase(
        self,
        ax: Axes,
        rho: np.ndarray,
        title: str,
        show_values: bool = False,
    ) -> None:
        probabilities = np.real(np.diag(rho)).astype(float)
        probabilities = np.maximum(probabilities, 0.0)
        total = float(np.sum(probabilities))
        if total > 0:
            probabilities = probabilities / total

        phases = self._dominant_state_phases(rho)
        vector_like = np.sqrt(probabilities).astype(complex) * np.exp(1j * phases)

        self._plot_vector_like(
            ax=ax,
            vector=vector_like,
            title=title,
            show_values=show_values,
            show_phase=True,
            mode="density_probability_phase",
        )

    @staticmethod
    def _dominant_state_phases(rho: np.ndarray) -> np.ndarray:
        """
        Returns approximate phases from the dominant eigenvector.

        This is intentionally labelled as approximate in the UI. A mixed state does
        not have one unique phase per basis state, but this gives an educational
        phase hint while the density-matrix Hinton view carries the exact complex
        information.
        """
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(rho)
            vector = eigenvectors[:, int(np.argmax(eigenvalues.real))]
            non_zero = np.where(np.abs(vector) > 1e-9)[0]
            if len(non_zero) > 0:
                vector = vector * np.exp(-1j * np.angle(vector[non_zero[0]]))
            return np.angle(vector)
        except Exception:
            return np.zeros(rho.shape[0], dtype=float)

    def _plot_vector_like(
        self,
        ax: Axes,
        vector: np.ndarray,
        title: str,
        show_values: bool,
        show_phase: bool,
        mode: str,
    ) -> None:
        size = len(vector)
        number_of_qubits = int(np.log2(size))
        labels = QuantumStateService.basis_labels(size)
        config = self._config_factory.for_qubits(number_of_qubits)

        ax.clear()
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=13, pad=8)

        self._draw_group_backgrounds(ax, number_of_qubits)

        indices = self._visible_indices(vector, config)
        xs: list[float] = []
        ys: list[float] = []
        hover_items: list[dict] = []

        for index in indices:
            amplitude = vector[index]
            x, y = self._layout_service.position(index, number_of_qubits)
            xs.append(x)
            ys.append(y)
            self._draw_single_circle(ax, x, y, amplitude, labels[index], config, show_values, show_phase, mode)

            magnitude = float(abs(amplitude))
            probability = magnitude ** 2
            phase = float(np.angle(amplitude)) if magnitude > 1e-12 else 0.0
            if mode == "density_probability_phase":
                text = (
                    f"{labels[index]} probability from density matrix diagonal = {probability:.4f}. "
                    f"Phase gauge = {phase:.4f} rad from dominant-state approximation. "
                    "Use Hinton real/imaginary parts for exact noisy coherence."
                )
            else:
                text = (
                    f"{labels[index]} amplitude |alpha| = {magnitude:.4f}, "
                    f"probability |alpha|² = {probability:.4f}, phase = {phase:.4f} rad."
                )

            hover_items.append(
                {
                    "type": "circle",
                    "x": float(x),
                    "y": float(y),
                    "radius": float(max(config.base_radius, 0.2)),
                    "text": text,
                }
            )

        ax._qv_hover_items = hover_items

        if not xs:
            ax.text(0, 0, "No significant amplitudes to display.", ha="center", va="center", fontsize=10)
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            return

        margin = 1.15 if number_of_qubits <= 2 else 1.0
        ax.set_xlim(min(xs) - margin, max(xs) + margin)
        ax.set_ylim(min(ys) - margin - 0.25, max(ys) + margin + 0.35)

        probabilities = np.abs(vector) ** 2
        significant_count = int(np.sum(probabilities > config.probability_threshold))
        shown_count = len(indices)
        mode_label = "probabilities + approximate phase" if mode == "density_probability_phase" else "amplitudes + phase"

        note = (
            f"{number_of_qubits} qubits | {size} basis states | layout: {config.layout} | "
            f"shown: {shown_count}/{significant_count} significant | {mode_label}"
        )
        ax.text(0, min(ys) - margin - 0.75, note, ha="center", fontsize=8, color="#64748B")

    def _visible_indices(self, vector: np.ndarray, config: CircleViewConfig) -> list[int]:
        probabilities = np.abs(vector) ** 2
        all_indices = list(range(len(vector)))

        if config.max_visible_states is None:
            return all_indices

        significant = [i for i in all_indices if probabilities[i] >= config.probability_threshold]
        if len(significant) <= config.max_visible_states:
            return significant

        sorted_indices = sorted(significant, key=lambda i: probabilities[i], reverse=True)
        return sorted(sorted_indices[: config.max_visible_states])

    def _draw_single_circle(
        self,
        ax: Axes,
        x: float,
        y: float,
        amplitude: complex,
        label: str,
        config: CircleViewConfig,
        show_values: bool,
        show_phase: bool,
        mode: str,
    ) -> None:
        base_radius = config.base_radius
        magnitude = float(abs(amplitude))
        probability = magnitude ** 2
        phase = float(np.angle(amplitude)) if magnitude > 1e-12 else 0.0
        is_tiny = probability < config.probability_threshold

        if config.hide_tiny and is_tiny:
            return

        edge_alpha = 0.35 if is_tiny else 1.0
        outer = Circle(
            (x, y),
            base_radius,
            facecolor="#FFFFFF",
            edgecolor=(0, 0, 0, edge_alpha),
            linewidth=1.0,
            zorder=2,
        )
        ax.add_patch(outer)

        if magnitude > 1e-12 and not is_tiny:
            inner = Circle(
                (x, y),
                base_radius * magnitude,
                facecolor="#3B82F6",
                edgecolor="#1E293B",
                linewidth=0.8,
                alpha=0.86,
                zorder=3,
            )
            ax.add_patch(inner)
            if show_phase:
                self._draw_phase_gauge(ax, x, y, base_radius * magnitude, phase)
        elif magnitude > 1e-12:
            tiny = Circle(
                (x, y),
                max(base_radius * 0.10, base_radius * magnitude),
                facecolor="#3B82F6",
                edgecolor="none",
                alpha=config.alpha_for_tiny,
                zorder=3,
            )
            ax.add_patch(tiny)
        else:
            small_dot = Circle(
                (x, y),
                base_radius * 0.04,
                facecolor="#CBD5E1",
                edgecolor="none",
                alpha=0.5,
                zorder=3,
            )
            ax.add_patch(small_dot)

        if config.show_labels:
            ax.text(x, y - base_radius - 0.12, label, ha="center", va="top", fontsize=config.font_size)

        adaptive_show_values = show_values and config.show_values_allowed
        if adaptive_show_values:
            if mode == "density_probability_phase":
                value_text = f"p={probability:.2f}\nφ≈{phase:.2f}"
            else:
                value_text = f"|α|={magnitude:.2f}\np={probability:.2f}\nφ={phase:.2f}"
            ax.text(
                x,
                y + base_radius + 0.12,
                value_text,
                ha="center",
                va="bottom",
                fontsize=max(6, config.font_size - 1),
                color="#0F172A",
            )

    @staticmethod
    def _draw_phase_gauge(ax: Axes, x: float, y: float, radius: float, phase: float) -> None:
        dx = radius * np.sin(phase)
        dy = radius * np.cos(phase)
        ax.plot([x, x], [y, y + radius], color="#CBD5E1", linewidth=0.6, linestyle="--", zorder=4)
        ax.plot([x, x + dx], [y, y + dy], color="#0F172A", linewidth=1.15, zorder=5)

    @staticmethod
    def _draw_group_backgrounds(ax: Axes, number_of_qubits: int) -> None:
        if number_of_qubits == 3:
            for x_center, label in [(-2.2, "q1 = 0"), (2.2, "q1 = 1")]:
                rect = Rectangle(
                    (x_center - 1.35, -1.35),
                    2.7,
                    2.7,
                    facecolor="#F8FAFC",
                    edgecolor="#CBD5E1",
                    linewidth=1.0,
                    zorder=0,
                )
                ax.add_patch(rect)
                ax.text(x_center, 1.68, label, ha="center", va="center", fontsize=9, color="#64748B")

        if number_of_qubits == 4:
            group_centers = {
                "00": (-1.175, 1.175),
                "01": (1.175, 1.175),
                "10": (-1.175, -1.175),
                "11": (1.175, -1.175),
            }
            for group, (x, y) in group_centers.items():
                rect = Rectangle(
                    (x - 0.95, y - 0.95),
                    1.9,
                    1.9,
                    facecolor="#F8FAFC",
                    edgecolor="#CBD5E1",
                    linewidth=1.0,
                    zorder=0,
                )
                ax.add_patch(rect)
                ax.text(x, y + 1.10, f"q1q2={group}", ha="center", va="center", fontsize=8, color="#64748B")


class LegendPlotter:
    def __init__(self) -> None:
        self._circle_plotter = AdaptiveCirclePlotter()

    def plot_circle_legend(self, ax: Axes) -> None:
        ax.clear()
        ax.set_title("Circle notation legend", fontsize=11)
        ax.set_aspect("equal")
        ax.axis("off")

        config = CircleViewConfig(
            layout="legend",
            base_radius=0.42,
            font_size=8,
            show_labels=True,
            show_values_allowed=False,
            probability_threshold=0.0,
            hide_tiny=False,
            alpha_for_tiny=0.2,
        )

        examples = [
            (0.0, 0.0, 1 / np.sqrt(2), "positive real"),
            (1.55, 0.0, 1j / np.sqrt(2), "+90° phase"),
            (3.10, 0.0, -1 / np.sqrt(2), "180° phase"),
        ]

        for x, y, amp, label in examples:
            self._circle_plotter._draw_single_circle(
                ax, x, y, amp, label, config, show_values=False, show_phase=True, mode="amplitude"
            )

        ax.text(1.55, -1.25, "Blue area = probability |α|²", ha="center", fontsize=8)
        ax.text(1.55, -1.55, "Gauge line = phase φ", ha="center", fontsize=8)
        ax.text(1.55, -1.85, "Noisy view: probability exact; phase ≈ dominant-state hint", ha="center", fontsize=8, color="#64748B")
        ax.set_xlim(-0.8, 3.9)
        ax.set_ylim(-2.15, 1.1)
        ax._qv_hover_items = []


class FigureFactory:
    def __init__(self) -> None:
        self.hinton = HintonPlotter()
        self.circle = AdaptiveCirclePlotter()
        self.legend = LegendPlotter()

    def create_hinton(self, rho: np.ndarray, selected_part: str, show_values: bool) -> Figure:
        if selected_part == "Real part only":
            fig = Figure(figsize=(6.5, 6), dpi=100)
            ax = fig.add_subplot(111)
            self.hinton.plot_matrix(ax, rho.real, "Real part of density matrix", show_values)
            fig.tight_layout()
            return fig

        if selected_part == "Imaginary part only":
            fig = Figure(figsize=(6.5, 6), dpi=100)
            ax = fig.add_subplot(111)
            self.hinton.plot_matrix(ax, rho.imag, "Imaginary part of density matrix", show_values)
            fig.tight_layout()
            return fig

        fig = Figure(figsize=(11, 5.5), dpi=100)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        self.hinton.plot_matrix(ax1, rho.real, "Real part", show_values)
        self.hinton.plot_matrix(ax2, rho.imag, "Imaginary part", show_values)
        fig.suptitle("Complex density matrix Hinton diagram", fontsize=14)
        fig.tight_layout()
        return fig

    def create_circle(
        self,
        state_vector: np.ndarray,
        rho: np.ndarray | None,
        show_values: bool,
        show_phase: bool,
        use_density_probabilities: bool,
    ) -> Figure:
        fig = Figure(figsize=(10.5, 6.6), dpi=100)
        ax_state = fig.add_subplot(121)
        ax_legend = fig.add_subplot(122)

        if use_density_probabilities and rho is not None:
            self.circle.plot_density_probabilities_with_phase(ax_state, rho, "Noisy circle notation: probability + phase hint", show_values)
        else:
            self.circle.plot_state(ax_state, state_vector, "Adaptive circle notation", show_values, show_phase)

        self.legend.plot_circle_legend(ax_legend)
        fig.suptitle("Adaptive circle notation", fontsize=14)
        fig.tight_layout()
        return fig

    def create_combined(
        self,
        rho: np.ndarray,
        state_vector: np.ndarray,
        selected_part: str,
        show_values: bool,
        show_phase: bool,
        use_density_probabilities: bool,
    ) -> Figure:
        fig = Figure(figsize=(13.4, 7.3), dpi=100)
        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)

        self.hinton.plot_matrix(ax1, rho.real, "Density matrix: real part", show_values)
        self.hinton.plot_matrix(ax2, rho.imag, "Density matrix: imaginary part", show_values)

        if use_density_probabilities:
            self.circle.plot_density_probabilities_with_phase(ax3, rho, "Circle notation: probability + phase hint", show_values)
        else:
            self.circle.plot_state(ax3, state_vector, "Adaptive circle notation", show_values, show_phase)

        self.legend.plot_circle_legend(ax4)
        fig.suptitle("Combined Hinton + adaptive circle notation", fontsize=14)
        fig.tight_layout()
        return fig

    def create_ideal_vs_noisy(
        self,
        ideal_rho: np.ndarray,
        noisy_rho: np.ndarray,
        ideal_state_vector: np.ndarray,
        show_values: bool,
        show_phase: bool,
    ) -> Figure:
        fig = Figure(figsize=(13.4, 7.3), dpi=100)
        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)

        self.hinton.plot_matrix(ax1, ideal_rho.real, "Ideal density matrix: real part", show_values)
        self.hinton.plot_matrix(ax2, noisy_rho.real, "Noisy density matrix: real part", show_values)
        self.circle.plot_state(ax3, ideal_state_vector, "Ideal circle notation", show_values, show_phase)
        self.circle.plot_density_probabilities_with_phase(ax4, noisy_rho, "Noisy circle notation: probability + phase hint", show_values)

        fig.suptitle("Ideal state vs noisy state comparison", fontsize=14)
        fig.tight_layout()
        return fig
