from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ConfirmedOperationalContext:
    cliente_id: str
    selected_item_id: str
    tipo_operativo_confirmado: str
    familia_smartpyme: str
    required_data: tuple[str, ...]
    possible_pathologies: tuple[str, ...]
    suggested_formulas: tuple[str, ...]

    @classmethod
    def from_selection_result(
        cls, cliente_id: str, selection_result: dict[str, Any]
    ) -> ConfirmedOperationalContext:
        """
        Crea un contexto confirmado a partir del resultado de la selección del dueño.
        """
        if selection_result.get("status") != "SELECTION_CONFIRMED":
            raise ValueError(
                f"Invalid selection result status: {selection_result.get('status')}"
            )

        return cls(
            cliente_id=cliente_id,
            selected_item_id=selection_result["item_id"],
            tipo_operativo_confirmado=selection_result["tipo_operativo_confirmado"],
            familia_smartpyme=selection_result["familia_smartpyme"],
            required_data=tuple(selection_result.get("required_data", [])),
            possible_pathologies=tuple(selection_result.get("possible_pathologies", [])),
            suggested_formulas=tuple(selection_result.get("suggested_formulas", [])),
        )
