"""SQLAlchemy models for PolicyShadow persistence."""

from sqlalchemy import JSON, Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ViolationModel(Base):
    __tablename__ = "violations"

    violation_id = Column(String, primary_key=True)
    record_id = Column(String, nullable=False)
    policy_id = Column(String, nullable=False)
    rule_name = Column(String, nullable=False)
    resource_kind = Column(String, nullable=False)
    resource_name = Column(String, nullable=False)
    namespace = Column(String, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, nullable=True)
    raw_result = Column(JSON, nullable=True)
