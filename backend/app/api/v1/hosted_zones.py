from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.deps import CurrentUser, CurrentZone, DbSession
from app.schemas.common import Page, TagIn, page_meta
from app.schemas.hosted_zone import (
    DeleteHostedZoneRequest,
    HostedZoneCreate,
    HostedZoneDetail,
    HostedZoneSummary,
    HostedZoneUpdate,
    VpcOut,
)
from app.schemas.transfer import BindImportRequest, ImportResult
from app.services.hosted_zone_service import HostedZoneService
from app.services.zone_transfer_service import ZoneTransferService

router = APIRouter(prefix="/hosted-zones", tags=["Hosted zones"])
service = HostedZoneService()
transfer_service = ZoneTransferService()


def tags(zone):
    return [
        TagIn(key=link.tag.tag_key, value=link.tag.tag_value) for link in zone.tag_links
    ]


def detail(zone) -> HostedZoneDetail:
    return HostedZoneDetail(
        id=zone.id,
        hosted_zone_id=zone.public_id,
        name=zone.name,
        type=zone.zone_type,
        created_by=zone.created_by_user_id,
        record_count=zone.record_count,
        description=zone.description,
        created_at=zone.created_at,
        updated_at=zone.updated_at,
        dnssec_enabled=zone.dnssec_enabled,
        vpcs=[VpcOut.model_validate(link.vpc) for link in zone.vpc_links],
        tags=tags(zone),
    )


def summary(zone) -> HostedZoneSummary:
    return HostedZoneSummary(
        id=zone.id,
        hosted_zone_id=zone.public_id,
        name=zone.name,
        type=zone.zone_type,
        created_by=zone.created_by_user_id,
        record_count=zone.record_count,
        description=zone.description,
        created_at=zone.created_at,
    )


@router.get("", response_model=Page[HostedZoneSummary])
def list_zones(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    type: str | None = Query(None, pattern="^(PUBLIC|PRIVATE)$"),
    sort_by: str = "name",
    sort_direction: str = Query("asc", pattern="^(asc|desc)$"),
):
    items, total = service.repository.list(
        db,
        user.account_id,
        page,
        page_size,
        search,
        type,
        sort_by,
        sort_direction == "desc",
    )
    return Page(
        items=[summary(item) for item in items],
        pagination=page_meta(page, page_size, total),
    )


@router.post("", response_model=HostedZoneDetail, status_code=201)
def create_zone(payload: HostedZoneCreate, db: DbSession, user: CurrentUser):
    return detail(service.create(db, user, payload))


@router.get("/{zone_id}/export")
def export_zone(
    zone: CurrentZone,
    db: DbSession,
    format: str = Query("json", pattern="^(json|bind)$"),
):
    filename = zone.name.rstrip(".")
    if format == "bind":
        return PlainTextResponse(
            transfer_service.export_bind(db, zone),
            headers={"Content-Disposition": f'attachment; filename="{filename}.zone"'},
        )
    return JSONResponse(
        transfer_service.export_json(db, zone),
        headers={"Content-Disposition": f'attachment; filename="{filename}.json"'},
    )


@router.post("/{zone_id}/import", response_model=ImportResult, status_code=201)
def import_bind_zone(payload: BindImportRequest, zone: CurrentZone, db: DbSession):
    return ImportResult(
        created_count=transfer_service.import_bind(db, zone, payload.content)
    )


@router.get("/{zone_id}", response_model=HostedZoneDetail)
def get_zone(zone: CurrentZone):
    return detail(zone)


@router.patch("/{zone_id}", response_model=HostedZoneDetail)
def update_zone(payload: HostedZoneUpdate, db: DbSession, zone: CurrentZone):
    return detail(service.update(db, zone, payload))


@router.delete("/{zone_id}", status_code=204)
def delete_zone(payload: DeleteHostedZoneRequest, db: DbSession, zone: CurrentZone):
    service.delete(db, zone, payload.confirmation)
    return Response(status_code=204)
