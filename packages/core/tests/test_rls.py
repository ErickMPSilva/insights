from types import SimpleNamespace
from uuid import uuid4

import pytest
from core.db import system_session, tenant_session, user_session
from core.models import Membership, Tenant, User
from sqlalchemy import delete, select, text, update
from sqlalchemy.exc import ProgrammingError


def _new_tenant() -> Tenant:
    return Tenant(
        name="Loja Teste",
        slug=f"store-{uuid4().hex[:8]}",
        segment="retail",
        metric_pack="retail@1",
    )


def _new_user() -> User:
    return User(
        email=f"{uuid4().hex[:8]}@test.com",
        name="Fulano",
        password_hash="fake-hash-for-tests",
    )


@pytest.fixture
def two_tenants():
    """
    Cria dois tenants (A e B), cada um com um usuário dono.
    Os dados são GRAVADOS (commit), porque o teste usa várias sessões.
    No final, apaga tudo.
    """
    with system_session() as s:
        tenant_a, tenant_b = _new_tenant(), _new_tenant()
        user_a, user_b = _new_user(), _new_user()
        s.add_all([tenant_a, tenant_b, user_a, user_b])
        s.flush()
        data = SimpleNamespace(
            tenant_a=tenant_a.id,
            tenant_b=tenant_b.id,
            user_a=user_a.id,
            user_b=user_b.id,
        )

    with tenant_session(data.tenant_a) as s:
        s.add(Membership(tenant_id=data.tenant_a, user_id=data.user_a, role="owner"))
    with tenant_session(data.tenant_b) as s:
        s.add(Membership(tenant_id=data.tenant_b, user_id=data.user_b, role="owner"))

    yield data

    # limpeza: apagar o tenant apaga as memberships em cascata
    with system_session() as s:
        s.execute(delete(Tenant).where(Tenant.id.in_([data.tenant_a, data.tenant_b])))
        s.execute(delete(User).where(User.id.in_([data.user_a, data.user_b])))


def test_tenant_sees_only_its_own_rows(two_tenants):
    with tenant_session(two_tenants.tenant_a) as s:
        tenant_ids = {r.tenant_id for r in s.scalars(select(Membership))}

    assert tenant_ids == {two_tenants.tenant_a}


def test_without_context_sees_nothing(two_tenants):
    with system_session() as s:
        rows = s.scalars(select(Membership)).all()

    assert rows == []


def test_cannot_insert_into_another_tenant(two_tenants):
    with pytest.raises(ProgrammingError, match="row-level security"):
        with tenant_session(two_tenants.tenant_a) as s:
            s.add(
                Membership(
                    tenant_id=two_tenants.tenant_b,
                    user_id=two_tenants.user_a,
                    role="admin",
                )
            )
            s.flush()


def test_cannot_update_another_tenants_rows(two_tenants):
    with tenant_session(two_tenants.tenant_a) as s:
        result = s.execute(
            update(Membership)
            .where(Membership.tenant_id == two_tenants.tenant_b)
            .values(role="viewer")
        )

    assert result.rowcount == 0


def test_user_session_sees_only_own_memberships(two_tenants):
    with user_session(two_tenants.user_a) as s:
        user_ids = [r.user_id for r in s.scalars(select(Membership))]

    assert user_ids == [two_tenants.user_a]


def test_user_session_cannot_write(two_tenants):
    with pytest.raises(ProgrammingError, match="row-level security"):
        with user_session(two_tenants.user_a) as s:
            s.add(
                Membership(
                    tenant_id=two_tenants.tenant_a,
                    user_id=two_tenants.user_a,
                    role="viewer",
                )
            )
            s.flush()


def test_rls_is_forced_and_app_cannot_bypass():
    with system_session() as s:
        bypass = s.execute(
            text("SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user")
        ).scalar_one()
        forced = s.execute(
            text("SELECT relforcerowsecurity FROM pg_class WHERE relname = 'memberships'")
        ).scalar_one()

    assert bypass is False
    assert forced is True
