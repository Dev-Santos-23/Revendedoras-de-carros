from fastapi import APIRouter, Depends, HTTPException
from schemas import UsuarioSchema, LoginSchema
from conection_banco import get_db
from psycopg2.extensions import connection
from auth.security import senha_hash, pwt_context, verificar_senha
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
    return{
        "mensagem": "Login realizado com sucesso",
        "Usuário": {
            "id": usuario_banco[0],
            "nome": usuario_banco[1],
            "email": usuario_banco[3]
        }
    }
    
        
#Verificação de cadastro e compra de carros

auth_routers.post("/Compra_automoveis")
async def buy_car(usuario : UsuarioSchema, bd : connection = Depends(get_db)):
    ...