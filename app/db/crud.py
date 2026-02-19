from sqlalchemy.orm import Session
from sqlalchemy import func, desc, cast, Date
from app.db.models import RedactionLog, User
from app.auth.password import hash_password
import json
from datetime import date

def create_redaction_log(
    db: Session,
    user_id: int,
    input_type: str,
    source_name: str,
    entity_count: int | None,
    columns_redacted: list[str] | None = None
):
    log = RedactionLog(
        input_type=input_type,
        user_id=user_id,
        source_name=source_name,
        entity_count=entity_count,
        columns_redacted=json.dumps(columns_redacted) if columns_redacted else None
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str, name: str):
    hashed_pwd = hash_password(password)

    user = User(
        email=email,
        hashed_password=hashed_pwd,
        name=name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def get_user_stats(db: Session, user_id: int):
    total_files = db.query(RedactionLog).filter(RedactionLog.user_id == user_id).count()
    total_entities = db.query(func.sum(RedactionLog.entity_count)).filter(RedactionLog.user_id == user_id).scalar() or 0
    
    recent_activity = db.query(
        cast(RedactionLog.created_at, Date).label('date'),
        func.count(RedactionLog.id).label('count')
    ).filter(
        RedactionLog.user_id == user_id
    ).group_by(
        cast(RedactionLog.created_at, Date)
    ).order_by(
        desc('date')
    ).limit(7).all()

    stats_list = [
        {"date": str(stat.date), "count": stat.count} 
        for stat in recent_activity
    ]
    
    user = db.query(User).filter(User.id == user_id).first()
    
    return {
        "name": user.name if user else None,
        "documents_processed": total_files,
        "redactions_done": total_entities,
        "recent_activity": stats_list
    }