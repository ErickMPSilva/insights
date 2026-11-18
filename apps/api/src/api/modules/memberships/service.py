from core.repositories import MembershipRepository
from sqlalchemy.orm import Session

from api.modules.memberships.schemas import MembershipOut


def list_membership(session: Session) -> list[MembershipOut]:
    rows = MembershipRepository(session).list_for_current_tenant()
    return [MembershipOut.model_validate(row) for row in rows]
