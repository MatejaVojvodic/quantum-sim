# import ast
# import csv
# import tkinter as tk
# from tkinter import ttk, messagebox, filedialog

# import numpy as np
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from matplotlib.figure import Figure
# from matplotlib.patches import Circle

# def ket_to_density_matrix(state_vector):
#     state_vector = np.asarray(state_vector, dtype=complex)
#     norm = np.linalg.norm(state_vector)

#     if norm == 0:
#         raise ValueError("State vector cannot be zero.")

#     state_vector = state_vector / norm
#     return np.outer(state_vector, state_vector.conj())


# def basis_labels(size):
#     qubits = int(np.log2(size))

#     if 2 ** qubits != size:
#         return [str(i) for i in range(size)]

#     return [f"|{i:0{qubits}b}>" for i in range(size)]

# def create_state_vector(choice):
#     if choice == "Bell state |Φ+> = (|00> + |11>) / √2":
#         return np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

#     if choice == "Bell state with phase = (|00> + i|11>) / √2":
#         return np.array([1, 0, 0, 1j], dtype=complex) / np.sqrt(2)

#     if choice == "Product state |00>":
#         return np.array([1, 0, 0, 0], dtype=complex)

#     if choice == "Superposition = (|00> + |01> + |10> + |11>) / 2":
#         return np.array([1, 1, 1, 1], dtype=complex) / 2

#     if choice == "GHZ state 3 qubits = (|000> + |111>) / √2":
#         return np.array([1, 0, 0, 0, 0, 0, 0, 1], dtype=complex) / np.sqrt(2)

#     raise ValueError("Unknown state selected.")


# def safe_eval_complex_expression(expression):
#     """
#     Evaluate simple user input safely.
#     Allows: sqrt, pi, e, j, i, complex numbers, +, -, *, /, **, brackets.
#     Example input: 1/sqrt(2), 0, 0, i/sqrt(2)
#     """
#     expression = expression.replace("i", "j")
#     allowed_names = {
#         "sqrt": np.sqrt,
#         "pi": np.pi,
#         "e": np.e,
#         "j": 1j,
#     }

#     try:
#         tree = ast.parse(expression, mode="eval")
#     except SyntaxError as error:
#         raise ValueError(f"Invalid custom input syntax: {error}")

#     for node in ast.walk(tree):
#         if not isinstance(
#             node,
#             (
#                 ast.Expression,
#                 ast.BinOp,
#                 ast.UnaryOp,
#                 ast.Num,
#                 ast.Constant,
#                 ast.Name,
#                 ast.Load,
#                 ast.Add,
#                 ast.Sub,
#                 ast.Mult,
#                 ast.Div,
#                 ast.Pow,
#                 ast.USub,
#                 ast.UAdd,
#                 ast.Call,
#                 ast.Tuple,
#                 ast.List,
#             ),
#         ):
#             raise ValueError("Custom input contains unsupported characters or operations.")

#         if isinstance(node, ast.Name) and node.id not in allowed_names:
#             raise ValueError(f"Unknown symbol: {node.id}")

#         if isinstance(node, ast.Call):
#             if not isinstance(node.func, ast.Name) or node.func.id not in allowed_names:
#                 raise ValueError("Only simple functions such as sqrt() are allowed.")

#     return eval(compile(tree, "<custom_state>", "eval"), {"__builtins__": {}}, allowed_names)


# def parse_custom_state_vector(text):
#     text = text.strip()
#     if not text:
#         raise ValueError("Custom state vector is empty.")

#     if not text.startswith("["):
#         text = "[" + text + "]"

#     values = safe_eval_complex_expression(text)
#     vector = np.asarray(values, dtype=complex).reshape(-1)

#     size = len(vector)
#     qubits = int(np.log2(size))

#     if 2 ** qubits != size:
#         raise ValueError("State vector length must be a power of 2, for example 2, 4, or 8.")

#     if np.linalg.norm(vector) == 0:
#         raise ValueError("State vector cannot contain only zeros.")

#     return vector / np.linalg.norm(vector)

# def apply_noise(rho, noise_type, strength):
#     """
#     Educational noise approximation.
#     Good for showing how noise changes density-matrix patterns.
#     """
#     strength = float(strength)
#     strength = max(0.0, min(1.0, strength))
#     size = rho.shape[0]

#     if noise_type == "No noise":
#         return rho

#     if noise_type == "Depolarizing noise":
#         identity = np.eye(size, dtype=complex) / size
#         return (1 - strength) * rho + strength * identity

#     if noise_type == "Phase damping / dephasing":
#         noisy = rho.copy()
#         for row in range(size):
#             for col in range(size):
#                 if row != col:
#                     noisy[row, col] *= 1 - strength
#         return noisy

#     if noise_type == "Bit-flip style mixing":
#         flipped = np.flipud(np.fliplr(rho))
#         return (1 - strength) * rho + strength * flipped

#     raise ValueError("Unknown noise type selected.")

# def plot_circle_hinton_on_axis(ax, matrix, title, show_values=False):
#     matrix = np.asarray(matrix, dtype=float)
#     size = matrix.shape[0]

#     max_value = np.max(np.abs(matrix))
#     if max_value == 0:
#         max_value = 1

#     labels = basis_labels(size)

#     ax.clear()
#     ax.set_title(title, fontsize=12)
#     ax.set_aspect("equal")
#     ax.set_xlim(-0.5, size - 0.5)
#     ax.set_ylim(size - 0.5, -0.5)
#     ax.set_facecolor("gray")

#     ax.set_xticks(range(size))
#     ax.set_yticks(range(size))
#     ax.set_xticklabels(labels, rotation=45, ha="right")
#     ax.set_yticklabels(labels)

#     ax.set_xticks(np.arange(-0.5, size, 1), minor=True)
#     ax.set_yticks(np.arange(-0.5, size, 1), minor=True)
#     ax.grid(which="minor", linewidth=0.5, alpha=0.35)

#     for row in range(size):
#         for col in range(size):
#             value = matrix[row, col]

#             if abs(value) < 1e-12:
#                 continue

#             magnitude = abs(value) / max_value
#             radius = np.sqrt(magnitude) * 0.43
#             color = "white" if value >= 0 else "black"

#             circle = Circle(
#                 (col, row),
#                 radius,
#                 facecolor=color,
#                 edgecolor="black",
#                 linewidth=1.2,
#             )
#             ax.add_patch(circle)

#             if show_values:
#                 text_color = "black" if color == "white" else "white"
#                 ax.text(
#                     col,
#                     row,
#                     f"{value:.2f}",
#                     ha="center",
#                     va="center",
#                     fontsize=8,
#                     color=text_color,
#                 )


# def create_hinton_figure(rho, selected_part, show_values):
#     if selected_part == "Real part only":
#         fig = Figure(figsize=(6.5, 6), dpi=100)
#         ax = fig.add_subplot(111)
#         plot_circle_hinton_on_axis(ax, rho.real, "Real part of density matrix", show_values)
#         fig.tight_layout()
#         return fig

#     if selected_part == "Imaginary part only":
#         fig = Figure(figsize=(6.5, 6), dpi=100)
#         ax = fig.add_subplot(111)
#         plot_circle_hinton_on_axis(ax, rho.imag, "Imaginary part of density matrix", show_values)
#         fig.tight_layout()
#         return fig

#     fig = Figure(figsize=(11, 5.5), dpi=100)
#     ax1 = fig.add_subplot(121)
#     ax2 = fig.add_subplot(122)
#     plot_circle_hinton_on_axis(ax1, rho.real, "Real part", show_values)
#     plot_circle_hinton_on_axis(ax2, rho.imag, "Imaginary part", show_values)
#     fig.suptitle("Complex density matrix Hinton visualisation", fontsize=14)
#     fig.tight_layout()
#     return fig


# def explanation_for_state(state_choice, noise_type, noise_strength):
#     explanations = {
#         "Bell state |Φ+> = (|00> + |11>) / √2": (
#             "This Bell state has probability only in |00> and |11>. "
#             "The off-diagonal circles between |00> and |11> show coherence, which is a visual sign of entanglement."
#         ),
#         "Bell state with phase = (|00> + i|11>) / √2": (
#             "This is similar to a Bell state, but it contains an imaginary phase. "
#             "That is why the imaginary diagram becomes important."
#         ),
#         "Product state |00>": (
#             "This is a simple non-entangled state. Almost all probability is located at |00>. "
#             "There are no important off-diagonal coherence terms."
#         ),
#         "Superposition = (|00> + |01> + |10> + |11>) / 2": (
#             "This state spreads probability across all basis states. "
#             "Many off-diagonal circles appear because the basis states are coherently related."
#         ),
#         "GHZ state 3 qubits = (|000> + |111>) / √2": (
#             "This is a 3-qubit entangled state. The most important values are at |000>, |111>, "
#             "and the coherence between them."
#         ),
#         "Custom state vector": (
#             "This visualisation is generated from your custom state vector. "
#             "The vector is automatically normalized before the density matrix is created."
#         ),
#     }

#     text = explanations.get(state_choice, "")

#     if noise_type != "No noise":
#         text += f"\n\nNoise applied: {noise_type} with strength {noise_strength:.2f}. "
#         if noise_type == "Depolarizing noise":
#             text += "This pushes the state toward a more mixed, less informative density matrix."
#         elif noise_type == "Phase damping / dephasing":
#             text += "This mainly reduces off-diagonal coherence circles."
#         elif noise_type == "Bit-flip style mixing":
#             text += "This mixes the original density matrix with a flipped version of itself."

#     return text

# class HintonApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Hinton Visualiser")
#         self.root.geometry("1320x780")

#         self.state_choice = tk.StringVar(value="Bell state |Φ+> = (|00> + |11>) / √2")
#         self.part_choice = tk.StringVar(value="Real and imaginary")
#         self.noise_choice = tk.StringVar(value="No noise")
#         self.noise_strength = tk.DoubleVar(value=0.0)
#         self.custom_state = tk.StringVar(value="1/sqrt(2), 0, 0, 1/sqrt(2)")
#         self.show_values = tk.BooleanVar(value=True)

#         self.canvas = None
#         self.toolbar = None
#         self.current_fig = None
#         self.current_rho = None

#         self.build_ui()
#         self.update_plot()

