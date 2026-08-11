from fastapi import FastAPI

app = FastAPI()

from auth.auth_router import auth_routers
from order.order_router import order_routers

app.include_router(auth_routers)
app.include_router(order_routers)

""" comando para rodar a minha api :
        uvicorn main:app --reload
"""
