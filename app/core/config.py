import os

class Settings:
    # Informações gerais do sistema
    PROJECT_NAME: str = "Sistema de Metas e Desempenho"
    PROJECT_VERSION: str = "1.0.0"
    
    # Configuração do Banco de Dados
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./metas.db"
    
    # Chave secreta para segurança (Sessões e Cookies)
    # No futuro, se for para a nuvem, o sistema puxa a senha do servidor (os.getenv)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dasghdcsagdsa")

# Cria uma variável global que poderá ser importada em outros arquivos
settings = Settings()