#     def build_ui(self):
#         control_frame = ttk.Frame(self.root, padding=12)
#         control_frame.pack(side=tk.LEFT, fill=tk.Y)

#         plot_frame = ttk.Frame(self.root, padding=8)
#         plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
#         self.plot_frame = plot_frame

#         title = ttk.Label(control_frame, text="Hinton Visualiser", font=("Arial", 16, "bold"))
#         title.pack(anchor="w", pady=(0, 14))

#         ttk.Label(control_frame, text="1. Choose quantum state:").pack(anchor="w")
#         state_menu = ttk.Combobox(
#             control_frame,
#             textvariable=self.state_choice,
#             values=[
#                 "Bell state |Φ+> = (|00> + |11>) / √2",
#                 "Bell state with phase = (|00> + i|11>) / √2",
#                 "Product state |00>",
#                 "Superposition = (|00> + |01> + |10> + |11>) / 2",
#                 "GHZ state 3 qubits = (|000> + |111>) / √2",
#                 "Custom state vector",
#             ],
#             state="readonly",
#             width=52,
#         )
#         state_menu.pack(anchor="w", pady=(4, 10))

#         ttk.Label(control_frame, text="Custom vector:").pack(anchor="w")
#         custom_entry = ttk.Entry(control_frame, textvariable=self.custom_state, width=55)
#         custom_entry.pack(anchor="w", pady=(4, 10))

#         custom_hint = ttk.Label(
#             control_frame,
#             text="Example: 1/sqrt(2), 0, 0, i/sqrt(2)",
#             foreground="gray",
#         )
#         custom_hint.pack(anchor="w", pady=(0, 12))

#         ttk.Label(control_frame, text="2. Choose matrix part:").pack(anchor="w")
#         part_menu = ttk.Combobox(
#             control_frame,
#             textvariable=self.part_choice,
#             values=["Real and imaginary", "Real part only", "Imaginary part only"],
#             state="readonly",
#             width=52,
#         )
#         part_menu.pack(anchor="w", pady=(4, 12))

#         ttk.Label(control_frame, text="3. Add noise:").pack(anchor="w")
#         noise_menu = ttk.Combobox(
#             control_frame,
#             textvariable=self.noise_choice,
#             values=[
#                 "No noise",
#                 "Depolarizing noise",
#                 "Phase damping / dephasing",
#                 "Bit-flip style mixing",
#             ],
#             state="readonly",
#             width=52,
#         )
#         noise_menu.pack(anchor="w", pady=(4, 8))

#         ttk.Label(control_frame, text="Noise strength:").pack(anchor="w")
#         noise_slider = ttk.Scale(
#             control_frame,
#             from_=0.0,
#             to=1.0,
#             variable=self.noise_strength,
#             orient="horizontal",
#             length=330,
#             command=lambda value: self.noise_value_label.config(text=f"{float(value):.2f}"),
#         )
#         noise_slider.pack(anchor="w", pady=(4, 2))

#         self.noise_value_label = ttk.Label(control_frame, text="0.00")
#         self.noise_value_label.pack(anchor="w", pady=(0, 12))

#         values_checkbox = ttk.Checkbutton(
#             control_frame,
#             text="Show numeric values",
#             variable=self.show_values,
#         )
#         values_checkbox.pack(anchor="w", pady=(0, 12))

#         update_button = ttk.Button(control_frame, text="Generate visualisation", command=self.update_plot)
#         update_button.pack(anchor="w", fill=tk.X, pady=(4, 8))

#         export_png_button = ttk.Button(control_frame, text="Export visualisation as PNG", command=self.export_png)
#         export_png_button.pack(anchor="w", fill=tk.X, pady=(0, 8))

#         export_csv_button = ttk.Button(control_frame, text="Export density matrix as CSV", command=self.export_csv)
#         export_csv_button.pack(anchor="w", fill=tk.X, pady=(0, 14))

#         ttk.Label(control_frame, text="Explanation:", font=("Arial", 11, "bold")).pack(anchor="w")
#         self.explanation_box = tk.Text(control_frame, width=45, height=13, wrap="word")
#         self.explanation_box.pack(anchor="w", pady=(4, 10))
#         self.explanation_box.configure(state="disabled")

#         reading = (
#             "How to read it:\n"
#             "• Bigger circle = larger matrix value\n"
#             "• White = positive value\n"
#             "• Black = negative value\n"
#             "• Diagonal = probabilities\n"
#             "• Off-diagonal = coherence / relationships"
#         )
#         ttk.Label(control_frame, text=reading, justify="left", wraplength=350).pack(anchor="w")

#     def get_selected_state_vector(self):
#         if self.state_choice.get() == "Custom state vector":
#             return parse_custom_state_vector(self.custom_state.get())

#         return create_state_vector(self.state_choice.get())

#     def update_explanation(self):
#         text = explanation_for_state(
#             self.state_choice.get(),
#             self.noise_choice.get(),
#             self.noise_strength.get(),
#         )
#         self.explanation_box.configure(state="normal")
#         self.explanation_box.delete("1.0", tk.END)
#         self.explanation_box.insert(tk.END, text)
#         self.explanation_box.configure(state="disabled")

#     def update_plot(self):
#         try:
#             state_vector = self.get_selected_state_vector()
#             rho = ket_to_density_matrix(state_vector)
#             rho = apply_noise(rho, self.noise_choice.get(), self.noise_strength.get())

#             self.current_rho = rho
#             fig = create_hinton_figure(rho, self.part_choice.get(), self.show_values.get())
#             self.current_fig = fig

#             if self.canvas is not None:
#                 self.canvas.get_tk_widget().destroy()

#             if self.toolbar is not None:
#                 self.toolbar.destroy()

#             self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
#             self.canvas.draw()
#             self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

#             self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
#             self.toolbar.update()

#             self.update_explanation()

#         except Exception as error:
#             messagebox.showerror("Visualisation error", str(error))

#     def export_png(self):
#         if self.current_fig is None:
#             messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
#             return

#         path = filedialog.asksaveasfilename(
#             defaultextension=".png",
#             filetypes=[("PNG image", "*.png")],
#             title="Save visualisation as PNG",
#         )

#         if path:
#             self.current_fig.savefig(path, dpi=200)
#             messagebox.showinfo("Export complete", f"Saved visualisation to:\n{path}")

#     def export_csv(self):
#         if self.current_rho is None:
#             messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
#             return

#         path = filedialog.asksaveasfilename(
#             defaultextension=".csv",
#             filetypes=[("CSV file", "*.csv")],
#             title="Save density matrix as CSV",
#         )

#         if path:
#             with open(path, "w", newline="", encoding="utf-8") as file:
#                 writer = csv.writer(file)
#                 writer.writerow(["row", "column", "real", "imaginary", "complex"])
#                 for row in range(self.current_rho.shape[0]):
#                     for col in range(self.current_rho.shape[1]):
#                         value = self.current_rho[row, col]
#                         writer.writerow([row, col, value.real, value.imag, str(value)])

#             messagebox.showinfo("Export complete", f"Saved density matrix to:\n{path}")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = HintonApp(root)
#     root.mainloop()


# import ast
# import csv
# import tkinter as tk
# from tkinter import ttk, messagebox, filedialog

# import numpy as np
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from matplotlib.figure import Figure
# from matplotlib.patches import Circle, Wedge
# from matplotlib import cm


# # =====================================================
# # Quantum state helpers
# # =====================================================

# def ket_to_density_matrix(state_vector):
#     """Convert a state vector |psi> into density matrix rho = |psi><psi|."""
#     state_vector = np.asarray(state_vector, dtype=complex)
#     norm = np.linalg.norm(state_vector)

#     if norm == 0:
#         raise ValueError("State vector cannot be zero.")

#     state_vector = state_vector / norm
#     return np.outer(state_vector, state_vector.conj())


# def basis_labels(size):
#     """Create computational basis labels such as |00>, |01>, |10>, |11>."""
#     qubits = int(np.log2(size))

#     if 2 ** qubits != size:
#         return [str(i) for i in range(size)]

#     return [f"|{i:0{qubits}b}>" for i in range(size)]


# def create_state_vector(choice):
#     """Return predefined example states."""
#     if choice == "Bell state |Φ+> = (|00> + |11>) / √2":
#         return np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

#     if choice == "Bell state with phase = (|00> + i|11>) / √2":
#         return np.array([1, 0, 0, 1j], dtype=complex) / np.sqrt(2)

#     if choice == "Product state |00>":
#         return np.array([1, 0, 0, 0], dtype=complex)

#     if choice == "Superposition = (|00> + |01> + |10> + |11>) / 2":
#         return np.array([1, 1, 1, 1], dtype=complex) / 2

#     if choice == "GHZ state 3 qubits = (|000> + |111>) / √2":
#         return np.array([1, 0, 0, 0, 0, 0, 0, 1], dtype=complex) / np.sqrt(2)

#     if choice == "W state 3 qubits = (|001> + |010> + |100>) / √3":
#         return np.array([0, 1, 1, 0, 1, 0, 0, 0], dtype=complex) / np.sqrt(3)

#     raise ValueError("Unknown state selected.")


# def safe_eval_complex_expression(expression):
#     """
#     Evaluate simple user input safely.
#     Allows: sqrt, pi, e, j, i, complex numbers, +, -, *, /, **, brackets.
#     Example input: 1/sqrt(2), 0, 0, i/sqrt(2)
#     """
#     expression = expression.replace("i", "j")
#     allowed_names = {
#         "sqrt": np.sqrt,
#         "pi": np.pi,
#         "e": np.e,
#         "j": 1j,
#     }

#     try:
#         tree = ast.parse(expression, mode="eval")
#     except SyntaxError as error:
#         raise ValueError(f"Invalid custom input syntax: {error}")

#     for node in ast.walk(tree):
#         if not isinstance(
#             node,
#             (
#                 ast.Expression,
#                 ast.BinOp,
#                 ast.UnaryOp,
#                 ast.Num,
#                 ast.Constant,
#                 ast.Name,
#                 ast.Load,
#                 ast.Add,
#                 ast.Sub,
#                 ast.Mult,
#                 ast.Div,
#                 ast.Pow,
#                 ast.USub,
#                 ast.UAdd,
#                 ast.Call,
#                 ast.Tuple,
#                 ast.List,
#             ),
#         ):
#             raise ValueError("Custom input contains unsupported characters or operations.")

