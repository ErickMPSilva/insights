from datetime import UTC, datetime

from core.repositories import UserRepository
from core.security import hash_password, verify_password
from sqlalchemy.orm import Session


class InvalidCredentialsError(Exception):
    """E-mail não cadastrado ou senha incorreta."""


_DUMMY_HASH = hash_password("dummy-password-for-timing")


def authenticate(session: Session, email: str, password: str):
    user = UserRepository(session).get_by_email(email)

    if user is None:
        verify_password(password, _DUMMY_HASH)
        raise InvalidCredentialsError

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError

    user.last_login_at = datetime.now(UTC)
    return user.id
