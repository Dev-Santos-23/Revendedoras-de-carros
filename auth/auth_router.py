from fastapi import APIRouter, Depends, HTTPException
from schemas import UsuarioSchema, LoginSchema, CompraSchema
from conection_banco import get_db
from psycopg2.extensions import connection
from auth.security import senha_hash, pwt_context, verificar_senha
from auth.jwt import criar_token, get_current_user

auth_routers = APIRouter(prefix="/auth", tags=["Autenticacao"])


#Verifica no banco se email ja está cadastrado
def consulta_banco(usuario_email, db_banc: connection = Depends(get_db)):
    db_banc_conn = db_banc.cursor()
    db_banc_conn.execute(
        "SELECT 1 FROM usuarios WHERE email = %s", (usuario_email,)
    )
    resultado = db_banc_conn.fetchone() 
    db_banc_conn.close()
    return resultado is not None

def buscar_email_usuario(email: str, db):
    cursor = db.cursor()
    cursor.execute(
        """ SELECT id, nome, telefone, email, senha 
            FROM usuarios
            WHERE email = %s
        """,
        (email,)
    )

    usuario = cursor.fetchone()
    cursor.close()

    return usuario 

#Buscando carro no Banco
def buscar_carro(id_carro: int, db: connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """SELECT cor, marca, modelo, preco 
        FROM registro_carros 
        WHERE id = %s""",
        (id_carro,)
    )

    carro = cursor.fetchone()
    cursor.close()

    return carro

#inserindo carro comprado no historico
def insert_car_in_historic(
        id_compra: int,
        carro_id : int, db: connection
        ):
    cursor = db.cursor()
    cursor.execute(
        """ SELECT * from registro_carros
            WHERE id = %s
        """,
        (carro_id,)
    )

    carro = cursor.fetchone()

    if carro is None:
        cursor.close()
        raise ValueError("Carro não encontrado!")

    cursor.execute (
        """
        INSERT INTO historico_de_carros_comprados(
        id_compra,
        id_carro_original,
        cor,
        marca,
        modelo,
        ano_de_fabricacao,
        preco,
        quilometragem,
        combustivel,
        cambio)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
          id_compra, carro[0], carro[1], carro[2], carro[3], carro[4],
          carro[5], carro[6], carro[7], carro[8]
          )
    )

    cursor.execute(
        """ DELETE FROM registro_carros
            WHERE id = %s
        """,
        (carro_id,)
    ) 
    ...

#Inserindo compra no banco
def insert_car_banc(
    user_id: int,
    carro_id: int,
    db: connection
):
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO compras_ (user_id, id_carro)
        VALUES (%s, %s)
        RETURNING id
        """,
        (user_id, carro_id)
    )

    id_compra = cursor.fetchone()[0]

    cursor.close()

    return id_compra


#deletando carros

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
auth_routers.post("/comprar_automóvel")
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

        id_compra = insert_car_banc (
            user_id,
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

    except Exception:
        bd.rollback()
        raise HTTPException (
            status_code=400,
            detail="Erro ao realizar a compra"
        )
    