from fastapi import APIRouter, Query, Response

from app.api.deps import CurrentZone, DbSession
from app.core.errors import DomainError
from app.repositories.record_repository import RecordRepository
from app.schemas.common import Page, page_meta
from app.schemas.record import (
    RECORD_TYPES,
    BulkDeleteRequest,
    BulkDeleteResult,
    DnsRecordOut,
    DnsRecordWrite,
)
from app.services.record_service import RecordService

router = APIRouter(prefix="/hosted-zones/{zone_id}/records", tags=["DNS records"])
service, repository = RecordService(), RecordRepository()


def out(record) -> DnsRecordOut:
    return DnsRecordOut(
        id=record.id,
        name=record.name,
        record_type=record.record_type,
        routing_policy=record.routing_policy,
        differentiator=record.set_identifier or None,
        is_alias=record.is_alias,
        alias_target=record.alias_target,
        values=[v.value for v in record.values],
        ttl=record.ttl,
        evaluate_target_health=record.evaluate_target_health,
        health_check_id=record.health_check_id,
        is_system_record=record.is_system_record,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("", response_model=Page[DnsRecordOut])
def list_records(
    db: DbSession,
    zone: CurrentZone,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    type: str | None = Query(None),
    sort_by: str = "name",
    sort_direction: str = Query("asc", pattern="^(asc|desc)$"),
):
    if type and type.upper() not in RECORD_TYPES:
        raise DomainError("invalid_record_type", "Unsupported record type.")
    items, total = repository.list(
        db,
        zone.id,
        page,
        page_size,
        search,
        type.upper() if type else None,
        sort_by,
        sort_direction == "desc",
    )
    return Page(
        items=[out(item) for item in items],
        pagination=page_meta(page, page_size, total),
    )


@router.post("", response_model=DnsRecordOut, status_code=201)
def create_record(payload: DnsRecordWrite, db: DbSession, zone: CurrentZone):
    return out(service.create(db, zone, payload))


@router.get("/{record_id}", response_model=DnsRecordOut)
def get_record(record_id: str, db: DbSession, zone: CurrentZone):
    record = repository.get(db, zone.id, record_id)
    if not record:
        raise DomainError("record_not_found", "DNS record was not found.", 404)
    return out(record)


@router.patch("/{record_id}", response_model=DnsRecordOut)
def update_record(
    record_id: str, payload: DnsRecordWrite, db: DbSession, zone: CurrentZone
):
    record = repository.get(db, zone.id, record_id)
    if not record:
        raise DomainError("record_not_found", "DNS record was not found.", 404)
    return out(service.update(db, zone, record, payload))


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: str, db: DbSession, zone: CurrentZone):
    record = repository.get(db, zone.id, record_id)
    if not record:
        raise DomainError("record_not_found", "DNS record was not found.", 404)
    service.delete(db, zone, record)
    return Response(status_code=204)


@router.post("/bulk-delete", response_model=BulkDeleteResult)
def bulk_delete(payload: BulkDeleteRequest, db: DbSession, zone: CurrentZone):
    deleted, failed = [], []
    for record_id in payload.record_ids:
        record = repository.get(db, zone.id, record_id)
        if not record:
            failed.append({"id": record_id, "reason": "Record not found"})
        elif record.is_system_record:
            failed.append(
                {"id": record_id, "reason": "Default records cannot be deleted"}
            )
        else:
            db.delete(record)
            zone.record_count -= 1
            deleted.append(record_id)
    db.commit()
    return BulkDeleteResult(deleted_ids=deleted, failed=failed)
