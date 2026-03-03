from fastapi import FastAPI, Request, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.db.database import engine, Base
from app.models import user
from app.api.routers import auth, metas
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models import user, meta
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.meta import Meta


# Isso aqui vai criar o arquivo metas.db e todas as tabelas.
Base.metadata.create_all(bind=engine)

# Inicia o aplicativo FastAPI
app = FastAPI(title="Sistema de Metas API")

# Ensina o FastAPI onde buscar o CSS, JS e Imagens
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Ensina o FastAPI onde buscar os arquivos HTML (Jinja2)
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(metas.router)

# NOVA ROTA: Renderiza a tela de Login no navegador
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # O Jinja2 pega o arquivo login.html e renderiza na tela
    return templates.TemplateResponse("login.html", {"request": request})

# Mude de:
@app.get("/registro", response_class=HTMLResponse)
def registro_page(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

# Para: (Lembre de adicionar o banco de dados 'db: Session = Depends(get_db)')
@app.get("/registro", response_class=HTMLResponse)
def registro_page(request: Request, db: Session = Depends(get_db)):
    # Busca no banco de dados todo mundo que tem o is_gestor marcado como True
    gestores = db.query(user.User).filter(user.User.is_gestor == True).all()
    
    # Envia essa lista para o HTML
    return templates.TemplateResponse("registro.html", {"request": request, "gestores": gestores})


@app.get("/painel", response_class=HTMLResponse)
def painel_page(request: Request, db: Session = Depends(get_db)): # <-- Adicionamos a conexão com o banco aqui!
    # 1. Verifica quem está logado
    nome_usuario = request.cookies.get("usuario_logado")
    
    if not nome_usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # 2. Busca o usuário no banco para pegar o ID dele
    usuario = db.query(user.User).filter(user.User.nome == nome_usuario).first()

    # 3. Busca todas as metas que pertencem a este usuário
    if usuario:
        minhas_metas = db.query(Meta).filter(Meta.user_id == usuario.id).all()
        total_metas = len(minhas_metas)
    else:
        minhas_metas = []
        total_metas = 0
        
    # 4. Envia o total e a lista de metas para o HTML!
    return templates.TemplateResponse(
        "painel.html", 
        {
            "request": request, 
            "usuario": nome_usuario, 
            "total_metas": total_metas,
            "metas": minhas_metas
        }
    )

# ROTA PROTEGIDA: Renderiza a tela de criar nova meta
@app.get("/metas/nova", response_class=HTMLResponse)
def nova_meta_page(request: Request):
    # Verifica o "crachá" do usuário
    usuario = request.cookies.get("usuario_logado")
    
    # Se não estiver logado, chuta para o login
    if not usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    # Se estiver logado, mostra a página do formulário
    return templates.TemplateResponse("nova_meta.html", {"request": request, "usuario": usuario})
