from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Define o caminho do banco de dados (vai criar um arquivo metas.db na raiz do projeto)
SQLALCHEMY_DATABASE_URL = "sqlite:///./metas.db"

# 2. Cria o "motor" do SQLAlchemy que vai se comunicar com o SQLite
# O connect_args é uma configuração obrigatória do SQLite para trabalhar bem com o FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Cria a fábrica de sessões (cada requisição na API terá sua própria sessão)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Cria a classe Base que nossos modelos (Tabelas) vão herdar
Base = declarative_base()

# 5. Função auxiliadora (Dependency) para abrir e fechar o banco a cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()