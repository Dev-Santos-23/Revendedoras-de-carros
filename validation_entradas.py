from psycopg2.extensions import connection
from conection_banco import get_db
from fastapi import Depends
from schemas import UsuarioSchema
from auth.security import senha_hash, verificar_senha

# def consulta_banco(usuario : UsuarioSchema ,db_banc: connection = Depends(get_db)):
#     db_banc_conn = db_banc.cursor()
#     cmd = "SELECT 1 FRON usuarios WHERE email = %s", usuario.email
#     db_banc_conn.execute(cmd)
#     if db_banc_conn =="1":
#         raise ValueError ("Esse email já esta cadastrado")
#     db_banc_conn.close()



      