#         if isinstance(node, ast.Name) and node.id not in allowed_names:
#             raise ValueError(f"Unknown symbol: {node.id}")

#         if isinstance(node, ast.Call):
#             if not isinstance(node.func, ast.Name) or node.func.id not in allowed_names:
#                 raise ValueError("Only simple functions such as sqrt() are allowed.")

#     return eval(compile(tree, "<custom_state>", "eval"), {"__builtins__": {}}, allowed_names)


# def parse_custom_state_vector(text):
#     """Parse custom state vector text into a normalized complex state vector."""
#     text = text.strip()
#     if not text:
#         raise ValueError("Custom state vector is empty.")

#     if not text.startswith("["):
#         text = "[" + text + "]"

#     values = safe_eval_complex_expression(text)
#     vector = np.asarray(values, dtype=complex).reshape(-1)

#     size = len(vector)
#     qubits = int(np.log2(size))

#     if 2 ** qubits != size:
#         raise ValueError("State vector length must be a power of 2, for example 2, 4, or 8.")

#     if np.linalg.norm(vector) == 0:
#         raise ValueError("State vector cannot contain only zeros.")

#     return vector / np.linalg.norm(vector)


# # =====================================================
# # Noise helpers
# # =====================================================

# def apply_noise(rho, noise_type, strength):
#     """
#     Educational density-matrix noise approximation.
#     Useful for showing how noise changes density-matrix patterns.
#     """
#     strength = float(strength)
#     strength = max(0.0, min(1.0, strength))
#     size = rho.shape[0]

#     if noise_type == "No noise":
#         return rho

#     if noise_type == "Depolarizing noise":
#         identity = np.eye(size, dtype=complex) / size
#         return (1 - strength) * rho + strength * identity

#     if noise_type == "Phase damping / dephasing":
#         noisy = rho.copy()
#         for row in range(size):
#             for col in range(size):
#                 if row != col:
#                     noisy[row, col] *= 1 - strength
#         return noisy

#     if noise_type == "Bit-flip style mixing":
#         flipped = np.flipud(np.fliplr(rho))
#         return (1 - strength) * rho + strength * flipped

#     raise ValueError("Unknown noise type selected.")


# def approximate_state_from_density_matrix(rho):
#     """
#     Recover the dominant pure-state approximation from a density matrix.
#     This is useful when noise makes the state mixed but the circular state
#     representation still needs a state-vector-like view.
#     """
#     eigenvalues, eigenvectors = np.linalg.eigh(rho)
#     index = np.argmax(eigenvalues.real)
#     vector = eigenvectors[:, index]

#     # Remove global phase for cleaner display.
#     non_zero = np.where(np.abs(vector) > 1e-9)[0]
#     if len(non_zero) > 0:
#         phase = np.angle(vector[non_zero[0]])
#         vector = vector * np.exp(-1j * phase)

#     return vector / np.linalg.norm(vector)


# # =====================================================
# # Hinton density matrix visualisation
# # =====================================================

# def plot_circle_hinton_on_axis(ax, matrix, title, show_values=False):
#     """
#     Circle-based Hinton diagram for one real-valued matrix.
#     Circle area represents magnitude. White/black encodes sign.
#     """
#     matrix = np.asarray(matrix, dtype=float)
#     size = matrix.shape[0]

#     max_value = np.max(np.abs(matrix))
#     if max_value == 0:
#         max_value = 1

#     labels = basis_labels(size)

#     ax.clear()
#     ax.set_title(title, fontsize=12)
#     ax.set_aspect("equal")
#     ax.set_xlim(-0.5, size - 0.5)
#     ax.set_ylim(size - 0.5, -0.5)
#     ax.set_facecolor("gray")

#     ax.set_xticks(range(size))
#     ax.set_yticks(range(size))
#     ax.set_xticklabels(labels, rotation=45, ha="right")
#     ax.set_yticklabels(labels)

#     ax.set_xticks(np.arange(-0.5, size, 1), minor=True)
#     ax.set_yticks(np.arange(-0.5, size, 1), minor=True)
#     ax.grid(which="minor", linewidth=0.5, alpha=0.35)

#     for row in range(size):
#         for col in range(size):
#             value = matrix[row, col]

#             if abs(value) < 1e-12:
#                 continue

#             magnitude = abs(value) / max_value
#             radius = np.sqrt(magnitude) * 0.43
#             color = "white" if value >= 0 else "black"

#             circle = Circle(
#                 (col, row),
#                 radius,
#                 facecolor=color,
#                 edgecolor="black",
#                 linewidth=1.2,
#             )
#             ax.add_patch(circle)

#             if show_values:
#                 text_color = "black" if color == "white" else "white"
#                 ax.text(
#                     col,
#                     row,
#                     f"{value:.2f}",
#                     ha="center",
#                     va="center",
#                     fontsize=8,
#                     color=text_color,
#                 )


# def create_hinton_figure(rho, selected_part, show_values):
#     """Create real/imaginary density matrix Hinton figure."""
#     if selected_part == "Real part only":
#         fig = Figure(figsize=(6.5, 6), dpi=100)
#         ax = fig.add_subplot(111)
#         plot_circle_hinton_on_axis(ax, rho.real, "Real part of density matrix", show_values)
#         fig.tight_layout()
#         return fig

#     if selected_part == "Imaginary part only":
#         fig = Figure(figsize=(6.5, 6), dpi=100)
#         ax = fig.add_subplot(111)
#         plot_circle_hinton_on_axis(ax, rho.imag, "Imaginary part of density matrix", show_values)
#         fig.tight_layout()
#         return fig

#     fig = Figure(figsize=(11, 5.5), dpi=100)
#     ax1 = fig.add_subplot(121)
#     ax2 = fig.add_subplot(122)
#     plot_circle_hinton_on_axis(ax1, rho.real, "Real part", show_values)
#     plot_circle_hinton_on_axis(ax2, rho.imag, "Imaginary part", show_values)
#     fig.suptitle("Complex density matrix Hinton visualisation", fontsize=14)
#     fig.tight_layout()
#     return fig


# # =====================================================
# # Dimensional Circle Notation inspired by Bley et al.
# # =====================================================


# def index_to_bits(index, number_of_qubits):
#     """
#     Return bit string using the usual computational basis order.
#     Example for 2 qubits: 0 -> 00, 1 -> 01, 2 -> 10, 3 -> 11.
#     """
#     return f"{index:0{number_of_qubits}b}"


# def basis_position_dcn(index, number_of_qubits):
#     """
#     Position basis-state circles according to dimensional circle notation.

#     In the paper's dimensional circle notation idea, every qubit corresponds
#     to one visual dimension/axis. For a small number of qubits this means:
#     - 1 qubit  -> two circles on a line
#     - 2 qubits -> four circles on a square
#     - 3 qubits -> eight circles on a cube-like projection

#     For more than 3 qubits, the view falls back to a 2D grid because a direct
#     n-dimensional drawing is no longer readable on a flat screen.
#     """
#     bits = index_to_bits(index, number_of_qubits)

#     if number_of_qubits == 1:
#         x = -1.4 if bits == "0" else 1.4
#         y = 0.0
#         return x, y

#     if number_of_qubits == 2:
#         # q2 controls vertical axis, q1 controls horizontal axis.
#         q2 = int(bits[0])
#         q1 = int(bits[1])
#         x = -1.6 if q1 == 0 else 1.6
#         y = 1.6 if q2 == 0 else -1.6
#         return x, y

#     if number_of_qubits == 3:
#         # Cube-like isometric projection.
#         # q3 -> diagonal depth axis, q2 -> vertical, q1 -> horizontal.
#         q3 = int(bits[0])
#         q2 = int(bits[1])
#         q1 = int(bits[2])

#         x_axis = np.array([1.8, 0.0])
#         y_axis = np.array([0.0, -1.8])
#         z_axis = np.array([1.0, 0.85])
#         origin = -0.5 * (x_axis + y_axis + z_axis)

#         position = origin + q1 * x_axis + q2 * y_axis + q3 * z_axis
#         return float(position[0]), float(position[1])

#     # Fallback for 4+ qubits: arrange all basis states on a grid.
#     cols = int(np.ceil(np.sqrt(2 ** number_of_qubits)))
#     row = index // cols
#     col = index % cols
#     spacing = 1.8
#     x = (col - (cols - 1) / 2) * spacing
#     y = -row * spacing
#     return x, y


# def draw_phase_gauge(ax, x, y, radius, phase):
#     """
#     Draw the phase line used in circle notation.

#     The paper describes phase as the angle between a radial line and a
#     vertical reference line. Therefore phase 0 points upward, pi points
#     downward, pi/2 points right, and -pi/2 points left.
#     """
#     dx = radius * np.sin(phase)
#     dy = radius * np.cos(phase)
#     ax.plot([x, x + dx], [y, y + dy], color="black", linewidth=1.6)
#     ax.plot([x, x], [y, y + radius], color="lightgray", linewidth=0.8, linestyle="--")


# def draw_single_circle_notation(ax, x, y, amplitude, label, show_values=False):
#     """
#     Draw one basis-state circle using circle notation.

#     Encoding:
#     - Outer circle radius = 1, representing the basis state container.
#     - Inner filled circle radius = |alpha_i|.
#     - Filled area = |alpha_i|^2, therefore equal to measurement probability.
#     - Gauge/radius line angle = phase of alpha_i.
#     """
#     magnitude = abs(amplitude)
#     probability = magnitude ** 2
#     phase = np.angle(amplitude) if magnitude > 1e-12 else 0.0

#     outer = Circle((x, y), 0.65, facecolor="white", edgecolor="black", linewidth=1.4)
#     ax.add_patch(outer)

#     if magnitude > 1e-12:
#         inner = Circle((x, y), 0.65 * magnitude, facecolor="#76B7E5", edgecolor="black", linewidth=1.0, alpha=0.9)
#         ax.add_patch(inner)
#         draw_phase_gauge(ax, x, y, 0.65 * magnitude, phase)
#     else:
#         small_dot = Circle((x, y), 0.025, facecolor="lightgray", edgecolor="none")
#         ax.add_patch(small_dot)

#     ax.text(x, y - 0.92, label, ha="center", va="top", fontsize=10)

