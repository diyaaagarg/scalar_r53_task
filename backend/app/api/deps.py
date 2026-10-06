from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import DomainError
from app.models import HostedZone, User
from app.services.auth_service import AuthService
from app.services.hosted_zone_service import HostedZoneService

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession, route53_session: str | None = Cookie(default=None)
) -> User:
    return AuthService().current_user(db, route53_session)


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_zone(zone_id: str, db: DbSession, user: CurrentUser) -> HostedZone:
    zone = HostedZoneService().repository.get(db, user.account_id, zone_id)
    if not zone:
        raise DomainError("hosted_zone_not_found", "Hosted zone was not found.", 404)
    return zone


CurrentZone = Annotated[HostedZone, Depends(get_zone)]
