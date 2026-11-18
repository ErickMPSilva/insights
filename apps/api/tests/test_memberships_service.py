from api.modules.memberships.service import list_membership
from core.models import Membership


def test_lists_only_memberships_of_the_session_tenant(
    db_session, set_context, make_tenant, make_user
):
    tenant_a, tenant_b = make_tenant(), make_tenant()
    user_a, user_b = make_user(), make_user()

    set_context("tenant_id", tenant_a.id)
    db_session.add(Membership(tenant_id=tenant_a.id, user_id=user_a.id, role="owner"))
    db_session.flush()

    set_context("tenant_id", tenant_b.id)
    db_session.add(Membership(tenant_id=tenant_b.id, user_id=user_b.id, role="owner"))
    db_session.flush()

    set_context("tenant_id", tenant_a.id)
    result = list_membership(db_session)

    assert [m.user_id for m in result] == [user_a.id]
