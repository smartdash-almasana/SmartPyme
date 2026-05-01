import decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator


def _validate_decimal(v: Any) -> decimal.Decimal:
    if isinstance(v, float):
        raise ValueError("float values are strictly forbidden for monetary operations.")

    if isinstance(v, (int, str, decimal.Decimal)):
        decimal.getcontext().prec = 28
        try:
            d = decimal.Decimal(v)
        except decimal.InvalidOperation as error:
            raise ValueError(f"Invalid decimal format: {v}") from error

        if d.is_nan() or d.is_infinite():
            raise ValueError("NaN or Infinity are not allowed in Decimal values.")
        return d

    raise TypeError(f"Invalid type for decimal field: {type(v)}.")


class HallazgoOperativo(BaseModel):
    model_config = ConfigDict(strict=False)

    cliente_id: str
    entidad_origen: str
    patologia_id: str
    nivel_severidad: str
    monto_detectado: decimal.Decimal
    diferencia: decimal.Decimal
    alicuota_iva: decimal.Decimal

    entidad_referencia: Optional[str] = None
    fuente_a: Optional[str] = None
    fuente_b: Optional[str] = None
    descripcion: Optional[str] = None

    @field_validator("cliente_id", "entidad_origen", "patologia_id", mode="before")
    @classmethod
    def _validate_not_empty(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("String field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("nivel_severidad", mode="before")
    @classmethod
    def _validate_severidad(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("nivel_severidad must be a non-empty string.")

        normalized = v.strip().lower()
        if normalized not in {"bajo", "medio", "alto", "critico"}:
            raise ValueError("Invalid nivel_severidad.")
        return normalized

    @field_validator("monto_detectado", "diferencia", "alicuota_iva", mode="before")
    @classmethod
    def _validate_money_fields(cls, v: Any) -> decimal.Decimal:
        return _validate_decimal(v)
