from fastapi import APIRouter, Depends
from psycopg2.extensions import connection
from conection_banco import get_db
from auth.jwt import get_current_user


order_routers = APIRouter(prefix="/order", tags=["Pedido"])

@order_routers.get("/Carros_a_venda")
async def pedido_carros_banco(
    db: connection = Depends(get_db),
    user_id : int = Depends(get_current_user)
    ):

    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM registro_carros"
    )
    carros = cursor.fetchall()
    cursor.close()

    resultado = [
            {
                "ID": carro[0],
                "Cor": carro[1],
                "Marca": carro[2],
                "Nome": carro[3],
                "Ano de Fabricação": carro[4],
                "Preço": float(carro[5]),
                "Quilometragem": carro[6],
                "Combustível": carro[7],
                "Câmbio": carro[8],
            }
        for carro in carros
        ]
    
    return {
        "Estoque de carros":
        resultado
    }

