from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass(frozen=True)
class NoiseModel:
    name: str
    description: str


class NoiseService:
    """
    Applies educational density-matrix noise models.

    These models are intentionally simplified for visual learning.
    For exact physical simulation, integrate Qiskit Aer noise models later.

    SOLID:
    - Single Responsibility: noise transformations only.
    - Open/Closed: add a new noise function without touching plotting/UI code.
    """

    NO_NOISE = "No noise"
    DEPOLARIZING = "Depolarizing noise"
    DEPHASING = "Phase damping / dephasing"
    BIT_FLIP_MIXING = "Bit-flip style mixing"

    def models(self) -> List[str]:
        return [
            self.NO_NOISE,
            self.DEPOLARIZING,
            self.DEPHASING,
            self.BIT_FLIP_MIXING,
        ]

    def apply(self, rho: np.ndarray, noise_type: str, strength: float) -> np.ndarray:
        strength = max(0.0, min(1.0, float(strength)))
        size = rho.shape[0]

        if noise_type == self.NO_NOISE:
            return rho

        if noise_type == self.DEPOLARIZING:
            identity = np.eye(size, dtype=complex) / size
            return (1 - strength) * rho + strength * identity

        if noise_type == self.DEPHASING:
            noisy = rho.copy()
            for row in range(size):
                for col in range(size):
                    if row != col:
                        noisy[row, col] *= 1 - strength
            return noisy

        if noise_type == self.BIT_FLIP_MIXING:
            flipped = np.flipud(np.fliplr(rho))
            return (1 - strength) * rho + strength * flipped

        raise ValueError(f"Unknown noise type selected: {noise_type}")

    @staticmethod
    def dominant_state_from_density_matrix(rho: np.ndarray) -> np.ndarray:
        """
        Returns the dominant pure-state approximation of a density matrix.

        This is used only for the state-vector circle view when noise turns the
        exact state into a mixed density matrix.
        """
        eigenvalues, eigenvectors = np.linalg.eigh(rho)
        index = np.argmax(eigenvalues.real)
        vector = eigenvectors[:, index]

        non_zero = np.where(np.abs(vector) > 1e-9)[0]
        if len(non_zero) > 0:
            phase = np.angle(vector[non_zero[0]])
            vector = vector * np.exp(-1j * phase)

        return vector / np.linalg.norm(vector)
