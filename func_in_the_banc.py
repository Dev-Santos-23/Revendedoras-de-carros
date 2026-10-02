from fastapi import APIRouter, Depends
from conection_banco import get_db
from psycopg2.extensions import connection


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
        WHERE id = %s
        AND disponivel = true 
        """,
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
        """
        UPDATE registro_carros
        SET disponivel = FALSE
        WHERE id = %s
        """,
        (carro_id,)
)
    ...

#Inserindo compra no banco
def insert_car_banc(
    user_id: int,
    db: connection
):
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO compras_ (id_usuario)
        VALUES (%s)
        RETURNING id
        """,
        (user_id,)
    )

    id_compra = cursor.fetchone()[0]

    cursor.close()

    return id_compra

def adicionar_carro_compra(
    id_compra: int,
    id_carro: int,
    db: connection
):
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO compra_carros (id_compra, id_carro)
        VALUES (%s, %s)
        """,
        (id_compra, id_carro)
    )

    cursor.close()

def carros_disponiveis_para_compra(bd):
    cursor_db = bd.cursor()

    cursor_db.execute(
        """
        SELECT * FROM registro_carros WHERE disponivel = TRUE
        """
    )

    carros = cursor_db.fetchall()
    cursor_db.close()

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
                "disponivel": carro[10],
            }
        for carro in carros
        ]
    
    return {
        "Carros disponiveis para comprar":
        resultado
    }

def buscar_um_carro(id_car, db):
    cursor_db = db.cursor()
    cursor_db.execute(
        """
        SELECT * FROM registro_carros
        WHERE id = %s AND disponivel = TRUE
        """,
        (id_car,)
    )

    carro = cursor_db.fetchone()
    cursor_db.close()

    if carro is None:
        return None

    return {
        "Carro encontrado": {
            "ID": carro[0],
            "Cor": carro[1],
            "Marca": carro[2],
            "Nome": carro[3],
            "Ano de Fabricação": carro[4],
            "Preço": float(carro[5]),
            "Quilometragem": carro[6],
            "Combustível": carro[7],
            "Câmbio": carro[8],
            "disponivel": carro[10],
        }
    }

def consulta_compras_de_um_usuario( db):
    cursor_db = db.cursor()
    cursor_db.execute(
        """
        SELECT 
        usuarios.nome,
        compras_.id AS compra_id,
        registro_carros.marca,
        registro_carros.modelo,
        registro_carros.preco
        FROM compras_
        JOIN usuarios
        ON compras_.id_usuario = usuarios.id
        JOIN compra_carros
        ON compra_carros.id_compra = compras_.id
        JOIN registro_carros
        ON compra_carros.id_carro = registro_carros.id;
        """
    )

    compras_usuarios = cursor_db.fetchall()
    cursor_db.close()

    return compras_usuarios

def consulta_carros_comprados(db):
    db_cursor = db.cursor()
    db_cursor.execute(
        """
        SELECT * FROM historico_de_carros_comprados;
        """
    )

    carros = db_cursor.fetchone()
    db_cursor.close()

    if carros is None:
        return None

    return {
        "Carros encontrado": {
            "ID": carros[2],
            "Cor": carros[3],
            "Marca": carros[4],
            "Nome": carros[5],
            "Ano de Fabricação": carros[6],
            "Preço": float(carros[7]),
            "Quilometragem": carros[8],
            "Combustível": carros[9],
            "Câmbio": carros[10],
        }
    }

