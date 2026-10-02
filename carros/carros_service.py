from fastapi import APIRouter, Depends, HTTPException
from conection_banco import get_db
from psycopg2.extensions import connection
from auth.jwt import get_current_user
from func_in_the_banc import carros_disponiveis_para_compra, buscar_um_carro, consulta_compras_de_um_usuario

car_routers = APIRouter(prefix="/carros", tags=["Listagem"])

#Listar carros disponiveis
@car_routers.get("/Carros_Disponiveis")
def carros_disponiveis(
    # user_id: int = Depends(get_current_user),
    db: connection = Depends(get_db)
    ):

    return carros_disponiveis_para_compra(db)


#buscar um carro específico
@car_routers.get("/busca_unica")
def carro_unico(
    id_carro: int,
    db: connection = Depends(get_db)
    ):

    carro_ = buscar_um_carro(id_carro, db)

    if carro_ is None:
        raise HTTPException(
            status_code=404,
            detail="ID não encontado no banco!"
        )

    return carro_

#Consulta compras dos usuario
@car_routers.get("/Registro_de_compras_do_usuario")
def buscar_usario_compras(db: connection = Depends(get_db)):

    return consulta_compras_de_um_usuario(db)
    ...