from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from api.main import app
from core.db import system_session, tenant_session
from core.models import Membership, Tenant, User
from core.security import hash_password
from fastapi.testclient import TestClient
from sqlalchemy import delete


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def account():
    """Um usuário dono de um tenant, mais um segundo tenant ao qual ele NÃO pertence."""
    password = "test-password-123"
    with system_session() as s:
        tenant = Tenant(
            name="Loja API",
            slug=f"api-{uuid4().hex[:8]}",
            segment="retail",
            metric_pack="retail@1",
        )
        other = Tenant(
            name="Outra Loja",
            slug=f"api-{uuid4().hex[:8]}",
            segment="retail",
            metric_pack="retail@1",
        )
        user = User(
            email=f"{uuid4().hex[:8]}@test.com",
            name="API User",
            password_hash=hash_password(password),
        )
        s.add_all([tenant, other, user])
        s.flush()
        data = SimpleNamespace(
            tenant_id=tenant.id,
            other_tenant_id=other.id,
            user_id=user.id,
            email=user.email,
            password=password,
        )

    with tenant_session(data.tenant_id) as s:
        s.add(
            Membership(
                tenant_id=data.tenant_id,
                user_id=data.user_id,
                role="owner",
                accepted_at=datetime.now(UTC),
            )
        )

    yield data

    with system_session() as s:
        s.execute(delete(Tenant).where(Tenant.id.in_([data.tenant_id, data.other_tenant_id])))
        s.execute(delete(User).where(User.id == data.user_id))


def _auth_headers(client: TestClient, account) -> dict[str, str]:
    response = client.post(
        "/auth/login", json={"email": account.email, "password": account.password}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_login_with_wrong_password_is_rejected(client, account):
    response = client.post("/auth/login", json={"email": account.email, "password": "wrong"})
    assert response.status_code == 401


def test_me_requires_token(client):
    assert client.get("/me").status_code == 401


def test_me_lists_user_tenants(client, account):
    response = client.get("/me", headers=_auth_headers(client, account))

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == account.email
    assert "password_hash" not in body["user"]
    assert [t["tenant_id"] for t in body["tenants"]] == [str(account.tenant_id)]


def test_memberships_of_own_tenant(client, account):
    headers = _auth_headers(client, account) | {"X-Tenant-Id": str(account.tenant_id)}
    response = client.get("/memberships", headers=headers)

    assert response.status_code == 200
    assert [m["user_id"] for m in response.json()] == [str(account.user_id)]


def test_memberships_of_another_tenant_is_forbidden(client, account):
    headers = _auth_headers(client, account) | {"X-Tenant-Id": str(account.other_tenant_id)}
    assert client.get("/memberships", headers=headers).status_code == 403


def test_memberships_without_tenant_header_is_rejected(client, account):
    response = client.get("/memberships", headers=_auth_headers(client, account))
    assert response.status_code == 422
