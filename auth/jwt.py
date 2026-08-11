from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import timedelta, timezone, datetime
import os

security = HTTPBearer()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def criar_token(user_id: int):
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": str(user_id),
        "exp": expiracao
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def verificar_token(token: str):

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido."
            )

        return int(user_id)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado."
        )

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    user_id = verificar_token(token)

    return user_id
    