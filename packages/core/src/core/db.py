from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from core.settings import get_settings


@lru_cache
def app_engine() -> Engine:
    """Banco app (control plane), conectando como o usuário 'app' (sujeito ao RLS)."""
    return create_engine(get_settings().app_database_url, pool_pre_ping=True)


@lru_cache
def warehouse_engine() -> Engine:
    """Banco warehouse (data plane)."""
    return create_engine(get_settings().warehouse_database_url, pool_pre_ping=True)


@contextmanager
def _session_with_context(**context: str) -> Iterator[Session]:
    """
    Abre uma transação no banco app e define variáveis de contexto
    (app.tenant_id, app.user_id) que valem só até o fim da transação.
    """
    with Session(app_engine()) as session, session.begin():
        for key, value in context.items():
            session.execute(
                text("SELECT set_config(:key, :value, true)"),
                {"key": f"app.{key}", "value": value},
            )
        yield session


@contextmanager
def tenant_session(tenant_id: UUID) -> Iterator[Session]:
    """
    Sessão do dia a dia: tudo o que rodar dentro do 'with' só enxerga
    e só altera dados deste tenant (garantido pelo RLS).
    """
    with _session_with_context(tenant_id=str(tenant_id)) as session:
        yield session


@contextmanager
def user_session(user_id: UUID) -> Iterator[Session]:
    """
    Sessão do login/escolha de empresa: só LÊ os vínculos (memberships)
    do próprio usuário, em todos os tenants. Não enxerga dados de tenant.
    """
    with _session_with_context(user_id=str(user_id)) as session:
        yield session


@contextmanager
def system_session() -> Iterator[Session]:
    """
    Sessão sem contexto, para tabelas globais (tenants, users).
    Em tabelas com RLS, não enxerga nada.
    """
    with Session(app_engine()) as session, session.begin():
        yield session