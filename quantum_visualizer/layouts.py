import numpy as np


class BasisLayoutService:
    """
    Calculates basis-state positions for adaptive circle notation.

    SOLID:
    - Single Responsibility: layout/positioning only.
    """

    @staticmethod
    def index_to_bits(index: int, number_of_qubits: int) -> str:
        return f"{index:0{number_of_qubits}b}"

    def position(self, index: int, number_of_qubits: int) -> tuple[float, float]:
        bits = self.index_to_bits(index, number_of_qubits)

        if number_of_qubits == 1:
            return (-1.35 if bits == "0" else 1.35), 0.0

        if number_of_qubits == 2:
            row = int(bits[0])
            col = int(bits[1])
            spacing = 1.9
            return (col - 0.5) * spacing, (0.5 - row) * spacing

        if number_of_qubits == 3:
            layer = int(bits[0])
            row = int(bits[1])
            col = int(bits[2])
            layer_offset_x = -2.2 if layer == 0 else 2.2
            spacing = 1.25
            return layer_offset_x + (col - 0.5) * spacing, (0.5 - row) * spacing

        if number_of_qubits == 4:
            group_row = int(bits[0])
            group_col = int(bits[1])
            local_row = int(bits[2])
            local_col = int(bits[3])

            group_spacing = 2.35
            local_spacing = 0.78

            x = (group_col - 0.5) * group_spacing + (local_col - 0.5) * local_spacing
            y = (0.5 - group_row) * group_spacing + (0.5 - local_row) * local_spacing
            return x, y

        total = 2 ** number_of_qubits
        cols = int(np.ceil(np.sqrt(total)))
        row = index // cols
        col = index % cols
        spacing = 0.82
        x = (col - (cols - 1) / 2) * spacing
        y = -row * spacing
        return x, y
