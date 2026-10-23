from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from core.settings import get_settings


@lru_cache
def app_engine() -> Engine:
    return create_engine(get_settings().app_database_url, pool_pre_ping=True)


@lru_cache
def warehouse_engine() -> Engine:
    return create_engine(get_settings().warehouse_database_url, pool_pre_ping=True)


@contextmanager
def tenant_session(tenant_id: UUID) -> Iterator[Session]:
    """
    Abre uma transação no banco app já 'carimbada' com o tenant.

    Tudo o que rodar dentro do 'with' só enxerga os dados desse tenant
    (quando as políticas de RLS estiverem ativas, no Passo 6).
    Ao sair do 'with': commit se deu certo, rollback se deu erro.
    """
    with Session(app_engine()) as session, session.begin():
        session.execute(
            text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": str(tenant_id)},
        )
        yield session


@contextmanager
def system_session() -> Iterator[Session]:
    """
    Transação sem tenant, para tabelas globais (users, tenants)
    e para descobrir a quais tenants um usuário pertence.
    """
    with Session(app_engine()) as session, session.begin():
        yield session
