from fastapi import FastAPI, Form, Request, status, Depends
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


# ROTA PROTEGIDA: Renderiza o Painel principal
@app.get("/painel", response_class=HTMLResponse)
def painel_page(request: Request, db: Session = Depends(get_db)):
    nome_usuario = request.cookies.get("usuario_logado")
    
    if not nome_usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Busca o usuário logado
    usuario = db.query(user.User).filter(user.User.nome == nome_usuario).first()

    # 1. Busca as metas
    if usuario:
        minhas_metas = db.query(Meta).filter(Meta.user_id == usuario.id).all()
        total_metas = len(minhas_metas)
    else:
        minhas_metas = []
        total_metas = 0

    # 2. LÓGICA DE HIERARQUIA: 
    # Conta a equipe (se for gestor)
    total_equipe = db.query(user.User).filter(user.User.gestor_id == usuario.id).count() if usuario and usuario.is_gestor else 0
    
    # Descobre quem é o chefe dele (se for colaborador ou sub-gestor)
    nome_meu_gestor = "Não vinculado a um gestor"
    if usuario and usuario.gestor_id:
        meu_gestor_obj = db.query(user.User).filter(user.User.id == usuario.gestor_id).first()
        if meu_gestor_obj:
            nome_meu_gestor = meu_gestor_obj.nome

    # Envia tudo para o HTML
    return templates.TemplateResponse(
        "painel.html", 
        {
            "request": request, 
            "usuario": nome_usuario, 
            "usuario_obj": usuario, # Enviamos o usuário completo para o HTML saber se é gestor
            "total_metas": total_metas,
            "metas": minhas_metas,
            "total_equipe": total_equipe,
            "nome_meu_gestor": nome_meu_gestor
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

# ROTA PROTEGIDA: Renderiza a página da equipe do gestor
@app.get("/equipe", response_class=HTMLResponse)
def equipe_page(request: Request, db: Session = Depends(get_db)):
    # 1. Verifica quem está logado
    nome_usuario = request.cookies.get("usuario_logado")
    if not nome_usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # 2. Busca o gestor no banco
    gestor = db.query(user.User).filter(user.User.nome == nome_usuario).first()
    
    # 3. Segurança: Se não for gestor, manda de volta pro painel
    if not gestor or not gestor.is_gestor:
        return RedirectResponse(url="/painel", status_code=status.HTTP_303_SEE_OTHER)

    # 4. Busca todos os usuários que têm o ID deste gestor!
    minha_equipe = db.query(user.User).filter(user.User.gestor_id == gestor.id).all()

    # 5. Manda a lista para a tela nova
    return templates.TemplateResponse(
        "equipe.html", 
        {"request": request, "usuario": nome_usuario, "equipe": minha_equipe}
    )
# NOVA ROTA: O Gestor adiciona um membro à equipe
@app.post("/equipe/adicionar")
def adicionar_membro_equipe(
    request: Request,
    username_colaborador: str = Form(...), # Recebe o que o gestor digitou
    db: Session = Depends(get_db)
):
    # 1. Verifica quem é o gestor logado
    nome_usuario = request.cookies.get("usuario_logado")
    if not nome_usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    gestor = db.query(user.User).filter(user.User.nome == nome_usuario).first()

    # 2. Vai no banco procurar o colaborador que o gestor quer adicionar
    colaborador = db.query(user.User).filter(   user.User.username == username_colaborador).first()

    # Se digitar o nome errado, devolve a tela com erro
    if not colaborador:
        minha_equipe = db.query(user.User).filter(user.User.gestor_id == gestor.id).all()
        return templates.TemplateResponse(
            "equipe.html", 
            {"request": request, "usuario": nome_usuario, "equipe": minha_equipe, "erro": f"O usuário '{username_colaborador}' não foi encontrado."}
        )

    # 3. A MÁGICA ACONTECE AQUI: Atualiza o chefe desse colaborador!
    colaborador.gestor_id = gestor.id
    db.commit()

    # Atualiza a página com sucesso
    return RedirectResponse(url="/equipe", status_code=status.HTTP_303_SEE_OTHER)

# in app/main.py, after the other /equipe routes

@app.get("/equipe/{colab_id}/metas", response_class=HTMLResponse)
def metas_colaborador(
    request: Request,
    colab_id: int,
    db: Session = Depends(get_db)
):
    nome_usuario = request.cookies.get("usuario_logado")
    if not nome_usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    gestor = db.query(user.User).filter(user.User.nome == nome_usuario).first()
    if not gestor or not gestor.is_gestor:
        return RedirectResponse(url="/painel", status_code=status.HTTP_303_SEE_OTHER)

    colaborador = db.query(user.User).filter(
        user.User.id == colab_id,
        user.User.gestor_id == gestor.id
    ).first()
    if not colaborador:
        # opcional: flash de erro ou simplesmente voltar
        return RedirectResponse(url="/equipe", status_code=status.HTTP_303_SEE_OTHER)

    metas = db.query(Meta).filter(Meta.user_id == colaborador.id).all()
    return templates.TemplateResponse(
        "metas_colaborador.html",
        {
            "request": request,
            "usuario": nome_usuario,
            "colaborador": colaborador,
            "metas": metas,
        }
    )