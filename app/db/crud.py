from sqlalchemy.orm import Session
from app.db.models import RedactionLog
import json

def create_redaction_log(
    db: Session,
    input_type: str,
    source_name: str,
    entity_count: int | None,
    columns_redacted: list[str] | None = None
):
    log = RedactionLog(
        input_type=input_type,
        source_name=source_name,
        entity_count=entity_count,
        columns_redacted=json.dumps(columns_redacted) if columns_redacted else None
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log