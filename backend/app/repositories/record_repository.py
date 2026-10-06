from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import DnsRecord


class RecordRepository:
    def get(self, db: Session, zone_id: str, record_id: str) -> DnsRecord | None:
        return db.scalar(
            select(DnsRecord)
            .where(DnsRecord.id == record_id, DnsRecord.hosted_zone_id == zone_id)
            .options(selectinload(DnsRecord.values))
        )

    def list(
        self,
        db: Session,
        zone_id: str,
        page: int,
        page_size: int,
        search: str | None,
        record_type: str | None,
        sort_by: str,
        descending: bool,
    ) -> tuple[list[DnsRecord], int]:
        criteria = [DnsRecord.hosted_zone_id == zone_id]
        if search:
            criteria.append(
                or_(
                    DnsRecord.name.ilike(f"%{search}%"),
                    DnsRecord.record_type.ilike(f"%{search}%"),
                )
            )
        if record_type:
            criteria.append(DnsRecord.record_type == record_type)
        sort_column = {
            "name": DnsRecord.name,
            "type": DnsRecord.record_type,
            "ttl": DnsRecord.ttl,
        }.get(sort_by, DnsRecord.name)
        stmt = (
            select(DnsRecord)
            .where(*criteria)
            .options(selectinload(DnsRecord.values))
            .order_by(sort_column.desc() if descending else sort_column.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(db.scalars(stmt)), db.scalar(
            select(func.count()).select_from(DnsRecord).where(*criteria)
        ) or 0
