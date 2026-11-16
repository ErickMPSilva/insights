from uuid import uuid4

import pytest
from core.db import app_engine
from core.models import Membership, Tenant, User
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


@pytest.fixture
def session():
    """Sessão que desfaz tudo no final: o banco fica limpo após cada teste."""
    with Session(app_engine()) as s:
        s.begin()
        yield s
        s.rollback()


def _new_tenant() -> Tenant:
    return Tenant(
        name="Loja Teste",
        slug=f"store-{uuid4().hex[:8]}",
        segment="retail",
        metric_pack="retail@1",
    )


def _new_user(email: str | None = None) -> User:
    return User(
        email=email or f"{uuid4().hex[:8]}@test.com",
        name="Fulano",
        password_hash="fake-hash-for-tests",
    )


def test_invalid_role_is_rejected(session):
    tenant, user = _new_tenant(), _new_user()
    session.add_all([tenant, user])
    session.flush()
    _set_tenant(session, tenant.id)

    session.add(Membership(tenant_id=tenant.id, user_id=user.id, role="superadmin"))
    with pytest.raises(IntegrityError, match="ck_memberships_role"):
        session.flush()


def test_uppercase_email_is_rejected(session):
    session.add(_new_user(email="Erick@Test.com"))
    with pytest.raises(IntegrityError, match="ck_users_email_lowercase"):
        session.flush()


def test_user_without_password_is_rejected(session):
    session.add(User(email=f"{uuid4().hex[:8]}@test.com", name="Sem Senha"))
    with pytest.raises(IntegrityError, match="password_hash"):
        session.flush()


def test_create_tenant_user_and_membership(session):
    tenant, user = _new_tenant(), _new_user()
    session.add_all([tenant, user])
    session.flush()
    _set_tenant(session, tenant.id)

    session.add(Membership(tenant_id=tenant.id, user_id=user.id, role="owner"))
    session.flush()

    membership = session.scalars(select(Membership).where(Membership.user_id == user.id)).one()
    assert membership.tenant_id == tenant.id
    assert tenant.plan == "trial"


def _set_tenant(session, tenant_id) -> None:
    """Carimba o tenant na transação do teste (o mesmo que o tenant_session faz)."""
    session.execute(
        text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )
