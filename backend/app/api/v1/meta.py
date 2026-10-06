from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models import Vpc
from app.schemas.hosted_zone import VpcOut
from app.schemas.record import RECORD_TYPES

router = APIRouter(tags=["Metadata"])


@router.get("/meta/record-types")
def record_types(_user: CurrentUser):
    return {"items": sorted(RECORD_TYPES)}


@router.get("/vpcs", response_model=dict[str, list[VpcOut]])
def vpcs(
    db: DbSession,
    user: CurrentUser,
    region: str | None = None,
    search: str | None = None,
):
    stmt = select(Vpc).where(Vpc.account_id == user.account_id)
    if region:
        stmt = stmt.where(Vpc.region == region)
    if search:
        stmt = stmt.where(Vpc.aws_vpc_id.ilike(f"%{search}%"))
    return {"items": [VpcOut.model_validate(vpc) for vpc in db.scalars(stmt)]}