#     if show_values:
#         ax.text(
#             x,
#             y + 0.92,
#             f"|α|={magnitude:.2f}\np={probability:.2f}\nφ={phase:.2f}",
#             ha="center",
#             va="bottom",
#             fontsize=8,
#         )


# def draw_dcn_axes(ax, number_of_qubits):
#     """Draw simple axis/edge guides for 1, 2, and 3 qubit DCN layouts."""
#     if number_of_qubits == 1:
#         ax.plot([-1.4, 1.4], [0, 0], color="lightgray", linewidth=1.2)
#         ax.text(0, -1.25, "q1 axis", ha="center", fontsize=9, color="gray")

#     elif number_of_qubits == 2:
#         points = [basis_position_dcn(i, 2) for i in range(4)]
#         p = {index_to_bits(i, 2): points[i] for i in range(4)}
#         edges = [("00", "01"), ("00", "10"), ("01", "11"), ("10", "11")]
#         for a, b in edges:
#             ax.plot([p[a][0], p[b][0]], [p[a][1], p[b][1]], color="lightgray", linewidth=1.2, zorder=0)
#         ax.text(0, -2.95, "q1 horizontal, q2 vertical", ha="center", fontsize=9, color="gray")

#     elif number_of_qubits == 3:
#         points = [basis_position_dcn(i, 3) for i in range(8)]
#         p = {index_to_bits(i, 3): points[i] for i in range(8)}
#         edges = []
#         for i in range(8):
#             bits = index_to_bits(i, 3)
#             for bit_position in range(3):
#                 flipped = list(bits)
#                 flipped[bit_position] = "1" if flipped[bit_position] == "0" else "0"
#                 flipped = "".join(flipped)
#                 if bits < flipped:
#                     edges.append((bits, flipped))
#         for a, b in edges:
#             ax.plot([p[a][0], p[b][0]], [p[a][1], p[b][1]], color="lightgray", linewidth=1.0, zorder=0)
#         ax.text(0, -3.25, "cube-like layout: one axis per qubit", ha="center", fontsize=9, color="gray")


# def plot_dimensional_circle_notation(ax, state_vector, title, show_values=False):
#     """
#     Plot dimensional circle notation for a pure state vector.

#     This is closer to the paper than the earlier version:
#     - It does not put all states around one large ring.
#     - It places basis states according to qubit dimensions.
#     - It uses inner filled circles for magnitude.
#     - It uses a radial gauge line for phase.
#     """
#     state_vector = np.asarray(state_vector, dtype=complex)
#     state_vector = state_vector / np.linalg.norm(state_vector)
#     size = len(state_vector)
#     number_of_qubits = int(np.log2(size))

#     labels = basis_labels(size)

#     ax.clear()
#     ax.set_aspect("equal")
#     ax.axis("off")
#     ax.set_title(title, fontsize=13)

#     draw_dcn_axes(ax, number_of_qubits)

#     xs = []
#     ys = []
#     for index, amplitude in enumerate(state_vector):
#         x, y = basis_position_dcn(index, number_of_qubits)
#         xs.append(x)
#         ys.append(y)
#         draw_single_circle_notation(ax, x, y, amplitude, labels[index], show_values)

#     margin = 1.75
#     ax.set_xlim(min(xs) - margin, max(xs) + margin)
#     ax.set_ylim(min(ys) - margin, max(ys) + margin)

#     if number_of_qubits > 3:
#         ax.text(
#             0,
#             min(ys) - 1.2,
#             "Note: 4+ qubits are displayed in a grid fallback because exact dimensional layout is not readable in 2D.",
#             ha="center",
#             fontsize=9,
#             color="gray",
#         )


# def plot_circle_notation_legend(ax):
#     """Legend matching circle notation encoding: magnitude and phase gauge."""
#     ax.clear()
#     ax.set_title("Circle notation legend", fontsize=11)
#     ax.set_aspect("equal")
#     ax.axis("off")

#     examples = [
#         (0.0, 0.0, 1 / np.sqrt(2), "positive real"),
#         (2.0, 0.0, 1j / np.sqrt(2), "+90° phase"),
#         (4.0, 0.0, -1 / np.sqrt(2), "180° phase"),
#     ]

#     for x, y, amp, label in examples:
#         draw_single_circle_notation(ax, x, y, amp, label, show_values=False)

#     ax.text(2.0, -1.75, "Inner circle radius = |α|; filled area = |α|² = probability", ha="center", fontsize=9)
#     ax.text(2.0, -2.15, "Gauge line angle from vertical = phase φ", ha="center", fontsize=9)
#     ax.set_xlim(-1.2, 5.2)
#     ax.set_ylim(-2.6, 1.7)


# def create_circular_state_figure(state_vector, show_values):
#     """Create dimensional circle notation figure."""
#     fig = Figure(figsize=(10, 6.4), dpi=100)
#     ax_state = fig.add_subplot(121)
#     ax_legend = fig.add_subplot(122)

#     plot_dimensional_circle_notation(
#         ax_state,
#         state_vector,
#         "Dimensional circle notation",
#         show_values,
#     )
#     plot_circle_notation_legend(ax_legend)

#     fig.suptitle("Dimensional circle notation for a quantum state", fontsize=14)
#     fig.tight_layout()
#     return fig


# def create_combined_figure(rho, state_vector, selected_part, show_values):
#     """Create combined figure: Hinton density matrix + dimensional circle notation."""
#     fig = Figure(figsize=(13, 7), dpi=100)
#     ax1 = fig.add_subplot(221)
#     ax2 = fig.add_subplot(222)
#     ax3 = fig.add_subplot(223)
#     ax4 = fig.add_subplot(224)

#     plot_circle_hinton_on_axis(ax1, rho.real, "Density matrix: real part", show_values)
#     plot_circle_hinton_on_axis(ax2, rho.imag, "Density matrix: imaginary part", show_values)
#     plot_dimensional_circle_notation(ax3, state_vector, "Dimensional circle notation", show_values)
#     plot_circle_notation_legend(ax4)

#     fig.suptitle("Combined Hinton + dimensional circle notation", fontsize=14)
#     fig.tight_layout()
#     return fig


# # =====================================================
# # Explanation text
# # =====================================================

# def explanation_for_state(state_choice, visualisation_choice, noise_type, noise_strength):
#     explanations = {
#         "Bell state |Φ+> = (|00> + |11>) / √2": (
#             "This Bell state has probability only in |00> and |11>. "
#             "In the density matrix, the off-diagonal circles between |00> and |11> show coherence, "
#             "which is a visual sign of entanglement."
#         ),
#         "Bell state with phase = (|00> + i|11>) / √2": (
#             "This is similar to a Bell state, but it contains an imaginary phase. "
#             "The circular notation makes this visible through the phase direction/colour, while the "
#             "Hinton view shows the real and imaginary density-matrix components."
#         ),
#         "Product state |00>": (
#             "This is a simple non-entangled state. Almost all probability is located at |00>. "
#             "There are no important off-diagonal coherence terms."
#         ),
#         "Superposition = (|00> + |01> + |10> + |11>) / 2": (
#             "This state spreads probability across all basis states. "
#             "Many off-diagonal circles appear in the density matrix because the basis states are coherently related."
#         ),
#         "GHZ state 3 qubits = (|000> + |111>) / √2": (
#             "This is a 3-qubit entangled state. The most important values are at |000>, |111>, "
#             "and the coherence between them."
#         ),
#         "W state 3 qubits = (|001> + |010> + |100>) / √3": (
#             "This is a 3-qubit W state. It distributes probability over three single-excitation basis states, "
#             "which creates a different entanglement pattern from the GHZ state."
#         ),
#         "Custom state vector": (
#             "This visualisation is generated from your custom state vector. "
#             "The vector is automatically normalized before the density matrix is created."
#         ),
#     }

#     text = explanations.get(state_choice, "")

#     if visualisation_choice == "Hinton density matrix":
#         text += "\n\nCurrent view: Hinton density matrix. This is best for inspecting probabilities, coherence terms, and real/imaginary matrix structure."
#     elif visualisation_choice == "Dimensional circle notation":
#         text += "\n\nCurrent view: dimensional circle notation. This is best for inspecting pure-state amplitudes: inner circle size shows |α|, filled area shows probability, and the radial gauge line shows phase relative to the vertical reference."
#     else:
#         text += "\n\nCurrent view: combined. This connects the state-vector view with the density-matrix view."

#     if noise_type != "No noise":
#         text += f"\n\nNoise applied: {noise_type} with strength {noise_strength:.2f}. "
#         if noise_type == "Depolarizing noise":
#             text += "This pushes the state toward a more mixed, less informative density matrix."
#         elif noise_type == "Phase damping / dephasing":
#             text += "This mainly reduces off-diagonal coherence circles."
#         elif noise_type == "Bit-flip style mixing":
#             text += "This mixes the original density matrix with a flipped version of itself."

#     return text


# # =====================================================
# # Tkinter UI
# # =====================================================

# class HintonApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Quantum State Visualiser")
#         self.root.geometry("1380x820")

#         self.state_choice = tk.StringVar(value="Bell state |Φ+> = (|00> + |11>) / √2")
#         self.visualisation_choice = tk.StringVar(value="Combined: Hinton + dimensional circle notation")
#         self.part_choice = tk.StringVar(value="Real and imaginary")
#         self.noise_choice = tk.StringVar(value="No noise")
#         self.noise_strength = tk.DoubleVar(value=0.0)
#         self.custom_state = tk.StringVar(value="1/sqrt(2), 0, 0, i/sqrt(2)")
#         self.show_values = tk.BooleanVar(value=True)

#         self.canvas = None
#         self.toolbar = None
#         self.current_fig = None
#         self.current_rho = None
#         self.current_state_vector = None

#         self.build_ui()
#         self.update_plot()

#     def build_ui(self):
#         control_frame = ttk.Frame(self.root, padding=12)
#         control_frame.pack(side=tk.LEFT, fill=tk.Y)

#         plot_frame = ttk.Frame(self.root, padding=8)
#         plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
#         self.plot_frame = plot_frame

#         title = ttk.Label(control_frame, text="Quantum State Visualiser", font=("Arial", 16, "bold"))
#         title.pack(anchor="w", pady=(0, 14))

