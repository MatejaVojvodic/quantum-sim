import ast
from typing import Any

import numpy as np

from quantum_visualizer.states import QuantumStateService


class CustomStateParser:
    """
    Safely parses simple custom quantum state vectors.

    Example:
        1/sqrt(2), 0, 0, i/sqrt(2)

    SOLID:
    - Single Responsibility: parsing user text only.
    """

    _allowed_names = {
        "sqrt": np.sqrt,
        "pi": np.pi,
        "e": np.e,
        "j": 1j,
    }

    _allowed_nodes = (
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
    )

    def parse_state_vector(self, text: str) -> np.ndarray:
        text = text.strip()
        if not text:
            raise ValueError("Custom state vector is empty.")

        if not text.startswith("["):
            text = "[" + text + "]"

        values = self._safe_eval(text)
        return QuantumStateService.normalize(np.asarray(values, dtype=complex).reshape(-1))

    def _safe_eval(self, expression: str) -> Any:
        expression = expression.replace("i", "j")

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as error:
            raise ValueError(f"Invalid custom input syntax: {error}") from error

        for node in ast.walk(tree):
            if not isinstance(node, self._allowed_nodes):
                raise ValueError("Custom input contains unsupported characters or operations.")

            if isinstance(node, ast.Name) and node.id not in self._allowed_names:
                raise ValueError(f"Unknown symbol: {node.id}")

            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in self._allowed_names:
                    raise ValueError("Only simple functions such as sqrt() are allowed.")

        return eval(compile(tree, "<custom_state>", "eval"), {"__builtins__": {}}, self._allowed_names)
