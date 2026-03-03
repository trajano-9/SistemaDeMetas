from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    is_gestor = Column(Boolean, default=False) 
    
    # NOVA COLUNA: Guarda o ID do gestor (pode ser vazio se o cara já for um gestor)
    gestor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    is_active = Column(Boolean, default=True)

    # Relacionamento com as metas
    metas = relationship("Meta", back_populates="dono")