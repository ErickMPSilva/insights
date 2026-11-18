from datetime import UTC, datetime
from uuid import uuid4

import pytest
from api.modules.me.service import UserNotFoundError, get_profile
from core.models import Membership


def test_profile_lists_only_accepted_tenants_in_name_order(
    db_session, set_context, make_tenant, make_user
):
    user = make_user()
    store_b = make_tenant(name="B Store")
    store_a = make_tenant(name="A Store")
    pending = make_tenant(name="Pending Store")

    # inserir vínculos exige o tenant no contexto (WITH CHECK do RLS)
    for tenant, accepted in [(store_b, True), (store_a, True), (pending, False)]:
        set_context("tenant_id", tenant.id)
        db_session.add(
            Membership(
                tenant_id=tenant.id,
                user_id=user.id,
                role="owner",
                accepted_at=datetime.now(UTC) if accepted else None,
            )
        )
        db_session.flush()

    # agora, como no /me: sem tenant, com o usuário no contexto
    set_context("tenant_id", None)
    set_context("user_id", user.id)

    profile = get_profile(db_session, user.id)

    assert profile.user.id == user.id
    assert [t.name for t in profile.tenants] == ["A Store", "B Store"]


def test_profile_of_unknown_user_raises(db_session):
    with pytest.raises(UserNotFoundError):
        get_profile(db_session, uuid4())
