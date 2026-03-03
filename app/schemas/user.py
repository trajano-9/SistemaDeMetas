from pydantic import BaseModel, EmailStr

# Schema para os dados que chegam do formulário de cadastro
class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    is_gestor: bool  # Receberá True (Gestor) ou False (Colaborador) do HTML

# Schema para devolver os dados do usuário (sem vazar a senha!)
class UserResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    is_gestor: bool
    is_active: bool

    class Config:
        from_attributes = True