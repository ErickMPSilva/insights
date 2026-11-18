from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MembershipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    role: str
    accepted_at: datetime | None
    created_at: datetime
