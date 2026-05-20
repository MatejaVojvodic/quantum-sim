import ast
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Circle

def ket_to_density_matrix(state_vector):
    state_vector = np.asarray(state_vector, dtype=complex)
    norm = np.linalg.norm(state_vector)

    if norm == 0:
        raise ValueError("State vector cannot be zero.")

    state_vector = state_vector / norm
    return np.outer(state_vector, state_vector.conj())


def basis_labels(size):
    qubits = int(np.log2(size))

    if 2 ** qubits != size:
        return [str(i) for i in range(size)]

    return [f"|{i:0{qubits}b}>" for i in range(size)]

def create_state_vector(choice):
    if choice == "Bell state |Φ+> = (|00> + |11>) / √2":
        return np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

    if choice == "Bell state with phase = (|00> + i|11>) / √2":
        return np.array([1, 0, 0, 1j], dtype=complex) / np.sqrt(2)

    if choice == "Product state |00>":
        return np.array([1, 0, 0, 0], dtype=complex)

    if choice == "Superposition = (|00> + |01> + |10> + |11>) / 2":
        return np.array([1, 1, 1, 1], dtype=complex) / 2

    if choice == "GHZ state 3 qubits = (|000> + |111>) / √2":
        return np.array([1, 0, 0, 0, 0, 0, 0, 1], dtype=complex) / np.sqrt(2)

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
        raise ValueError("State vector length must be a power of 2, for example 2, 4, or 8.")

    if np.linalg.norm(vector) == 0:
        raise ValueError("State vector cannot contain only zeros.")

    return vector / np.linalg.norm(vector)

