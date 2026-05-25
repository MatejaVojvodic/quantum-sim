import csv
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure


class ExportService:
    """Handles exporting visualisations and density matrices."""

    @staticmethod
    def export_figure_png(figure: Figure, path: str) -> None:
        figure.savefig(path, dpi=200)

    @staticmethod
    def export_density_matrix_csv(rho: np.ndarray, path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["row", "column", "real", "imaginary", "complex"])
            for row in range(rho.shape[0]):
                for col in range(rho.shape[1]):
                    value = rho[row, col]
                    writer.writerow([row, col, value.real, value.imag, str(value)])
