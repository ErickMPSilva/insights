from collections.abc import Callable, Iterator
from uuid import UUID, uuid4

import pytest
from core.db import app_engine
from core.models import Tenant, User
from core.security import hash_password
from sqlalchemy import text
from sqlalchemy.orm import Session

DEFAULT_PASSWORD = "test-password-123"


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Sessão que desfaz tudo no final: os testes de service não deixam rastro no banco."""
    with Session(app_engine()) as session:
        session.begin()
        yield session
        session.rollback()


@pytest.fixture
def set_context(db_session: Session) -> Callable[[str, UUID | None], None]:
    """
    Define o contexto de RLS da transação do teste, como as sessões do core fazem.
    set_context("tenant_id", tenant.id) / set_context("user_id", user.id)
    set_context("tenant_id", None) limpa o contexto.
    """

    def _set(key: str, value: UUID | None) -> None:
        db_session.execute(
            text("SELECT set_config(:key, :value, true)"),
            {"key": f"app.{key}", "value": str(value) if value else ""},
        )

    return _set


@pytest.fixture
def password() -> str:
    """Senha padrão dos usuários criados pelo make_user."""
    return DEFAULT_PASSWORD


@pytest.fixture
def make_tenant(db_session: Session) -> Callable[..., Tenant]:
    def _make(name: str = "Loja Teste") -> Tenant:
        tenant = Tenant(
            name=name,
            slug=f"store-{uuid4().hex[:8]}",
            segment="retail",
            metric_pack="retail@1",
        )
        db_session.add(tenant)
        db_session.flush()
        return tenant

    return _make


@pytest.fixture
def make_user(db_session: Session, password: str) -> Callable[..., User]:
    def _make() -> User:
        user = User(
            email=f"{uuid4().hex[:8]}@test.com",
            name="Test User",
            password_hash=hash_password(password),
        )
        db_session.add(user)
        db_session.flush()
        return user

    return _make
