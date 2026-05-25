from dataclasses import dataclass


@dataclass(frozen=True)
class CircleViewConfig:
    layout: str
    base_radius: float
    font_size: int
    show_labels: bool
    show_values_allowed: bool
    probability_threshold: float
    hide_tiny: bool
    alpha_for_tiny: float
    max_visible_states: int | None = None


class AdaptiveCircleConfigFactory:
    """
    Decides how detailed the circle notation should be.

    This is the core adaptive visualisation policy.
    """

    def for_qubits(self, number_of_qubits: int) -> CircleViewConfig:
        if number_of_qubits <= 1:
            return CircleViewConfig(
                layout="line",
                base_radius=0.72,
                font_size=10,
                show_labels=True,
                show_values_allowed=True,
                probability_threshold=0.0,
                hide_tiny=False,
                alpha_for_tiny=0.20,
            )

        if number_of_qubits == 2:
            return CircleViewConfig(
                layout="square",
                base_radius=0.62,
                font_size=9,
                show_labels=True,
                show_values_allowed=True,
                probability_threshold=0.0,
                hide_tiny=False,
                alpha_for_tiny=0.20,
            )

        if number_of_qubits == 3:
            return CircleViewConfig(
                layout="layered",
                base_radius=0.46,
                font_size=8,
                show_labels=True,
                show_values_allowed=False,
                probability_threshold=0.005,
                hide_tiny=False,
                alpha_for_tiny=0.16,
            )

        if number_of_qubits == 4:
            return CircleViewConfig(
                layout="grouped_grid",
                base_radius=0.33,
                font_size=7,
                show_labels=True,
                show_values_allowed=False,
                probability_threshold=0.01,
                hide_tiny=False,
                alpha_for_tiny=0.10,
            )

        return CircleViewConfig(
            layout="top_amplitudes",
            base_radius=0.30,
            font_size=7,
            show_labels=True,
            show_values_allowed=False,
            probability_threshold=0.015,
            hide_tiny=True,
            alpha_for_tiny=0.08,
            max_visible_states=24,
        )
