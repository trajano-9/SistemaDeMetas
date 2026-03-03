from fastapi import APIRouter, Depends, Form, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password

# Cria o roteador que vai gerenciar as URLs que começam com /auth
router = APIRouter(prefix="/auth", tags=["Autenticação"])
templates = Jinja2Templates(directory="app/templates")

@router.post("/registro")
def registrar_usuario(
    request: Request,
    nome: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    is_gestor: bool = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Verifica se já existe alguém com esse nome de usuário no banco
    usuario_existente = db.query(User).filter(User.username == username).first()
    if usuario_existente:
        return templates.TemplateResponse("registro.html", {"request": request, "erro": "Este nome de usuário já está em uso."})

    # 2. Criptografa a senha
    senha_criptografada = get_password_hash(password)

    # 3. Prepara o novo usuário APENAS com os dados básicos (sem gestor_id por enquanto)
    novo_usuario = User(
        nome=nome,
        username=username,
        hashed_password=senha_criptografada,
        is_gestor=is_gestor,
        gestor_id=None # Nasce sem vínculo! Será adicionado depois pelo gestor.
    )
    
    # 4. Salva no banco de dados
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    # 5. Se deu tudo certo, redireciona para a página de login
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/login")
def login_usuario(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(User).filter(User.username == username).first()

    if not usuario or not verify_password(password, usuario.hashed_password):
        # Renderizamos a tela com a variável de erro:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "erro": "Usuário ou senha incorretos."}
        )
    
    resposta = RedirectResponse(url="/painel", status_code=status.HTTP_303_SEE_OTHER)
    resposta.set_cookie(key="usuario_logado", value=usuario.nome)
    
    return resposta

@router.get("/logout")
def logout_usuario():
    # Prepara o redirecionamento para a tela de login
    resposta = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Destrói o "crachá" (cookie) do navegador
    resposta.delete_cookie(key="usuario_logado")
    
    return resposta