#         ttk.Label(control_frame, text="1. Choose quantum state:").pack(anchor="w")
#         state_menu = ttk.Combobox(
#             control_frame,
#             textvariable=self.state_choice,
#             values=[
#                 "Bell state |Φ+> = (|00> + |11>) / √2",
#                 "Bell state with phase = (|00> + i|11>) / √2",
#                 "Product state |00>",
#                 "Superposition = (|00> + |01> + |10> + |11>) / 2",
#                 "GHZ state 3 qubits = (|000> + |111>) / √2",
#                 "W state 3 qubits = (|001> + |010> + |100>) / √3",
#                 "Custom state vector",
#             ],
#             state="readonly",
#             width=58,
#         )
#         state_menu.pack(anchor="w", pady=(4, 10))

#         ttk.Label(control_frame, text="Custom vector:").pack(anchor="w")
#         custom_entry = ttk.Entry(control_frame, textvariable=self.custom_state, width=61)
#         custom_entry.pack(anchor="w", pady=(4, 10))

#         custom_hint = ttk.Label(
#             control_frame,
#             text="Example: 1/sqrt(2), 0, 0, i/sqrt(2)",
#             foreground="gray",
#         )
#         custom_hint.pack(anchor="w", pady=(0, 12))

#         ttk.Label(control_frame, text="2. Choose visualisation:").pack(anchor="w")
#         visualisation_menu = ttk.Combobox(
#             control_frame,
#             textvariable=self.visualisation_choice,
#             values=[
#                 "Hinton density matrix",
#                 "Dimensional circle notation",
#                 "Combined: Hinton + dimensional circle notation",
#             ],
#             state="readonly",
#             width=58,
#         )
#         visualisation_menu.pack(anchor="w", pady=(4, 12))

#         ttk.Label(control_frame, text="3. Hinton matrix part:").pack(anchor="w")
#         part_menu = ttk.Combobox(
#             control_frame,
#             textvariable=self.part_choice,
#             values=["Real and imaginary", "Real part only", "Imaginary part only"],
#             state="readonly",
#             width=58,
#         )
#         part_menu.pack(anchor="w", pady=(4, 12))

#         ttk.Label(control_frame, text="4. Add noise:").pack(anchor="w")
#         noise_menu = ttk.Combobox(
#             control_frame,
#             textvariable=self.noise_choice,
#             values=[
#                 "No noise",
#                 "Depolarizing noise",
#                 "Phase damping / dephasing",
#                 "Bit-flip style mixing",
#             ],
#             state="readonly",
#             width=58,
#         )
#         noise_menu.pack(anchor="w", pady=(4, 8))

#         ttk.Label(control_frame, text="Noise strength:").pack(anchor="w")
#         noise_slider = ttk.Scale(
#             control_frame,
#             from_=0.0,
#             to=1.0,
#             variable=self.noise_strength,
#             orient="horizontal",
#             length=360,
#             command=lambda value: self.noise_value_label.config(text=f"{float(value):.2f}"),
#         )
#         noise_slider.pack(anchor="w", pady=(4, 2))

#         self.noise_value_label = ttk.Label(control_frame, text="0.00")
#         self.noise_value_label.pack(anchor="w", pady=(0, 12))

#         values_checkbox = ttk.Checkbutton(
#             control_frame,
#             text="Show numeric values",
#             variable=self.show_values,
#         )
#         values_checkbox.pack(anchor="w", pady=(0, 12))

#         update_button = ttk.Button(control_frame, text="Generate visualisation", command=self.update_plot)
#         update_button.pack(anchor="w", fill=tk.X, pady=(4, 8))

#         export_png_button = ttk.Button(control_frame, text="Export visualisation as PNG", command=self.export_png)
#         export_png_button.pack(anchor="w", fill=tk.X, pady=(0, 8))

#         export_csv_button = ttk.Button(control_frame, text="Export density matrix as CSV", command=self.export_csv)
#         export_csv_button.pack(anchor="w", fill=tk.X, pady=(0, 14))

#         ttk.Label(control_frame, text="Explanation:", font=("Arial", 11, "bold")).pack(anchor="w")
#         self.explanation_box = tk.Text(control_frame, width=50, height=15, wrap="word")
#         self.explanation_box.pack(anchor="w", pady=(4, 10))
#         self.explanation_box.configure(state="disabled")

#         reading = (
#             "How to read it:\n"
#             "Hinton view:\n"
#             "• Bigger circle = larger matrix value\n"
#             "• White/black = positive/negative real value\n"
#             "• Off-diagonal = coherence relationships\n\n"
#             "Dimensional circle notation:\n"
#             "• Each basis state has one outer circle\n"
#             "• Inner circle radius = |α|\n"
#             "• Filled area = |α|² probability\n"
#             "• Gauge line angle = complex phase"
#         )
#         ttk.Label(control_frame, text=reading, justify="left", wraplength=390).pack(anchor="w")

#     def get_selected_state_vector(self):
#         if self.state_choice.get() == "Custom state vector":
#             return parse_custom_state_vector(self.custom_state.get())

#         return create_state_vector(self.state_choice.get())

#     def update_explanation(self):
#         text = explanation_for_state(
#             self.state_choice.get(),
#             self.visualisation_choice.get(),
#             self.noise_choice.get(),
#             self.noise_strength.get(),
#         )
#         self.explanation_box.configure(state="normal")
#         self.explanation_box.delete("1.0", tk.END)
#         self.explanation_box.insert(tk.END, text)
#         self.explanation_box.configure(state="disabled")

#     def update_plot(self):
#         try:
#             original_state_vector = self.get_selected_state_vector()
#             rho = ket_to_density_matrix(original_state_vector)
#             noisy_rho = apply_noise(rho, self.noise_choice.get(), self.noise_strength.get())

#             # If noise is applied, use dominant eigenstate as a pure-state approximation
#             # for the circular state-vector view. The density matrix remains exact for Hinton.
#             if self.noise_choice.get() == "No noise":
#                 display_state_vector = original_state_vector
#             else:
#                 display_state_vector = approximate_state_from_density_matrix(noisy_rho)

#             self.current_rho = noisy_rho
#             self.current_state_vector = display_state_vector

#             if self.visualisation_choice.get() == "Hinton density matrix":
#                 fig = create_hinton_figure(noisy_rho, self.part_choice.get(), self.show_values.get())
#             elif self.visualisation_choice.get() == "Dimensional circle notation":
#                 fig = create_circular_state_figure(display_state_vector, self.show_values.get())
#             else:
#                 fig = create_combined_figure(
#                     noisy_rho,
#                     display_state_vector,
#                     self.part_choice.get(),
#                     self.show_values.get(),
#                 )

#             self.current_fig = fig

#             if self.canvas is not None:
#                 self.canvas.get_tk_widget().destroy()

#             if self.toolbar is not None:
#                 self.toolbar.destroy()

#             self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
#             self.canvas.draw()
#             self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

#             self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
#             self.toolbar.update()

#             self.update_explanation()

#         except Exception as error:
#             messagebox.showerror("Visualisation error", str(error))

#     def export_png(self):
#         if self.current_fig is None:
#             messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
#             return

#         path = filedialog.asksaveasfilename(
#             defaultextension=".png",
#             filetypes=[("PNG image", "*.png")],
#             title="Save visualisation as PNG",
#         )

#         if path:
#             self.current_fig.savefig(path, dpi=200)
#             messagebox.showinfo("Export complete", f"Saved visualisation to:\n{path}")

#     def export_csv(self):
#         if self.current_rho is None:
#             messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
#             return

#         path = filedialog.asksaveasfilename(
#             defaultextension=".csv",
#             filetypes=[("CSV file", "*.csv")],
#             title="Save density matrix as CSV",
#         )

#         if path:
#             with open(path, "w", newline="", encoding="utf-8") as file:
#                 writer = csv.writer(file)
#                 writer.writerow(["row", "column", "real", "imaginary", "complex"])
#                 for row in range(self.current_rho.shape[0]):
#                     for col in range(self.current_rho.shape[1]):
#                         value = self.current_rho[row, col]
#                         writer.writerow([row, col, value.real, value.imag, str(value)])

#             messagebox.showinfo("Export complete", f"Saved density matrix to:\n{path}")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = HintonApp(root)
#     root.mainloop()


import ast
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle


# =====================================================
# Quantum state helpers
# =====================================================

def ket_to_density_matrix(state_vector):
    """Convert a state vector |psi> into density matrix rho = |psi><psi|."""
    state_vector = np.asarray(state_vector, dtype=complex)
    norm = np.linalg.norm(state_vector)

    if norm == 0:
        raise ValueError("State vector cannot be zero.")

    state_vector = state_vector / norm
    return np.outer(state_vector, state_vector.conj())


def basis_labels(size):
    """Create computational basis labels such as |00>, |01>, |10>, |11>."""
    qubits = int(np.log2(size))

    if 2 ** qubits != size:
        return [str(i) for i in range(size)]

    return [f"|{i:0{qubits}b}>" for i in range(size)]


def create_state_vector(choice):
    """Return predefined example states."""
    if choice == "Bell state |Φ+> = (|00> + |11>) / √2":
        return np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

    if choice == "Bell state with phase = (|00> + i|11>) / √2":
        return np.array([1, 0, 0, 1j], dtype=complex) / np.sqrt(2)

    if choice == "Product state |00>":
        return np.array([1, 0, 0, 0], dtype=complex)

    if choice == "Superposition 2 qubits = all basis states":
        return np.array([1, 1, 1, 1], dtype=complex) / 2

    if choice == "GHZ state 3 qubits = (|000> + |111>) / √2":
        return np.array([1, 0, 0, 0, 0, 0, 0, 1], dtype=complex) / np.sqrt(2)

    if choice == "W state 3 qubits = (|001> + |010> + |100>) / √3":
        return np.array([0, 1, 1, 0, 1, 0, 0, 0], dtype=complex) / np.sqrt(3)

    if choice == "Superposition 3 qubits = all basis states":
        return np.ones(8, dtype=complex) / np.sqrt(8)

    if choice == "Superposition 4 qubits = all basis states":
        return np.ones(16, dtype=complex) / np.sqrt(16)

    if choice == "Sparse 4 qubits = |0000> + i|1111>":
        vector = np.zeros(16, dtype=complex)
        vector[0] = 1
        vector[15] = 1j
        return vector / np.sqrt(2)

    raise ValueError("Unknown state selected.")


