from dataclasses import dataclass
from typing import Callable, Dict, List

import numpy as np


@dataclass(frozen=True)
class QuantumStatePreset:
    """Represents one selectable example quantum state."""
    name: str
    description: str
    factory: Callable[[], np.ndarray]


class QuantumStateService:
    """
    Responsible only for creating and validating quantum state vectors.

    SOLID:
    - Single Responsibility: state creation/validation only.
    - Open/Closed: add new presets without changing the UI.
    """

    def __init__(self) -> None:
        self._presets: Dict[str, QuantumStatePreset] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(
            "Product state |00>",
            "A simple two-qubit state with one clear outcome.",
            lambda: np.array([1, 0, 0, 0], dtype=complex),
        )

        self.register(
            "Superposition 2 qubits = all basis states",
            "A two-qubit state where all four outcomes have equal probability.",
            lambda: np.array([1, 1, 1, 1], dtype=complex) / 2,
        )

        self.register(
            "Bell state |Φ+> = (|00> + |11>) / √2",
            "A two-qubit entangled state with outcomes |00> and |11>.",
            lambda: np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "Bell state with phase = (|00> + i|11>) / √2",
            "A Bell-like state with a complex phase difference.",
            lambda: np.array([1, 0, 0, 1j], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "GHZ state 3 qubits = (|000> + |111>) / √2",
            "A three-qubit entangled state similar to a larger Bell state.",
            lambda: np.array([1, 0, 0, 0, 0, 0, 0, 1], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "W state 3 qubits = (|001> + |010> + |100>) / √3",
            "A three-qubit entangled state spread over three single-excitation outcomes.",
            lambda: np.array([0, 1, 1, 0, 1, 0, 0, 0], dtype=complex) / np.sqrt(3),
        )

        self.register(
            "Superposition 3 qubits = all basis states",
            "A three-qubit state where all eight outcomes have equal probability.",
            lambda: np.ones(8, dtype=complex) / np.sqrt(8),
        )

        self.register(
            "Superposition 4 qubits = all basis states",
            "A four-qubit state where all sixteen outcomes have equal probability.",
            lambda: np.ones(16, dtype=complex) / np.sqrt(16),
        )

        self.register(
            "Sparse 4 qubits = |0000> + i|1111>",
            "A sparse four-qubit state with only two dominant outcomes.",
            self._sparse_four_qubit_state,
        )

    @staticmethod
    def _sparse_four_qubit_state() -> np.ndarray:
        vector = np.zeros(16, dtype=complex)
        vector[0] = 1
        vector[15] = 1j
        return vector / np.sqrt(2)

    def register(self, name: str, description: str, factory: Callable[[], np.ndarray]) -> None:
        self._presets[name] = QuantumStatePreset(name, description, factory)

    def preset_names(self) -> List[str]:
        return list(self._presets.keys())

    def create_preset(self, name: str) -> np.ndarray:
        if name not in self._presets:
            raise ValueError(f"Unknown quantum state preset: {name}")
        return self.normalize(self._presets[name].factory())

    @staticmethod
    def normalize(state_vector: np.ndarray) -> np.ndarray:
        vector = np.asarray(state_vector, dtype=complex).reshape(-1)
        norm = np.linalg.norm(vector)

        if norm == 0:
            raise ValueError("State vector cannot be zero.")

        size = len(vector)
        qubits = int(np.log2(size))

        if 2 ** qubits != size:
            raise ValueError("State vector length must be a power of 2, for example 2, 4, 8, or 16.")

        return vector / norm

    @staticmethod
    def ket_to_density_matrix(state_vector: np.ndarray) -> np.ndarray:
        vector = QuantumStateService.normalize(state_vector)
        return np.outer(vector, vector.conj())

    @staticmethod
    def number_of_qubits(state_vector: np.ndarray) -> int:
        return int(np.log2(len(state_vector)))

    @staticmethod
    def basis_labels(size: int) -> List[str]:
        qubits = int(np.log2(size))

        if 2 ** qubits != size:
            return [str(i) for i in range(size)]

        return [f"|{i:0{qubits}b}>" for i in range(size)]
