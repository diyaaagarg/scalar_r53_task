from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.models import DnsRecord, DnsRecordValue, HostedZone
from app.repositories.record_repository import RecordRepository
from app.schemas.record import DnsRecordWrite
from app.services.record_validation_service import RecordValidationService


class RecordService:
    def __init__(self):
        self.repository = RecordRepository()
        self.validator = RecordValidationService()

    def create(self, db: Session, zone: HostedZone, data: DnsRecordWrite) -> DnsRecord:
        self.validator.validate(db, zone.id, data)
        record = DnsRecord(
            hosted_zone_id=zone.id,
            name=data.name,
            record_type=data.record_type,
            ttl=data.ttl,
            is_alias=bool(data.alias),
            alias_target=data.alias.dns_name if data.alias else None,
            evaluate_target_health=data.evaluate_target_health,
            health_check_id=data.health_check_id,
        )
        record.values = [
            DnsRecordValue(value=value, position=index)
            for index, value in enumerate(data.values)
        ]
        db.add(record)
        zone.record_count += 1
        db.commit()
        db.refresh(record)
        return record

    def update(
        self, db: Session, zone: HostedZone, record: DnsRecord, data: DnsRecordWrite
    ) -> DnsRecord:
        if record.is_system_record:
            raise DomainError(
                "system_record", "Default NS and SOA records cannot be edited.", 403
            )
        self.validator.validate(db, zone.id, data, record.id)
        record.name, record.record_type, record.ttl = (
            data.name,
            data.record_type,
            data.ttl,
        )
        record.is_alias, record.alias_target = (
            bool(data.alias),
            data.alias.dns_name if data.alias else None,
        )
        record.evaluate_target_health, record.health_check_id = (
            data.evaluate_target_health,
            data.health_check_id,
        )
        record.values[:] = [
            DnsRecordValue(value=value, position=index)
            for index, value in enumerate(data.values)
        ]
        db.commit()
        db.refresh(record)
        return record

    def delete(self, db: Session, zone: HostedZone, record: DnsRecord) -> None:
        if record.is_system_record:
            raise DomainError(
                "system_record", "Default NS and SOA records cannot be deleted.", 403
            )
        db.delete(record)
        zone.record_count -= 1
        db.commit()
