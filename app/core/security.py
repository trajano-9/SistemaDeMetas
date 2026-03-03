import bcrypt

def get_password_hash(password: str) -> str:
    """Recebe uma senha em texto limpo e retorna o hash criptografado."""
    # O bcrypt exige que a senha seja convertida para bytes (utf-8)
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    
    # Retornamos como string normal para o SQLAlchemy salvar no banco
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha digitada bate com o hash salvo no banco."""
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)