from fastapi import APIRouter, HTTPException, status

from api.deps.sessions import SystemSession
from api.modules.auth.schemas import LoginIn, TokenOut
from api.modules.auth.service import InvalidCredentialsError, authenticate
from api.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(body: LoginIn, session: SystemSession) -> TokenOut:
    try:
        user_id = authenticate(session, body.email, body.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        ) from None  # noqa: E501

    return TokenOut(access_token=create_access_token(user_id=user_id))