def safe_eval_complex_expression(expression):
    """
    Evaluate simple user input safely.
    Allows: sqrt, pi, e, j, i, complex numbers, +, -, *, /, **, brackets.
    Example input: 1/sqrt(2), 0, 0, i/sqrt(2)
    """
    expression = expression.replace("i", "j")
    allowed_names = {
        "sqrt": np.sqrt,
        "pi": np.pi,
        "e": np.e,
        "j": 1j,
    }

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError(f"Invalid custom input syntax: {error}")

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.Expression,
                ast.BinOp,
                ast.UnaryOp,
                ast.Num,
                ast.Constant,
                ast.Name,
                ast.Load,
                ast.Add,
                ast.Sub,
                ast.Mult,
                ast.Div,
                ast.Pow,
                ast.USub,
                ast.UAdd,
                ast.Call,
                ast.Tuple,
                ast.List,
            ),
        ):
            raise ValueError("Custom input contains unsupported characters or operations.")

        if isinstance(node, ast.Name) and node.id not in allowed_names:
            raise ValueError(f"Unknown symbol: {node.id}")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in allowed_names:
                raise ValueError("Only simple functions such as sqrt() are allowed.")

    return eval(compile(tree, "<custom_state>", "eval"), {"__builtins__": {}}, allowed_names)


def parse_custom_state_vector(text):
    """Parse custom state vector text into a normalized complex state vector."""
    text = text.strip()
    if not text:
        raise ValueError("Custom state vector is empty.")

    if not text.startswith("["):
        text = "[" + text + "]"

    values = safe_eval_complex_expression(text)
    vector = np.asarray(values, dtype=complex).reshape(-1)

    size = len(vector)
    qubits = int(np.log2(size))

    if 2 ** qubits != size:
        raise ValueError("State vector length must be a power of 2, for example 2, 4, 8, or 16.")

    if np.linalg.norm(vector) == 0:
        raise ValueError("State vector cannot contain only zeros.")

    return vector / np.linalg.norm(vector)


# =====================================================
# Noise helpers
# =====================================================

def apply_noise(rho, noise_type, strength):
    """
    Educational density-matrix noise approximation.
    Useful for showing how noise changes density-matrix patterns.
    """
    strength = float(strength)
    strength = max(0.0, min(1.0, strength))
    size = rho.shape[0]

    if noise_type == "No noise":
        return rho

    if noise_type == "Depolarizing noise":
        identity = np.eye(size, dtype=complex) / size
        return (1 - strength) * rho + strength * identity

    if noise_type == "Phase damping / dephasing":
        noisy = rho.copy()
        for row in range(size):
            for col in range(size):
                if row != col:
                    noisy[row, col] *= 1 - strength
        return noisy

    if noise_type == "Bit-flip style mixing":
        flipped = np.flipud(np.fliplr(rho))
        return (1 - strength) * rho + strength * flipped

    raise ValueError("Unknown noise type selected.")


def approximate_state_from_density_matrix(rho):
    """
    Recover the dominant pure-state approximation from a density matrix.
    This is useful when noise makes the state mixed but the circular state
    representation still needs a state-vector-like view.
    """
    eigenvalues, eigenvectors = np.linalg.eigh(rho)
    index = np.argmax(eigenvalues.real)
    vector = eigenvectors[:, index]

    # Remove global phase for cleaner display.
    non_zero = np.where(np.abs(vector) > 1e-9)[0]
    if len(non_zero) > 0:
        phase = np.angle(vector[non_zero[0]])
        vector = vector * np.exp(-1j * phase)

    return vector / np.linalg.norm(vector)


# =====================================================
# Hinton density matrix visualisation
# =====================================================

def plot_circle_hinton_on_axis(ax, matrix, title, show_values=False):
    """
    Circle-based Hinton diagram for one real-valued matrix.
    Circle area represents magnitude. White/black encodes sign.
    """
    matrix = np.asarray(matrix, dtype=float)
    size = matrix.shape[0]

    max_value = np.max(np.abs(matrix))
    if max_value == 0:
        max_value = 1

    labels = basis_labels(size)

    ax.clear()
    ax.set_title(title, fontsize=12)
    ax.set_aspect("equal")
    ax.set_xlim(-0.5, size - 0.5)
    ax.set_ylim(size - 0.5, -0.5)
    ax.set_facecolor("gray")

    ax.set_xticks(range(size))
    ax.set_yticks(range(size))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    ax.set_xticks(np.arange(-0.5, size, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, size, 1), minor=True)
    ax.grid(which="minor", linewidth=0.5, alpha=0.35)

    # For larger matrices, numeric values quickly become unreadable.
    adaptive_show_values = show_values and size <= 8

    for row in range(size):
        for col in range(size):
            value = matrix[row, col]

            if abs(value) < 1e-12:
                continue

            magnitude = abs(value) / max_value
            radius = np.sqrt(magnitude) * 0.43
            color = "white" if value >= 0 else "black"

            circle = Circle(
                (col, row),
                radius,
                facecolor=color,
                edgecolor="black",
                linewidth=1.2,
            )
            ax.add_patch(circle)

            if adaptive_show_values:
                text_color = "black" if color == "white" else "white"
                ax.text(
                    col,
                    row,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=text_color,
                )


def create_hinton_figure(rho, selected_part, show_values):
    """Create real/imaginary density matrix Hinton figure."""
    if selected_part == "Real part only":
        fig = Figure(figsize=(6.5, 6), dpi=100)
        ax = fig.add_subplot(111)
        plot_circle_hinton_on_axis(ax, rho.real, "Real part of density matrix", show_values)
        fig.tight_layout()
        return fig

    if selected_part == "Imaginary part only":
        fig = Figure(figsize=(6.5, 6), dpi=100)
        ax = fig.add_subplot(111)
        plot_circle_hinton_on_axis(ax, rho.imag, "Imaginary part of density matrix", show_values)
        fig.tight_layout()
        return fig

    fig = Figure(figsize=(11, 5.5), dpi=100)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    plot_circle_hinton_on_axis(ax1, rho.real, "Real part", show_values)
    plot_circle_hinton_on_axis(ax2, rho.imag, "Imaginary part", show_values)
    fig.suptitle("Complex density matrix Hinton visualisation", fontsize=14)
    fig.tight_layout()
    return fig


# =====================================================
# Adaptive dimensional circle notation
# =====================================================

def index_to_bits(index, number_of_qubits):
    return f"{index:0{number_of_qubits}b}"


def get_adaptive_circle_config(number_of_qubits):
    """
    Level-of-detail rules.

    The goal is to keep circle notation readable as dimensionality grows.
    """
    if number_of_qubits <= 1:
        return {
            "layout": "line",
            "base_radius": 0.72,
            "font_size": 10,
            "show_labels": True,
            "show_values_allowed": True,
            "probability_threshold": 0.0,
            "hide_tiny": False,
            "alpha_for_tiny": 0.20,
        }

    if number_of_qubits == 2:
        return {
            "layout": "square",
            "base_radius": 0.62,
            "font_size": 9,
            "show_labels": True,
            "show_values_allowed": True,
            "probability_threshold": 0.0,
            "hide_tiny": False,
            "alpha_for_tiny": 0.20,
        }

    if number_of_qubits == 3:
        return {
            "layout": "layered",
            "base_radius": 0.46,
            "font_size": 8,
            "show_labels": True,
            "show_values_allowed": False,
            "probability_threshold": 0.005,
            "hide_tiny": False,
            "alpha_for_tiny": 0.16,
        }

    if number_of_qubits == 4:
        return {
            "layout": "grouped_grid",
            "base_radius": 0.33,
            "font_size": 7,
            "show_labels": True,
            "show_values_allowed": False,
            "probability_threshold": 0.01,
            "hide_tiny": False,
            "alpha_for_tiny": 0.10,
        }

    return {
        "layout": "top_amplitudes",
        "base_radius": 0.30,
        "font_size": 7,
        "show_labels": True,
        "show_values_allowed": False,
        "probability_threshold": 0.015,
        "hide_tiny": True,
        "alpha_for_tiny": 0.08,
    }


def basis_position_adaptive(index, number_of_qubits):
    """
    Adaptive layout for circle notation.

    1 qubit: line.
    2 qubits: square.
    3 qubits: two 2x2 layers, much clearer than cube projection.
    4 qubits: grouped 4x4 grid with quadrant grouping.
    5+ qubits: compact grid/top-amplitudes view.
    """
    bits = index_to_bits(index, number_of_qubits)

    if number_of_qubits == 1:
        return (-1.35 if bits == "0" else 1.35), 0.0

    if number_of_qubits == 2:
        row = int(bits[0])
        col = int(bits[1])
        spacing = 1.9
        x = (col - 0.5) * spacing
        y = (0.5 - row) * spacing
        return x, y

    if number_of_qubits == 3:
        # Two clean layers based on the first qubit.
        # Within each layer, the last two qubits form a 2x2 square.
        layer = int(bits[0])
        row = int(bits[1])
        col = int(bits[2])

        layer_offset_x = -2.2 if layer == 0 else 2.2
        spacing = 1.25
        x = layer_offset_x + (col - 0.5) * spacing
        y = (0.5 - row) * spacing
        return x, y

    if number_of_qubits == 4:
        # 4x4 grid:
        # first two bits decide the big group,
        # last two bits decide the local position inside group.
        group_row = int(bits[0])
        group_col = int(bits[1])
        local_row = int(bits[2])
        local_col = int(bits[3])

        group_spacing = 2.35
        local_spacing = 0.78

        x = (group_col - 0.5) * group_spacing + (local_col - 0.5) * local_spacing
        y = (0.5 - group_row) * group_spacing + (0.5 - local_row) * local_spacing
        return x, y

    # 5+ qubits: simple compact grid.
    total = 2 ** number_of_qubits
    cols = int(np.ceil(np.sqrt(total)))
    row = index // cols
    col = index % cols
    spacing = 0.82
    x = (col - (cols - 1) / 2) * spacing
    y = -row * spacing
    return x, y


def draw_phase_gauge(ax, x, y, radius, phase, linewidth=1.2):
    """
    Draw the phase gauge line.

    Phase 0 points upward, pi points downward, pi/2 points right,
    and -pi/2 points left.
    """
    dx = radius * np.sin(phase)
    dy = radius * np.cos(phase)

    # Light vertical reference line.
    ax.plot([x, x], [y, y + radius], color="lightgray", linewidth=0.6, linestyle="--", zorder=4)

    # Actual phase line.
    ax.plot([x, x + dx], [y, y + dy], color="black", linewidth=linewidth, zorder=5)


