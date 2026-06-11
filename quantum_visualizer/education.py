class ExplanationService:
    """
    Generates beginner-friendly and technical explanations.

    SOLID:
    - Single Responsibility: educational text only.
    """

    def explain(
        self,
        state_choice: str,
        visualisation_choice: str,
        noise_type: str,
        noise_strength: float,
        number_of_qubits: int,
        learning_mode: str,
        compare_ideal_noisy: bool,
    ) -> str:
        base = self._state_explanation(state_choice)

        if learning_mode == "Beginner mode":
            text = "Plain-language interpretation:\n" + base
        else:
            text = "Technical interpretation:\n" + base

        text += "\n\n" + self._visualisation_explanation(visualisation_choice)
        text += "\n\n" + self._adaptive_explanation(number_of_qubits)
        text += "\n\n" + self.traffic_light_noise(noise_type, noise_strength)
        text += "\n\nWhat should I notice?\n" + self.what_to_notice(state_choice, noise_type, noise_strength)

        if learning_mode == "Beginner mode":
            text += "\n\n" + self.beginner_dictionary()

        if compare_ideal_noisy and noise_type == "No noise":
            text += "\n\nNote: ideal-vs-noisy comparison becomes useful after selecting a noise type and increasing noise strength."

        return text

    @staticmethod
    def _state_explanation(state_choice: str) -> str:
        explanations = {
            "Single qubit |0>": (
                "This is the most basic one-qubit state. All probability is concentrated in |0>."
            ),
            "Single qubit |1>": (
                "This is the other basic one-qubit state. All probability is concentrated in |1>."
            ),
            "Single qubit |+> = (|0> + |1>) / √2": (
                "This state is an equal superposition. Both |0> and |1> have equal probability and the same phase."
            ),
            "Single qubit |-> = (|0> - |1>) / √2": (
                "This is an equal superposition with a negative phase on |1>. The probabilities look like |+>, but the phase structure differs."
            ),
            "Single qubit |+i> = (|0> + i|1>) / √2": (
                "This is an equal superposition with a +90 degree phase difference. It is useful for testing whether phase gauges are visible."
            ),
            "Single qubit |-i> = (|0> - i|1>) / √2": (
                "This is an equal superposition with a -90 degree phase difference. It helps compare opposite phase directions."
            ),
            "Product state |00>": (
                "This is a simple non-entangled state. Almost all probability is located at |00>. "
                "There are no important off-diagonal coherence terms."
            ),
            "Superposition 2 qubits = all basis states": (
                "This state spreads probability across all two-qubit basis states. "
                "Many off-diagonal circles appear in the density matrix because the basis states are coherently related."
            ),
            "Bell state |Φ+> = (|00> + |11>) / √2": (
                "This Bell state has probability only in |00> and |11>. "
                "In the density matrix, the off-diagonal circles between |00> and |11> show coherence, "
                "which is a visual sign of entanglement."
            ),

            "Bell state |Φ-> = (|00> - |11>) / √2": (
                "This Bell state has the same probabilities as |Φ+>, but the phase relationship between |00> and |11> is negative."
            ),
            "Bell state |Ψ+> = (|01> + |10>) / √2": (
                "This Bell state has probability in |01> and |10>. It shows entanglement between opposite two-qubit outcomes."
            ),
            "Bell state |Ψ-> = (|01> - |10>) / √2": (
                "This Bell state has probability in |01> and |10>, with a negative phase relationship between them."
            ),
            "Bell state phase π/4 = (|00> + exp(iπ/4)|11>) / √2": (
                "This Bell-like state uses a smaller phase difference. The phase gauge should sit between the real and imaginary examples."
            ),
            "Bell state with phase = (|00> + i|11>) / √2": (
                "This is similar to a Bell state, but it contains an imaginary phase. "
                "The circle notation shows this using the phase gauge line, while the Hinton view shows "
                "the real and imaginary density-matrix components."
            ),
            "GHZ state 3 qubits = (|000> + |111>) / √2": (
                "This is a 3-qubit entangled state. The most important values are at |000>, |111>, "
                "and the coherence between them."
            ),
            "W state 3 qubits = (|001> + |010> + |100>) / √3": (
                "This is a 3-qubit W state. It distributes probability over three single-excitation basis states, "
                "which creates a different entanglement pattern from the GHZ state."
            ),

            "Cluster state 3 qubits = (|000> + |011> + |101> - |110>) / 2": (
                "This 3-qubit cluster-style state distributes probability across four basis states and includes one negative phase."
            ),
            "Grover 2 qubits initial superposition": (
                "This is the starting point of Grover search: all possible answers have equal probability."
            ),
            "Grover 2 qubits after oracle target |11>": (
                "The oracle has marked |11> by flipping its phase. Probabilities may look unchanged, but phase has changed."
            ),
            "Grover 2 qubits after diffusion target |11>": (
                "The diffusion step amplifies the marked answer |11>, making it visually dominant."
            ),
            "Grover 2 qubits final target |11>": (
                "This is the final two-qubit Grover state where |11> dominates after amplitude amplification."
            ),
            "Grover 3 qubits initial superposition": (
                "This is the starting point for a 3-qubit Grover search: all eight possible answers are equally likely."
            ),
            "Grover 3 qubits after oracle target |111>": (
                "The oracle flips the phase of |111>. This is an intermediate state where phase matters before probability changes clearly."
            ),
            "Grover 3 qubits after diffusion target |111>": (
                "The first diffusion step starts amplifying |111>, showing the search mechanism more clearly."
            ),
            "Grover 3 qubits final target |111>": (
                "After Grover iterations, the target |111> becomes the most likely outcome."
            ),
            "Grover 3 qubits final target |101>": (
                "This Grover example marks |101>, allowing users to check whether the layout helps find a different target."
            ),
            "Grover 2 qubits = search target |11>": (
                "This is a small Grover search example. The marked answer is |11>. "
                "Grover's algorithm amplifies the marked state's amplitude, so |11> should visually dominate."
            ),
            "Grover 3 qubits = search target |111>": (
                "This is a 3-qubit Grover search example. The marked answer is |111>. "
                "After two Grover iterations, the target state becomes much more likely than the others."
            ),
            "Grover 3 qubits = search target |101>": (
                "This is a 3-qubit Grover search example with |101> as the marked answer. "
                "It helps compare whether the visualisations clearly show a different target state."
            ),
            "Superposition 3 qubits = all basis states": (
                "This state distributes probability evenly across all 8 basis states. "
                "The adaptive circle view hides numeric values to prevent visual overload."
            ),
            "Superposition 4 qubits = all basis states": (
                "This state distributes probability evenly across all 16 basis states. "
                "The adaptive circle view switches to a grouped 4-qubit layout to improve readability."
            ),
            "Sparse 4 qubits = |0000> + i|1111>": (
                "This sparse 4-qubit state highlights two dominant basis states. "
                "It is useful for testing whether the adaptive layout can keep important amplitudes readable."
            ),

            "Random state 2 qubits (fixed example)": (
                "This is a fixed random two-qubit example. It is useful for exploring less regular patterns."
            ),
            "Random state 3 qubits (fixed example)": (
                "This is a fixed random three-qubit example. It tests readability when many amplitudes and phases differ."
            ),
            "Random state 4 qubits (fixed example)": (
                "This is a fixed random four-qubit example. It is useful for stress-testing adaptive layout readability."
            ),
            "Custom state vector": (
                "This visualisation is generated from your custom state vector. "
                "The vector is automatically normalized before the density matrix is created."
            ),
        }
        return explanations.get(state_choice, "Look for the largest circles first. They show the most important outcomes or relationships.")

    @staticmethod
    def _visualisation_explanation(visualisation_choice: str) -> str:
        if visualisation_choice == "Hinton diagram (density matrix)":
            return (
                "Current view: Hinton diagram. This view is best for inspecting probabilities, "
                "coherence terms, and real/imaginary density-matrix structure."
            )
        if visualisation_choice == "Adaptive circle notation (state vector)":
            return (
                "Current view: adaptive circle notation. This view changes its layout and detail level "
                "as the number of qubits grows."
            )
        return "Current view: combined. This connects the state-vector view with the density-matrix view."

    @staticmethod
    def _adaptive_explanation(number_of_qubits: int) -> str:
        if number_of_qubits <= 2:
            return (
                "Adaptive behaviour: this is a small quantum system, so the app can show more detail. "
                "The circle view shows amplitudes, while the Hinton view shows density-matrix relationships."
            )
        if number_of_qubits == 3:
            return (
                "Adaptive behaviour: this is a 3-qubit system with 8 basis states. "
                "The app uses grouped layers and hides numeric values to reduce clutter."
            )
        if number_of_qubits == 4:
            return (
                "Adaptive behaviour: this is a 4-qubit system with 16 basis states. "
                "The app uses a grouped 4x4 layout and hides numeric values because full annotation becomes too dense."
            )
        return (
            "Adaptive behaviour: this system has many basis states. "
            "The app switches to a compact overview because quantum state spaces grow exponentially."
        )

    @staticmethod
    def traffic_light_noise(noise_type: str, noise_strength: float) -> str:
        if noise_type == "No noise" or noise_strength <= 0.001:
            return "🟢 No visible noise: the state is shown in its ideal form."
        if noise_strength < 0.25:
            return "🟡 Low noise: small changes may appear, especially in weak coherence terms."
        if noise_strength < 0.60:
            return "🟠 Medium noise: the state is becoming less clean and coherence may fade."
        return "🔴 High noise: the state may become strongly mixed and harder to interpret."

    @staticmethod
    def what_to_notice(state_choice: str, noise_type: str, noise_strength: float) -> str:
        notes: list[str] = []

        if state_choice.startswith("Single qubit"):
            notes.append("Notice how one-qubit examples make phase and probability easiest to inspect.")
            notes.append("Compare |+>, |->, |+i>, and |-i>: probabilities can stay the same while phase changes.")
        elif state_choice == "Product state |00>":
            notes.append("Notice that almost everything is concentrated in |00>. This is one clear outcome.")
            notes.append("In the Hinton view, there should be little or no off-diagonal structure.")
        elif state_choice.startswith("Bell state |Φ+") or state_choice.startswith("Bell state |Φ-") or "Bell state with phase" in state_choice or "Bell state phase" in state_choice:
            notes.append("Notice the two important outcomes: |00> and |11>. In plain words: both qubits agree.")
            notes.append("In the Hinton view, the off-diagonal circles between |00> and |11> show entanglement.")
        elif state_choice.startswith("Bell state |Ψ+") or state_choice.startswith("Bell state |Ψ-"):
            notes.append("Notice that |01> and |10> dominate instead of |00> and |11>.")
            notes.append("Compare Ψ+ and Ψ-: they have similar probabilities but different phase relationships.")
        elif "Grover" in state_choice:
            if "|11>" in state_choice:
                notes.append("Notice that the marked answer |11> is amplified and should dominate the circle view.")
            elif "|111>" in state_choice:
                notes.append("Notice that |111> is amplified compared with the other seven basis states.")
            elif "|101>" in state_choice:
                notes.append("Notice that |101> is amplified; this checks whether the layout helps users find a different target.")
            notes.append("In the Hinton view, the target state appears as a strong diagonal probability, with coherence terms showing state relationships.")
        elif "GHZ" in state_choice:
            notes.append("Notice that only |000> and |111> dominate. This is like a larger Bell pattern.")
            notes.append("This shows how entanglement patterns become harder to read as qubits increase.")
        elif "W state" in state_choice:
            notes.append("Notice that probability is spread across |001>, |010>, and |100>.")
        elif "Cluster" in state_choice:
            notes.append("Notice that several basis states are active and one of them has a negative phase.")
        elif "Random state" in state_choice:
            notes.append("Notice that random states are less structured; use them to test whether the visualization remains readable.")
        elif "Superposition" in state_choice:
            notes.append("Notice that probability is spread over many basis states.")
            notes.append("For 3 or 4 qubits, the app reduces detail automatically because showing every number would be unreadable.")
        elif "Sparse 4 qubits" in state_choice:
            notes.append("Notice that even though this is a 4-qubit system, only two basis states dominate.")
        else:
            notes.append("Look for the largest circles first. They show the most important outcomes or relationships.")

        if noise_type != "No noise" and noise_strength > 0:
            notes.append("After adding noise, check whether important off-diagonal Hinton circles shrink.")

        return "\n".join(f"• {note}" for note in notes)

    @staticmethod
    def beginner_dictionary() -> str:
        return (
            "Mini dictionary:\n"
            "• Basis state: one possible outcome, such as |00> or |111>.\n"
            "• Probability: how likely an outcome is after measurement.\n"
            "• Amplitude: a quantum value that creates probabilities.\n"
            "• Phase: the hidden direction of the quantum wave.\n"
            "• Coherence: a hidden relationship between possible outcomes.\n"
            "• Entanglement: qubits are connected so their outcomes depend on each other.\n"
            "• Noise: disturbance that weakens or changes the quantum state."
        )

    @staticmethod
    def welcome_text() -> str:
        return (
            "Welcome to the Quantum State Visualiser\n\n"
            "This tool helps you explore quantum states using two complementary visualisations:\n\n"
            "1. Hinton diagram (density matrix)\n"
            "   • Larger circles mean stronger matrix values.\n"
            "   • Diagonal circles usually represent probabilities.\n"
            "   • Off-diagonal circles show coherence relationships.\n\n"
            "2. Adaptive circle notation\n"
            "   • Every basis state, such as |00> or |111>, has its own circle.\n"
            "   • The inner circle radius represents |α|.\n"
            "   • The filled area represents probability |α|².\n"
            "   • The gauge line shows the complex phase.\n\n"
            "Recommended learning path:\n"
            "   1. Product state |00> — one simple outcome.\n"
            "   2. Superposition 2 qubits — several possible outcomes.\n"
            "   3. Bell state |Φ+> — basic entanglement.\n"
            "   4. Bell state with phase — introduces phase.\n"
            "   5. Grover 2 or 3 qubits — search/amplitude amplification.\n"
            "   6. Add noise slowly and compare ideal vs noisy state.\n\n"
            "Tip: start with 'Combined view' to compare both visualisations."
        )
