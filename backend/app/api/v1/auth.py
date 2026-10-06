from fastapi import APIRouter, Cookie, Response

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.schemas.auth import AccountOut, LoginRequest, SessionOut, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def session_out(user) -> SessionOut:
    return SessionOut(
        user=UserOut(id=user.id, email=user.email, display_name=user.display_name),
        account=AccountOut(
            aws_account_id=user.account.aws_account_id,
            display_name=user.account.display_name,
        ),
        region=user.account.default_region,
    )


@router.post("/login", response_model=SessionOut)
def login(payload: LoginRequest, response: Response, db: DbSession):
    user, token = AuthService().login(db, payload.email, payload.password)
    settings = get_settings()
    response.set_cookie(
        "route53_session",
        token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite=settings.cookie_samesite_value,
        max_age=settings.session_days * 86400,
        path="/",
    )
    return session_out(user)


@router.post("/logout", status_code=204)
def logout(
    response: Response,
    db: DbSession,
    user: CurrentUser,
    route53_session: str | None = Cookie(default=None),
):
    AuthService().logout(db, route53_session)
    response.delete_cookie("route53_session", path="/")


@router.get("/me", response_model=SessionOut)
def me(user: CurrentUser):
    return session_out(user)
