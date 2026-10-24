from uuid import uuid4

from core.db import app_engine, tenant_session
from core.settings import get_settings
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_settings_load_from_env():
    settings = get_settings()
    assert "5438" in settings.app_database_url


def test_connects_as_app_user_and_sets_tenant():
    tenant_id = uuid4()
    with tenant_session(tenant_id) as session:
        current_user = session.execute(text("SELECT current_user")).scalar_one()
        current_tenant = session.execute(
            text("SELECT current_setting('app.tenant_id')")
        ).scalar_one()

    assert current_user == "app"
    assert current_tenant == str(tenant_id)


def test_tenant_does_not_leak_to_next_transaction():
    with tenant_session(uuid4()):
        pass

    # nova transação, provavelmente na MESMA conexão do pool
    with Session(app_engine()) as session:
        current_tenant = session.execute(
            text("SELECT current_setting('app.tenant_id', true)")
        ).scalar_one()

    assert current_tenant in (None, "")
