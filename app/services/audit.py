from sqlalchemy.orm import Session

from app.models import AuditLog


def create_audit_log(
    db: Session,
    user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    details: str | None = None,
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(log)
    db.commit()
    return log