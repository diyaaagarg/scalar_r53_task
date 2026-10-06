from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.core.security import (
    hash_token,
    new_session_token,
    session_expiry,
    utc_now,
    verify_password,
)
from app.models import SessionToken, User


class AuthService:
    def login(self, db: Session, email: str, password: str) -> tuple[User, str]:
        user = db.scalar(select(User).where(User.email == email.lower()))
        if (
            not user
            or not user.is_active
            or not verify_password(password, user.password_hash)
        ):
            raise DomainError(
                "invalid_credentials", "Email or password is incorrect.", 401
            )
        raw = new_session_token()
        db.add(
            SessionToken(
                user_id=user.id, token_hash=hash_token(raw), expires_at=session_expiry()
            )
        )
        db.commit()
        return user, raw

    def current_user(self, db: Session, raw_token: str | None) -> User:
        if not raw_token:
            raise DomainError("not_authenticated", "Authentication is required.", 401)
        session = db.scalar(
            select(SessionToken).where(SessionToken.token_hash == hash_token(raw_token))
        )
        if not session or session.revoked_at or session.expires_at <= utc_now():
            raise DomainError(
                "not_authenticated", "Session is invalid or expired.", 401
            )
        user = db.get(User, session.user_id)
        if not user or not user.is_active:
            raise DomainError(
                "not_authenticated", "Session is invalid or expired.", 401
            )
        return user

    def logout(self, db: Session, raw_token: str | None) -> None:
        if raw_token:
            session = db.scalar(
                select(SessionToken).where(
                    SessionToken.token_hash == hash_token(raw_token)
                )
            )
            if session:
                session.revoked_at = utc_now()
                db.commit()
