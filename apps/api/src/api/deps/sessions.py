from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from core.db import system_session, tenant_session, user_session
from core.repositories import MembershipRepository
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from api.deps.auth import CurrentUserId


def get_system_session() -> Iterator[Session]:
    """Sessão sem contexto: tabelas globais (users, tenants). Uso: login."""
    with system_session() as session:
        yield session


def get_user_session(user_id: CurrentUserId) -> Iterator[Session]:
    """Sessão do usuário logado: lê os próprios vínculos em todos os tenants. Uso: /me."""
    with user_session(user_id) as session:
        yield session


def get_tenant_session(
    user_id: CurrentUserId,
    x_tenant_id: Annotated[UUID, Header()],
) -> Iterator[Session]:
    """Valida o acesso ao tenant do header X-Tenant-Id e entrega uma sessão sob RLS."""
    with user_session(user_id) as s:
        is_member = MembershipRepository(s).is_active_member(x_tenant_id, user_id)

    if not is_member:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No access to this tenant")

    with tenant_session(x_tenant_id) as session:
        yield session


SystemSession = Annotated[Session, Depends(get_system_session)]
UserSession = Annotated[Session, Depends(get_user_session)]
TenantSession = Annotated[Session, Depends(get_tenant_session)]