def draw_single_circle_notation(
    ax,
    x,
    y,
    amplitude,
    label,
    config,
    show_values=False,
):
    """
    Draw one basis-state circle using adaptive circle notation.
    """
    base_radius = config["base_radius"]
    font_size = config["font_size"]
    probability_threshold = config["probability_threshold"]

    magnitude = abs(amplitude)
    probability = magnitude ** 2
    phase = np.angle(amplitude) if magnitude > 1e-12 else 0.0

    is_tiny = probability < probability_threshold

    if config["hide_tiny"] and is_tiny:
        return

    # Fade low-probability states instead of giving them equal visual weight.
    alpha = config["alpha_for_tiny"] if is_tiny else 1.0
    edge_alpha = 0.35 if is_tiny else 1.0

    outer = Circle(
        (x, y),
        base_radius,
        facecolor="white",
        edgecolor=(0, 0, 0, edge_alpha),
        linewidth=1.0,
        zorder=2,
    )
    ax.add_patch(outer)

    if magnitude > 1e-12 and not is_tiny:
        inner = Circle(
            (x, y),
            base_radius * magnitude,
            facecolor="#76B7E5",
            edgecolor="black",
            linewidth=0.8,
            alpha=0.88,
            zorder=3,
        )
        ax.add_patch(inner)
        draw_phase_gauge(ax, x, y, base_radius * magnitude, phase, linewidth=1.0)
    elif magnitude > 1e-12:
        tiny = Circle(
            (x, y),
            max(base_radius * 0.10, base_radius * magnitude),
            facecolor="#76B7E5",
            edgecolor="none",
            alpha=alpha,
            zorder=3,
        )
        ax.add_patch(tiny)
    else:
        small_dot = Circle((x, y), base_radius * 0.04, facecolor="lightgray", edgecolor="none", alpha=0.5, zorder=3)
        ax.add_patch(small_dot)

    if config["show_labels"]:
        ax.text(x, y - base_radius - 0.12, label, ha="center", va="top", fontsize=font_size)

    adaptive_show_values = show_values and config["show_values_allowed"]
    if adaptive_show_values:
        ax.text(
            x,
            y + base_radius + 0.12,
            f"|α|={magnitude:.2f}\np={probability:.2f}\nφ={phase:.2f}",
            ha="center",
            va="bottom",
            fontsize=font_size - 1,
        )


def draw_group_backgrounds(ax, number_of_qubits):
    """
    Draw subtle group/layer backgrounds.
    This improves readability for 3 and 4 qubits.
    """
    if number_of_qubits == 3:
        # q0 = 0 layer and q0 = 1 layer
        for x_center, label in [(-2.2, "q1 = 0"), (2.2, "q1 = 1")]:
            rect = Rectangle(
                (x_center - 1.35, -1.35),
                2.7,
                2.7,
                facecolor="#F5F5F5",
                edgecolor="lightgray",
                linewidth=1.0,
                zorder=0,
            )
            ax.add_patch(rect)
            ax.text(x_center, 1.68, label, ha="center", va="center", fontsize=9, color="dimgray")

    if number_of_qubits == 4:
        # Four groups by first two qubits.
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
                facecolor="#F7F7F7",
                edgecolor="lightgray",
                linewidth=1.0,
                zorder=0,
            )
            ax.add_patch(rect)
            ax.text(x, y + 1.10, f"q1q2={group}", ha="center", va="center", fontsize=8, color="dimgray")


def plot_adaptive_circle_notation(ax, state_vector, title, show_values=False):
    """
    Adaptive dimensional circle notation.

    Important behaviour:
    - 1-2 qubits: detailed dimensional circle notation.
    - 3 qubits: grouped into two layers, values hidden by default.
    - 4 qubits: grouped 4x4 layout, labels retained but values hidden.
    - 5+ qubits: compact overview/top-amplitude-like grid.
    """
    state_vector = np.asarray(state_vector, dtype=complex)
    state_vector = state_vector / np.linalg.norm(state_vector)
    size = len(state_vector)
    number_of_qubits = int(np.log2(size))
    labels = basis_labels(size)
    config = get_adaptive_circle_config(number_of_qubits)

    ax.clear()
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13)

    draw_group_backgrounds(ax, number_of_qubits)

    xs = []
    ys = []
    probabilities = np.abs(state_vector) ** 2

    for index, amplitude in enumerate(state_vector):
        x, y = basis_position_adaptive(index, number_of_qubits)
        xs.append(x)
        ys.append(y)
        draw_single_circle_notation(ax, x, y, amplitude, labels[index], config, show_values)

    margin = 1.15 if number_of_qubits <= 2 else 1.0
    ax.set_xlim(min(xs) - margin, max(xs) + margin)
    ax.set_ylim(min(ys) - margin - 0.25, max(ys) + margin + 0.35)

    # Add concise adaptive status note.
    non_zero_count = int(np.sum(probabilities > config["probability_threshold"]))
    note = (
        f"{number_of_qubits} qubits | {size} basis states | "
        f"adaptive layout: {config['layout']} | visible significant states: {non_zero_count}"
    )
    ax.text(
        0,
        min(ys) - margin - 0.75,
        note,
        ha="center",
        fontsize=8,
        color="gray",
    )


def plot_circle_notation_legend(ax):
    """Legend matching circle notation encoding: magnitude and phase gauge."""
    ax.clear()
    ax.set_title("Circle notation legend", fontsize=11)
    ax.set_aspect("equal")
    ax.axis("off")

    config = {
        "base_radius": 0.42,
        "font_size": 8,
        "show_labels": True,
        "show_values_allowed": False,
        "probability_threshold": 0.0,
        "hide_tiny": False,
        "alpha_for_tiny": 0.2,
    }

    examples = [
        (0.0, 0.0, 1 / np.sqrt(2), "positive real"),
        (1.55, 0.0, 1j / np.sqrt(2), "+90° phase"),
        (3.10, 0.0, -1 / np.sqrt(2), "180° phase"),
    ]

    for x, y, amp, label in examples:
        draw_single_circle_notation(ax, x, y, amp, label, config, show_values=False)

    ax.text(1.55, -1.25, "Inner radius = |α|; filled area = |α|²", ha="center", fontsize=8)
    ax.text(1.55, -1.55, "Gauge line angle from vertical = phase φ", ha="center", fontsize=8)
    ax.text(1.55, -1.85, "3+ qubits: values are hidden automatically to reduce clutter", ha="center", fontsize=8, color="gray")
    ax.set_xlim(-0.8, 3.9)
    ax.set_ylim(-2.15, 1.1)


def create_circular_state_figure(state_vector, show_values):
    """Create adaptive circle notation figure."""
    fig = Figure(figsize=(10.5, 6.6), dpi=100)
    ax_state = fig.add_subplot(121)
    ax_legend = fig.add_subplot(122)

    plot_adaptive_circle_notation(
        ax_state,
        state_vector,
        "Adaptive dimensional circle notation",
        show_values,
    )
    plot_circle_notation_legend(ax_legend)

    fig.suptitle("Adaptive dimensional circle notation for a quantum state", fontsize=14)
    fig.tight_layout()
    return fig


def create_combined_figure(rho, state_vector, selected_part, show_values):
    """Create combined figure: Hinton density matrix + adaptive circle notation."""
    fig = Figure(figsize=(13.4, 7.3), dpi=100)
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    plot_circle_hinton_on_axis(ax1, rho.real, "Density matrix: real part", show_values)
    plot_circle_hinton_on_axis(ax2, rho.imag, "Density matrix: imaginary part", show_values)
    plot_adaptive_circle_notation(ax3, state_vector, "Adaptive circle notation", show_values)
    plot_circle_notation_legend(ax4)

    fig.suptitle("Combined Hinton + adaptive dimensional circle notation", fontsize=14)
    fig.tight_layout()
    return fig


# =====================================================
# Explanation text
# =====================================================

def explanation_for_state(state_choice, visualisation_choice, noise_type, noise_strength, number_of_qubits):
    explanations = {
        "Bell state |Φ+> = (|00> + |11>) / √2": (
            "This Bell state has probability only in |00> and |11>. "
            "In the density matrix, the off-diagonal circles between |00> and |11> show coherence, "
            "which is a visual sign of entanglement."
        ),
        "Bell state with phase = (|00> + i|11>) / √2": (
            "This is similar to a Bell state, but it contains an imaginary phase. "
            "The circle notation shows this using the phase gauge line, while the Hinton view shows "
            "the real and imaginary density-matrix components."
        ),
        "Product state |00>": (
            "This is a simple non-entangled state. Almost all probability is located at |00>. "
            "There are no important off-diagonal coherence terms."
        ),
        "Superposition 2 qubits = all basis states": (
            "This state spreads probability across all two-qubit basis states. "
            "Many off-diagonal circles appear in the density matrix because the basis states are coherently related."
        ),
        "GHZ state 3 qubits = (|000> + |111>) / √2": (
            "This is a 3-qubit entangled state. The most important values are at |000>, |111>, "
            "and the coherence between them."
        ),
        "W state 3 qubits = (|001> + |010> + |100>) / √3": (
            "This is a 3-qubit W state. It distributes probability over three single-excitation basis states, "
            "which creates a different entanglement pattern from the GHZ state."
        ),
        "Superposition 3 qubits = all basis states": (
            "This state distributes probability evenly across all 8 basis states. "
            "The adaptive circle view hides numeric values to prevent visual overload."
        ),
        "Superposition 4 qubits = all basis states": (
            "This state distributes probability evenly across all 16 basis states. "
            "The adaptive circle view switches to grouped 4-qubit layout to improve readability."
        ),
        "Sparse 4 qubits = |0000> + i|1111>": (
            "This sparse 4-qubit state highlights two dominant basis states. "
            "It is useful for testing whether the adaptive layout can keep important amplitudes readable."
        ),
        "Custom state vector": (
            "This visualisation is generated from your custom state vector. "
            "The vector is automatically normalized before the density matrix is created."
        ),
    }

    text = explanations.get(state_choice, "")

    if visualisation_choice == "Hinton density matrix":
        text += "\n\nCurrent view: Hinton density matrix. This is best for inspecting probabilities, coherence terms, and real/imaginary matrix structure."
    elif visualisation_choice == "Adaptive dimensional circle notation":
        text += "\n\nCurrent view: adaptive dimensional circle notation. It changes its layout and detail level as the number of qubits grows."
    else:
        text += "\n\nCurrent view: combined. This connects the state-vector view with the density-matrix view."

    if number_of_qubits <= 2:
        text += "\n\nAdaptive behaviour: detailed labels and numeric values are allowed because the state space is still small."
    elif number_of_qubits == 3:
        text += "\n\nAdaptive behaviour: the view uses two grouped layers and hides numeric values to reduce clutter."
    elif number_of_qubits == 4:
        text += "\n\nAdaptive behaviour: the view uses a grouped 4x4 layout and hides numeric values because 16 basis states are too dense for full annotation."
    else:
        text += "\n\nAdaptive behaviour: the view switches to a compact overview because the number of basis states grows exponentially."

    if noise_type != "No noise":
        text += f"\n\nNoise applied: {noise_type} with strength {noise_strength:.2f}. "
        if noise_type == "Depolarizing noise":
            text += "This pushes the state toward a more mixed, less informative density matrix."
        elif noise_type == "Phase damping / dephasing":
            text += "This mainly reduces off-diagonal coherence circles."
        elif noise_type == "Bit-flip style mixing":
            text += "This mixes the original density matrix with a flipped version of itself."

    return text