def apply_noise(rho, noise_type, strength):
    """
    Educational noise approximation.
    Good for showing how noise changes density-matrix patterns.
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

def plot_circle_hinton_on_axis(ax, matrix, title, show_values=False):
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

            if show_values:
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


def explanation_for_state(state_choice, noise_type, noise_strength):
    explanations = {
        "Bell state |Φ+> = (|00> + |11>) / √2": (
            "This Bell state has probability only in |00> and |11>. "
            "The off-diagonal circles between |00> and |11> show coherence, which is a visual sign of entanglement."
        ),
        "Bell state with phase = (|00> + i|11>) / √2": (
            "This is similar to a Bell state, but it contains an imaginary phase. "
            "That is why the imaginary diagram becomes important."
        ),
        "Product state |00>": (
            "This is a simple non-entangled state. Almost all probability is located at |00>. "
            "There are no important off-diagonal coherence terms."
        ),
        "Superposition = (|00> + |01> + |10> + |11>) / 2": (
            "This state spreads probability across all basis states. "
            "Many off-diagonal circles appear because the basis states are coherently related."
        ),
        "GHZ state 3 qubits = (|000> + |111>) / √2": (
            "This is a 3-qubit entangled state. The most important values are at |000>, |111>, "
            "and the coherence between them."
        ),
        "Custom state vector": (
            "This visualisation is generated from your custom state vector. "
            "The vector is automatically normalized before the density matrix is created."
        ),
    }

    text = explanations.get(state_choice, "")

    if noise_type != "No noise":
        text += f"\n\nNoise applied: {noise_type} with strength {noise_strength:.2f}. "
        if noise_type == "Depolarizing noise":
            text += "This pushes the state toward a more mixed, less informative density matrix."
        elif noise_type == "Phase damping / dephasing":
            text += "This mainly reduces off-diagonal coherence circles."
        elif noise_type == "Bit-flip style mixing":
            text += "This mixes the original density matrix with a flipped version of itself."

    return text

class HintonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hinton Visualiser")
        self.root.geometry("1320x780")

        self.state_choice = tk.StringVar(value="Bell state |Φ+> = (|00> + |11>) / √2")
        self.part_choice = tk.StringVar(value="Real and imaginary")
        self.noise_choice = tk.StringVar(value="No noise")
        self.noise_strength = tk.DoubleVar(value=0.0)
        self.custom_state = tk.StringVar(value="1/sqrt(2), 0, 0, 1/sqrt(2)")
        self.show_values = tk.BooleanVar(value=True)

        self.canvas = None
        self.toolbar = None
        self.current_fig = None
        self.current_rho = None

        self.build_ui()
        self.update_plot()

    def build_ui(self):
        control_frame = ttk.Frame(self.root, padding=12)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        plot_frame = ttk.Frame(self.root, padding=8)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.plot_frame = plot_frame

        title = ttk.Label(control_frame, text="Hinton Visualiser", font=("Arial", 16, "bold"))
        title.pack(anchor="w", pady=(0, 14))

        ttk.Label(control_frame, text="1. Choose quantum state:").pack(anchor="w")
        state_menu = ttk.Combobox(
            control_frame,
            textvariable=self.state_choice,
            values=[
                "Bell state |Φ+> = (|00> + |11>) / √2",
                "Bell state with phase = (|00> + i|11>) / √2",
                "Product state |00>",
                "Superposition = (|00> + |01> + |10> + |11>) / 2",
                "GHZ state 3 qubits = (|000> + |111>) / √2",
                "Custom state vector",
            ],
            state="readonly",
            width=52,
        )
        state_menu.pack(anchor="w", pady=(4, 10))

        ttk.Label(control_frame, text="Custom vector:").pack(anchor="w")
        custom_entry = ttk.Entry(control_frame, textvariable=self.custom_state, width=55)
        custom_entry.pack(anchor="w", pady=(4, 10))

        custom_hint = ttk.Label(
            control_frame,
            text="Example: 1/sqrt(2), 0, 0, i/sqrt(2)",
            foreground="gray",
        )
        custom_hint.pack(anchor="w", pady=(0, 12))

        ttk.Label(control_frame, text="2. Choose matrix part:").pack(anchor="w")
        part_menu = ttk.Combobox(
            control_frame,
            textvariable=self.part_choice,
            values=["Real and imaginary", "Real part only", "Imaginary part only"],
            state="readonly",
            width=52,
        )
        part_menu.pack(anchor="w", pady=(4, 12))

        ttk.Label(control_frame, text="3. Add noise:").pack(anchor="w")
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
            width=52,
        )
        noise_menu.pack(anchor="w", pady=(4, 8))

        ttk.Label(control_frame, text="Noise strength:").pack(anchor="w")
        noise_slider = ttk.Scale(
            control_frame,
            from_=0.0,
            to=1.0,
            variable=self.noise_strength,
            orient="horizontal",
            length=330,
            command=lambda value: self.noise_value_label.config(text=f"{float(value):.2f}"),
        )
        noise_slider.pack(anchor="w", pady=(4, 2))

        self.noise_value_label = ttk.Label(control_frame, text="0.00")
        self.noise_value_label.pack(anchor="w", pady=(0, 12))

        values_checkbox = ttk.Checkbutton(
            control_frame,
            text="Show numeric values",
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
        self.explanation_box = tk.Text(control_frame, width=45, height=13, wrap="word")
        self.explanation_box.pack(anchor="w", pady=(4, 10))
        self.explanation_box.configure(state="disabled")

        reading = (
            "How to read it:\n"
            "• Bigger circle = larger matrix value\n"
            "• White = positive value\n"
            "• Black = negative value\n"
            "• Diagonal = probabilities\n"
            "• Off-diagonal = coherence / relationships"
        )
        ttk.Label(control_frame, text=reading, justify="left", wraplength=350).pack(anchor="w")

    def get_selected_state_vector(self):
        if self.state_choice.get() == "Custom state vector":
            return parse_custom_state_vector(self.custom_state.get())

        return create_state_vector(self.state_choice.get())

    def update_explanation(self):
        text = explanation_for_state(
            self.state_choice.get(),
            self.noise_choice.get(),
            self.noise_strength.get(),
        )
        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("1.0", tk.END)
        self.explanation_box.insert(tk.END, text)
        self.explanation_box.configure(state="disabled")

    def update_plot(self):
        try:
            state_vector = self.get_selected_state_vector()
            rho = ket_to_density_matrix(state_vector)
            rho = apply_noise(rho, self.noise_choice.get(), self.noise_strength.get())

            self.current_rho = rho
            fig = create_hinton_figure(rho, self.part_choice.get(), self.show_values.get())
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

            self.update_explanation()

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

