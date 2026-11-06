from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from app.database.base import Base


class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workflow_name = Column(String(150), index=True, nullable=False)
    execution_id = Column(String(100), nullable=True)
    trigger_event = Column(String(100), nullable=False)
    status = Column(String(50), index=True, nullable=False)  # success, failed, retried
    error_message = Column(Text, nullable=True)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

