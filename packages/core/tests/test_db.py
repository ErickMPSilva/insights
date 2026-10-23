from uuid import uuid4

from core.db import app_engine, tenant_session
from core.settings import get_settings
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_settings_carregam_do_env():
    settings = get_settings()
    assert "5438" in settings.app_database_url


def test_conecta_como_usuario_app_e_carimba_tenant():
    tenant_id = uuid4()
    with tenant_session(tenant_id) as session:
        usuario = session.execute(text("SELECT current_user")).scalar_one()
        tenant = session.execute(text("SELECT current_setting('app.tenant_id')")).scalar_one()

    assert usuario == "app"
    assert tenant == str(tenant_id)


def test_tenant_nao_vaza_para_a_proxima_transacao():
    with tenant_session(uuid4()):
        pass

    # nova transação, provavelmente na MESMA conexão do pool
    with Session(app_engine()) as session:
        tenant = session.execute(text("SELECT current_setting('app.tenant_id', true)")).scalar_one()

    assert tenant in (None, "")
