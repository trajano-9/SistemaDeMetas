from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.meta import Meta

# Cria o roteador para gerir tudo o que envolve metas
router = APIRouter(prefix="/metas", tags=["Metas"])

@router.post("/nova")
def gravar_nova_meta(
    request: Request,
    indicador: str = Form(...),
    perspectiva: str = Form(...),
    peso: float = Form(...),
    escala_a: str = Form(...),
    escala_b: str = Form(...),
    escala_c: str = Form(...),
    escala_d: str = Form(...),
    escala_e: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Verifica quem é o utilizador logado através do cookie
    nome_usuario = request.cookies.get("usuario_logado")
    
    # Se por algum motivo o cookie se perdeu, expulsa para o login
    if not nome_usuario:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # 2. Vai à base de dados buscar os dados do utilizador logado
    usuario = db.query(User).filter(User.nome == nome_usuario).first()

    # 3. Prepara a nova meta cruzando os dados do formulário com o ID do utilizador
    nova_meta = Meta(
        indicador=indicador,
        perspectiva=perspectiva,
        peso=peso,
        escala_a=escala_a,
        escala_b=escala_b,
        escala_c=escala_c,
        escala_d=escala_d,
        escala_e=escala_e,
        status="Pendente", # Fica a aguardar aprovação do Gestor
        user_id=usuario.id # Associa a meta ao dono!
    )

    # 4. Guarda efetivamente na base de dados
    db.add(nova_meta)
    db.commit()
    db.refresh(nova_meta)

    # 5. Após gravar com sucesso, redireciona o utilizador de volta para o painel principal
    return RedirectResponse(url="/painel", status_code=status.HTTP_303_SEE_OTHER)