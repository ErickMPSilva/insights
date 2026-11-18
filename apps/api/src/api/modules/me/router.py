from fastapi import APIRouter, HTTPException, status

from api.deps.auth import CurrentUserId
from api.deps.sessions import UserSession
from api.modules.me.schemas import MeOut
from api.modules.me.service import UserNotFoundError, get_profile

router = APIRouter(prefix="/me", tags=["Me"])


@router.get("/")
def me(user_id: CurrentUserId, session: UserSession) -> MeOut:
    try:
        return get_profile(session=session, user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        ) from None  # noqa: E501
