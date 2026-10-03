from fastapi import APIRouter, Depends, HTTPException
from schemas import UsuarioSchema, LoginSchema, CompraSchema
from conection_banco import get_db
from psycopg2.extensions import connection
from auth.security import senha_hash, pwt_context, verificar_senha
from auth.jwt import criar_token, get_current_user
from func_in_the_banc import consulta_banco, buscar_carro,buscar_email_usuario, insert_car_banc, insert_car_in_historic, adicionar_carro_compra

auth_routers = APIRouter(prefix="/auth", tags=["Autenticacao"])

#Adicionando usuários no banco e validando email
@auth_routers.post("/create_usuario")
async def auth(usuario: UsuarioSchema, db : connection = Depends(get_db)):

    if consulta_banco(usuario.email, db):
        raise HTTPException (
            status_code=400,
            detail="Email ja cadastrado!"
        )
    
    hash_senha = senha_hash(usuario.senha)
                      
    cursor = db.cursor()

    cursor.execute (
        "INSERT INTO usuarios(nome, telefone, email, senha) VALUES (%s, %s, %s, %s)", 
        (usuario.nome, usuario.telefone, usuario.email, hash_senha)
    )
    db.commit()
    cursor.close()
    return {"mensagem": "Usuário criado com sucesso!"}


#login
@auth_routers.post("/login")
async def login_user( usuario : LoginSchema, db: connection = Depends(get_db)):
    usuario_banco = buscar_email_usuario(usuario.email, db)
    if usuario_banco is None:
        raise HTTPException (
            status_code=400,
            detail= "Email ou senha inválidos"
        )

    senha_verificada = usuario_banco[4]

    if not verificar_senha(
        usuario.senha, senha_verificada
    ):
        raise HTTPException (
            status_code=401,
            detail="Email ou senha inválidas"
        )

    token = criar_token(
        usuario_banco[0]
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
      
#Verificação de cadastro e compra de carros
@auth_routers.post("/comprar_automóvel")
async def buy_car(
        compra : CompraSchema,
        bd : connection = Depends(get_db),
        user_id : int = Depends(get_current_user)
    ):

    try:
        carro = buscar_carro(compra.id_carro, bd)

        if carro is None:
            raise HTTPException(
                status_code=404,
                detail="Carro não encontrado"
            )

        if carro[4] is False:
            raise HTTPException(
                status_code=404,
                detail="Carro indisponivel para compra"
            )

        id_compra = insert_car_banc (
            user_id,
            bd
        )


        adicionar_carro_compra(
            id_compra,
            compra.id_carro,
            bd
        )

        insert_car_in_historic(
            id_compra,
            compra.id_carro,
            bd
            )

        bd.commit()

        return {
            "Mensagem": "Compra realizada com sucesso!",
            "usuario_id": user_id,
            "carro" : {
                "modelo" : carro[2],
                "marca" : carro[1],
                "cor": carro[0],
                "preco" : carro[3],
            }
        }
    except HTTPException:
        bd.rollback()
        raise

    except Exception as e :
        bd.rollback()
        print("Erro:", e)
        raise

