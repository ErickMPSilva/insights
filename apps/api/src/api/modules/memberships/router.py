from fastapi import APIRouter

from api.deps.sessions import TenantSession
from api.modules.memberships.schemas import MembershipOut
from api.modules.memberships.service import list_membership

router = APIRouter(prefix="/memberships", tags=["memberships"])


@router.get("/")
def get_memberships(session: TenantSession) -> list[MembershipOut]:
    return list_membership(session)
