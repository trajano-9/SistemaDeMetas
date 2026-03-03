from pydantic import BaseModel
from typing import Optional

# Schema para quando o usuário está CRIANDO a meta
class MetaCreate(BaseModel):
    indicador: str
    perspectiva: str
    peso: float
    escala_a: str
    escala_b: str
    escala_c: str
    escala_d: str
    escala_e: str

# Schema para quando o usuário vai se AVALIAR (Preencher justificativa e letra)
class MetaAvaliacao(BaseModel):
    justificativa: str
    avaliacao: str # A, B, C, D, E

# Schema para devolver os dados para o Front-end
class MetaResponse(BaseModel):
    id: int
    indicador: str
    perspectiva: str
    peso: float
    escala_a: str
    escala_b: str
    escala_c: str
    escala_d: str
    escala_e: str
    justificativa: Optional[str]
    avaliacao: Optional[str]
    nota: Optional[float]
    status: str
    user_id: int

    class Config:
        from_attributes = True