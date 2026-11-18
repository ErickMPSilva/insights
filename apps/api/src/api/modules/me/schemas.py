from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str


class TenantAccessOut(BaseModel):
    tenant_id: UUID
    name: str
    slug: str
    role: str


class MeOut(BaseModel):
    user: UserOut
    tenants: list[TenantAccessOut]
