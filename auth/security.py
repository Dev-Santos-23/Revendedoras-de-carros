from passlib.context import CryptContext

pwt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

senha_ = "1234567"

def senha_hash(senha: str) -> str:
    return pwt_context.hash(senha)

def verificar_senha(senha: str, senha_hash: str) ->bool:
    return pwt_context.verify(senha, senha_hash)


