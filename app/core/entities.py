import decimal
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, field_validator

def _validate_decimal(v: Any) -> decimal.Decimal:
    """Interceptors to deny floats explicitly, preserving decimal exactness."""
    if isinstance(v, float):
        raise ValueError("float values are strictly forbidden for monetary operations.")
    
    if isinstance(v, (int, str, decimal.Decimal)):
        # Configurar precision
        decimal.getcontext().prec = 28
        try:
            d = decimal.Decimal(v)
        except decimal.InvalidOperation:
            raise ValueError(f"Invalid decimal format: {v}")
        
        if d.is_nan() or d.is_infinite():
            raise ValueError(f"NaN or Infinity are not allowed in Decimal values.")
        return d
        
    raise TypeError(f"Invalid type for decimal field: {type(v)}. Must be str, int, or Decimal.")

class HallazgoOperativo(BaseModel):
    model_config = ConfigDict(strict=False)

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

    @field_validator('entidad_origen', 'patologia_id', mode='before')
    @classmethod
    def _validate_not_empty(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("String field cannot be empty or whitespace only.")
        return v

    @field_validator('nivel_severidad', mode='before')
    @classmethod
    def _validate_severidad(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("nivel_severidad must be a non-empty string.")
        
        normalized = v.strip().lower()
        if normalized not in {'bajo', 'medio', 'alto', 'critico'}:
            raise ValueError(f"Invalid nivel_severidad: {normalized}. Allowed: bajo, medio, alto, critico.")
        return normalized

    @field_validator('monto_detectado', 'diferencia', 'alicuota_iva', mode='before')
    @classmethod
    def _validate_money_fields(cls, v: Any) -> decimal.Decimal:
        return _validate_decimal(v)
