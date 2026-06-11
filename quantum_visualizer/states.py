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
        # Single-qubit learning states.
        self.register(
            "Single qubit |0>",
            "A basic one-qubit state with probability concentrated in |0>.",
            lambda: np.array([1, 0], dtype=complex),
        )

        self.register(
            "Single qubit |1>",
            "A basic one-qubit state with probability concentrated in |1>.",
            lambda: np.array([0, 1], dtype=complex),
        )

        self.register(
            "Single qubit |+> = (|0> + |1>) / √2",
            "A one-qubit equal superposition with positive real amplitudes.",
            lambda: np.array([1, 1], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "Single qubit |-> = (|0> - |1>) / √2",
            "A one-qubit equal superposition with a negative phase on |1>.",
            lambda: np.array([1, -1], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "Single qubit |+i> = (|0> + i|1>) / √2",
            "A one-qubit equal superposition with a +90 degree phase on |1>.",
            lambda: np.array([1, 1j], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "Single qubit |-i> = (|0> - i|1>) / √2",
            "A one-qubit equal superposition with a -90 degree phase on |1>.",
            lambda: np.array([1, -1j], dtype=complex) / np.sqrt(2),
        )

        # Two-qubit states.
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
            "Bell state |Φ-> = (|00> - |11>) / √2",
            "A Bell state with a negative phase relationship between |00> and |11>.",
            lambda: np.array([1, 0, 0, -1], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "Bell state |Ψ+> = (|01> + |10>) / √2",
            "A Bell state where the important outcomes are |01> and |10>.",
            lambda: np.array([0, 1, 1, 0], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "Bell state |Ψ-> = (|01> - |10>) / √2",
            "A Bell state with a negative phase relationship between |01> and |10>.",
            lambda: np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "Bell state with phase = (|00> + i|11>) / √2",
            "A Bell-like state with a complex phase difference.",
            lambda: np.array([1, 0, 0, 1j], dtype=complex) / np.sqrt(2),
        )

        self.register(
            "Bell state phase π/4 = (|00> + exp(iπ/4)|11>) / √2",
            "A Bell-like state with a smaller phase offset, useful for testing phase gauges.",
            lambda: np.array([1, 0, 0, np.exp(1j * np.pi / 4)], dtype=complex) / np.sqrt(2),
        )

        # Three-qubit states.
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
            "Cluster state 3 qubits = (|000> + |011> + |101> - |110>) / 2",
            "A three-qubit cluster-style state with a negative phase on one basis state.",
            lambda: np.array([1, 0, 0, 1, 0, 1, -1, 0], dtype=complex) / 2,
        )

        self.register(
            "Superposition 3 qubits = all basis states",
            "A three-qubit state where all eight outcomes have equal probability.",
            lambda: np.ones(8, dtype=complex) / np.sqrt(8),
        )

        # Grover intermediate states.
        self.register(
            "Grover 2 qubits initial superposition",
            "The initial equal superposition before the Grover oracle is applied.",
            lambda: self._grover_state(number_of_qubits=2, marked_index=3, stage="initial"),
        )

        self.register(
            "Grover 2 qubits after oracle target |11>",
            "The phase oracle has flipped the marked answer |11>.",
            lambda: self._grover_state(number_of_qubits=2, marked_index=3, stage="oracle"),
        )

        self.register(
            "Grover 2 qubits after diffusion target |11>",
            "After diffusion, amplitude amplification makes the marked state |11> dominant.",
            lambda: self._grover_state(number_of_qubits=2, marked_index=3, stage="diffusion"),
        )

        self.register(
            "Grover 2 qubits final target |11>",
            "A small Grover search example where the marked state |11> becomes dominant.",
            lambda: self._grover_search_state(number_of_qubits=2, marked_index=3, iterations=1),
        )

        self.register(
            "Grover 3 qubits initial superposition",
            "The initial equal superposition over all eight possible answers.",
            lambda: self._grover_state(number_of_qubits=3, marked_index=7, stage="initial"),
        )

        self.register(
            "Grover 3 qubits after oracle target |111>",
            "The oracle flips the phase of the marked answer |111>.",
            lambda: self._grover_state(number_of_qubits=3, marked_index=7, stage="oracle"),
        )

        self.register(
            "Grover 3 qubits after diffusion target |111>",
            "The first diffusion step starts increasing the marked answer |111>.",
            lambda: self._grover_state(number_of_qubits=3, marked_index=7, stage="diffusion"),
        )

        self.register(
            "Grover 3 qubits final target |111>",
            "After two Grover iterations, |111> becomes the most likely outcome.",
            lambda: self._grover_search_state(number_of_qubits=3, marked_index=7, iterations=2),
        )

        self.register(
            "Grover 3 qubits final target |101>",
            "A three-qubit Grover search example with a different marked state.",
            lambda: self._grover_search_state(number_of_qubits=3, marked_index=5, iterations=2),
        )

        # Compatibility names used by earlier quick buttons.
        self.register(
            "Grover 2 qubits = search target |11>",
            "A small Grover search example. After one Grover iteration, the marked state |11> becomes dominant.",
            lambda: self._grover_search_state(number_of_qubits=2, marked_index=3, iterations=1),
        )

        self.register(
            "Grover 3 qubits = search target |111>",
            "A three-qubit Grover search example. After two iterations, |111> becomes the most likely outcome.",
            lambda: self._grover_search_state(number_of_qubits=3, marked_index=7, iterations=2),
        )

        self.register(
            "Grover 3 qubits = search target |101>",
            "A three-qubit Grover search example with a different marked state, useful for comparing search patterns.",
            lambda: self._grover_search_state(number_of_qubits=3, marked_index=5, iterations=2),
        )

        # Four-qubit states.
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

        # Deterministic random states for exploration.
        self.register(
            "Random state 2 qubits (fixed example)",
            "A deterministic random two-qubit state for exploratory visualisation.",
            lambda: self._random_state(number_of_qubits=2, seed=22),
        )

        self.register(
            "Random state 3 qubits (fixed example)",
            "A deterministic random three-qubit state for exploratory visualisation.",
            lambda: self._random_state(number_of_qubits=3, seed=33),
        )

        self.register(
            "Random state 4 qubits (fixed example)",
            "A deterministic random four-qubit state for exploratory visualisation.",
            lambda: self._random_state(number_of_qubits=4, seed=44),
        )

    @staticmethod
    def _grover_state(number_of_qubits: int, marked_index: int, stage: str) -> np.ndarray:
        size = 2 ** number_of_qubits
        state = np.ones(size, dtype=complex) / np.sqrt(size)

        if stage == "initial":
            return QuantumStateService.normalize(state)

        # Oracle: flip the phase of the marked state.
        state[marked_index] *= -1

        if stage == "oracle":
            return QuantumStateService.normalize(state)

        if stage == "diffusion":
            average = np.mean(state)
            state = 2 * average - state
            return QuantumStateService.normalize(state)

        raise ValueError(f"Unknown Grover stage: {stage}")

    @staticmethod
    def _grover_search_state(number_of_qubits: int, marked_index: int, iterations: int) -> np.ndarray:
        """
        Creates a small educational Grover-search state vector.

        The state starts in an equal superposition, applies a phase oracle to the
        marked basis state, and then applies the standard diffusion operator.
        This is not a full circuit renderer; it provides the resulting state so
        users can inspect Grover-style amplitude amplification visually.
        """
        size = 2 ** number_of_qubits
        if marked_index < 0 or marked_index >= size:
            raise ValueError("Marked Grover index is outside the basis-state range.")

        state = np.ones(size, dtype=complex) / np.sqrt(size)

        for _ in range(iterations):
            state[marked_index] *= -1
            average = np.mean(state)
            state = 2 * average - state

        return QuantumStateService.normalize(state)

    @staticmethod
    def _sparse_four_qubit_state() -> np.ndarray:
        vector = np.zeros(16, dtype=complex)
        vector[0] = 1
        vector[15] = 1j
        return vector / np.sqrt(2)

    @staticmethod
    def _random_state(number_of_qubits: int, seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        size = 2 ** number_of_qubits
        vector = rng.normal(size=size) + 1j * rng.normal(size=size)
        return QuantumStateService.normalize(vector)

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
