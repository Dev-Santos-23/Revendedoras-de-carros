from fastapi import APIRouter, Depends
from conection_banco import get_db
from psycopg2.extensions import connection
from auth.jwt import get_current_user
from func_in_the_banc import carros_disponiveis_para_compra

car_routers = APIRouter(prefix="/carros", tags=["Listagem"])

#Listar carros disponiveis
@car_routers.get("/Carros_Disponiveis")
def carros_disponiveis(
    # user_id: int = Depends(get_current_user),
    db: connection = Depends(get_db)
    ):

    return carros_disponiveis_para_compra(db)


#buscar um carro específico
