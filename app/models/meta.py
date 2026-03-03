from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Meta(Base):
    __tablename__ = "metas"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados Base da Meta
    indicador = Column(Text, nullable=False) # Ex: Seguidores - Instagram
    perspectiva = Column(String, nullable=False) # Financeira, Cliente, Processos, Pessoas
    peso = Column(Float, nullable=False) # Ex: 20 (para 20%)
    
    # Descrições da Escala (O que precisa fazer para tirar cada nota)
    escala_a = Column(Text, nullable=False)
    escala_b = Column(Text, nullable=False)
    escala_c = Column(Text, nullable=False)
    escala_d = Column(Text, nullable=False)
    escala_e = Column(Text, nullable=False)
    
    # Avaliação (Preenchidos depois pelo usuário)
    justificativa = Column(Text, nullable=True)
    avaliacao = Column(String, nullable=True) # Letra escolhida: A, B, C, D ou E
    nota = Column(Float, nullable=True) # Valor calculado: (Peso * Valor da Letra)
    
    # Controle do Gestor
    status = Column(String, default="Pendente") # Pendente, Aprovada, Rejeitada
    
    # Relacionamento: De quem é essa meta?
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Cria o "link" com o usuário
    dono = relationship("User", back_populates="metas")