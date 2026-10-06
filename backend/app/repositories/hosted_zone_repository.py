from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import DnsRecord, HostedZone


class HostedZoneRepository:
    def get(self, db: Session, account_id: str, zone_id: str) -> HostedZone | None:
        stmt = (
            select(HostedZone)
            .where(
                HostedZone.id == zone_id,
                HostedZone.account_id == account_id,
                HostedZone.deleted_at.is_(None),
            )
            .options(
                selectinload(HostedZone.vpc_links), selectinload(HostedZone.tag_links)
            )
        )
        return db.scalar(stmt)

    def list(
        self,
        db: Session,
        account_id: str,
        page: int,
        page_size: int,
        search: str | None,
        zone_type: str | None,
        sort_by: str,
        descending: bool,
    ) -> tuple[list[HostedZone], int]:
        criteria = [
            HostedZone.account_id == account_id,
            HostedZone.deleted_at.is_(None),
        ]
        if search:
            criteria.append(
                or_(
                    HostedZone.name.ilike(f"%{search}%"),
                    HostedZone.description.ilike(f"%{search}%"),
                )
            )
        if zone_type:
            criteria.append(HostedZone.zone_type == zone_type)
        sort_column = {
            "name": HostedZone.name,
            "type": HostedZone.zone_type,
            "created_at": HostedZone.created_at,
            "record_count": HostedZone.record_count,
        }.get(sort_by, HostedZone.name)
        statement = (
            select(HostedZone)
            .where(*criteria)
            .order_by(sort_column.desc() if descending else sort_column.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(db.scalars(statement)), db.scalar(
            select(func.count()).select_from(HostedZone).where(*criteria)
        ) or 0

    def non_system_record_count(self, db: Session, zone_id: str) -> int:
        return (
            db.scalar(
                select(func.count())
                .select_from(DnsRecord)
                .where(DnsRecord.hosted_zone_id == zone_id, ~DnsRecord.is_system_record)
            )
            or 0
        )