# =====================================================
# Tkinter UI
# =====================================================

class HintonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum State Visualiser")
        self.root.geometry("1400x840")

        self.state_choice = tk.StringVar(value="Bell state |Φ+> = (|00> + |11>) / √2")
        self.visualisation_choice = tk.StringVar(value="Combined: Hinton + adaptive circle notation")
        self.part_choice = tk.StringVar(value="Real and imaginary")
        self.noise_choice = tk.StringVar(value="No noise")
        self.noise_strength = tk.DoubleVar(value=0.0)
        self.custom_state = tk.StringVar(value="1/sqrt(2), 0, 0, i/sqrt(2)")
        self.show_values = tk.BooleanVar(value=True)

        self.canvas = None
        self.toolbar = None
        self.current_fig = None
        self.current_rho = None
        self.current_state_vector = None

        self.build_ui()
        self.update_plot()

    def build_ui(self):
        control_frame = ttk.Frame(self.root, padding=12)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        plot_frame = ttk.Frame(self.root, padding=8)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.plot_frame = plot_frame

        title = ttk.Label(control_frame, text="Quantum State Visualiser", font=("Arial", 16, "bold"))
        title.pack(anchor="w", pady=(0, 14))

        ttk.Label(control_frame, text="1. Choose quantum state:").pack(anchor="w")
        state_menu = ttk.Combobox(
            control_frame,
            textvariable=self.state_choice,
            values=[
                "Bell state |Φ+> = (|00> + |11>) / √2",
                "Bell state with phase = (|00> + i|11>) / √2",
                "Product state |00>",
                "Superposition 2 qubits = all basis states",
                "GHZ state 3 qubits = (|000> + |111>) / √2",
                "W state 3 qubits = (|001> + |010> + |100>) / √3",
                "Superposition 3 qubits = all basis states",
                "Superposition 4 qubits = all basis states",
                "Sparse 4 qubits = |0000> + i|1111>",
                "Custom state vector",
            ],
            state="readonly",
            width=58,
        )
        state_menu.pack(anchor="w", pady=(4, 10))

        ttk.Label(control_frame, text="Custom vector:").pack(anchor="w")
        custom_entry = ttk.Entry(control_frame, textvariable=self.custom_state, width=61)
        custom_entry.pack(anchor="w", pady=(4, 10))

        custom_hint = ttk.Label(
            control_frame,
            text="Example: 1/sqrt(2), 0, 0, i/sqrt(2)",
            foreground="gray",
        )
        custom_hint.pack(anchor="w", pady=(0, 12))

        ttk.Label(control_frame, text="2. Choose visualisation:").pack(anchor="w")
        visualisation_menu = ttk.Combobox(
            control_frame,
            textvariable=self.visualisation_choice,
            values=[
                "Hinton density matrix",
                "Adaptive dimensional circle notation",
                "Combined: Hinton + adaptive circle notation",
            ],
            state="readonly",
            width=58,
        )
        visualisation_menu.pack(anchor="w", pady=(4, 12))

        ttk.Label(control_frame, text="3. Hinton matrix part:").pack(anchor="w")
        part_menu = ttk.Combobox(
            control_frame,
            textvariable=self.part_choice,
            values=["Real and imaginary", "Real part only", "Imaginary part only"],
            state="readonly",
            width=58,
        )
        part_menu.pack(anchor="w", pady=(4, 12))

        ttk.Label(control_frame, text="4. Add noise:").pack(anchor="w")
        noise_menu = ttk.Combobox(
            control_frame,
            textvariable=self.noise_choice,
            values=[
                "No noise",
                "Depolarizing noise",
                "Phase damping / dephasing",
                "Bit-flip style mixing",
            ],
            state="readonly",
            width=58,
        )
        noise_menu.pack(anchor="w", pady=(4, 8))

        ttk.Label(control_frame, text="Noise strength:").pack(anchor="w")
        noise_slider = ttk.Scale(
            control_frame,
            from_=0.0,
            to=1.0,
            variable=self.noise_strength,
            orient="horizontal",
            length=360,
            command=lambda value: self.noise_value_label.config(text=f"{float(value):.2f}"),
        )
        noise_slider.pack(anchor="w", pady=(4, 2))

        self.noise_value_label = ttk.Label(control_frame, text="0.00")
        self.noise_value_label.pack(anchor="w", pady=(0, 12))

        values_checkbox = ttk.Checkbutton(
            control_frame,
            text="Show numeric values where readable",
            variable=self.show_values,
        )
        values_checkbox.pack(anchor="w", pady=(0, 12))

        update_button = ttk.Button(control_frame, text="Generate visualisation", command=self.update_plot)
        update_button.pack(anchor="w", fill=tk.X, pady=(4, 8))

        export_png_button = ttk.Button(control_frame, text="Export visualisation as PNG", command=self.export_png)
        export_png_button.pack(anchor="w", fill=tk.X, pady=(0, 8))

        export_csv_button = ttk.Button(control_frame, text="Export density matrix as CSV", command=self.export_csv)
        export_csv_button.pack(anchor="w", fill=tk.X, pady=(0, 14))

        ttk.Label(control_frame, text="Explanation:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.explanation_box = tk.Text(control_frame, width=50, height=16, wrap="word")
        self.explanation_box.pack(anchor="w", pady=(4, 10))
        self.explanation_box.configure(state="disabled")

        reading = (
            "How to read it:\n"
            "Hinton view:\n"
            "• Bigger circle = larger matrix value\n"
            "• White/black = positive/negative real value\n"
            "• Off-diagonal = coherence relationships\n\n"
            "Adaptive circle notation:\n"
            "• 1-2 qubits: detailed dimensional view\n"
            "• 3 qubits: grouped layers\n"
            "• 4 qubits: grouped 4x4 layout\n"
            "• 5+ qubits: compact overview\n"
            "• Inner radius = |α|, area = |α|²\n"
            "• Gauge line angle = complex phase"
        )
        ttk.Label(control_frame, text=reading, justify="left", wraplength=390).pack(anchor="w")

    def get_selected_state_vector(self):
        if self.state_choice.get() == "Custom state vector":
            return parse_custom_state_vector(self.custom_state.get())

        return create_state_vector(self.state_choice.get())

    def update_explanation(self, number_of_qubits):
        text = explanation_for_state(
            self.state_choice.get(),
            self.visualisation_choice.get(),
            self.noise_choice.get(),
            self.noise_strength.get(),
            number_of_qubits,
        )
        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("1.0", tk.END)
        self.explanation_box.insert(tk.END, text)
        self.explanation_box.configure(state="disabled")

    def update_plot(self):
        try:
            original_state_vector = self.get_selected_state_vector()
            number_of_qubits = int(np.log2(len(original_state_vector)))
            rho = ket_to_density_matrix(original_state_vector)
            noisy_rho = apply_noise(rho, self.noise_choice.get(), self.noise_strength.get())

            # If noise is applied, use dominant eigenstate as a pure-state approximation
            # for the circle state-vector view. The density matrix remains exact for Hinton.
            if self.noise_choice.get() == "No noise":
                display_state_vector = original_state_vector
            else:
                display_state_vector = approximate_state_from_density_matrix(noisy_rho)

            self.current_rho = noisy_rho
            self.current_state_vector = display_state_vector

            if self.visualisation_choice.get() == "Hinton density matrix":
                fig = create_hinton_figure(noisy_rho, self.part_choice.get(), self.show_values.get())
            elif self.visualisation_choice.get() == "Adaptive dimensional circle notation":
                fig = create_circular_state_figure(display_state_vector, self.show_values.get())
            else:
                fig = create_combined_figure(
                    noisy_rho,
                    display_state_vector,
                    self.part_choice.get(),
                    self.show_values.get(),
                )

            self.current_fig = fig

            if self.canvas is not None:
                self.canvas.get_tk_widget().destroy()

            if self.toolbar is not None:
                self.toolbar.destroy()

            self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
            self.toolbar.update()

            self.update_explanation(number_of_qubits)

        except Exception as error:
            messagebox.showerror("Visualisation error", str(error))

    def export_png(self):
        if self.current_fig is None:
            messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            title="Save visualisation as PNG",
        )

        if path:
            self.current_fig.savefig(path, dpi=200)
            messagebox.showinfo("Export complete", f"Saved visualisation to:\n{path}")

    def export_csv(self):
        if self.current_rho is None:
            messagebox.showwarning("Nothing to export", "Generate a visualisation first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            title="Save density matrix as CSV",
        )

        if path:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["row", "column", "real", "imaginary", "complex"])
                for row in range(self.current_rho.shape[0]):
                    for col in range(self.current_rho.shape[1]):
                        value = self.current_rho[row, col]
                        writer.writerow([row, col, value.real, value.imag, str(value)])

            messagebox.showinfo("Export complete", f"Saved density matrix to:\n{path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HintonApp(root)
    root.mainloop()