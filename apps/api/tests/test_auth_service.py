import pytest
from api.modules.auth.service import InvalidCredentialsError, authenticate
from sqlalchemy import text


def test_authenticate_returns_user_id(db_session, make_user, password):
    user = make_user()
    assert authenticate(db_session, user.email, password) == user.id


def test_authenticate_persists_last_login(db_session, make_user, password):
    user = make_user()

    authenticate(db_session, user.email, password)
    db_session.flush()  # envia o UPDATE (dentro da transação do teste)

    stored = db_session.execute(
        text("SELECT last_login_at FROM users WHERE id = :id"), {"id": user.id}
    ).scalar_one()
    assert stored is not None


def test_authenticate_ignores_email_case(db_session, make_user, password):
    user = make_user()
    assert authenticate(db_session, user.email.upper(), password) == user.id


def test_wrong_password_raises(db_session, make_user):
    user = make_user()
    with pytest.raises(InvalidCredentialsError):
        authenticate(db_session, user.email, "wrong-password")


def test_unknown_email_raises(db_session):
    with pytest.raises(InvalidCredentialsError):
        authenticate(db_session, "nobody@test.com", "whatever")
