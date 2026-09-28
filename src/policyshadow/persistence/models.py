"""SQLAlchemy models for PolicyShadow persistence."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RunModel(Base):
    __tablename__ = "runs"

    run_id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    status = Column(String, nullable=False)
    total_records = Column(Integer, nullable=False)
    error = Column(Text, nullable=True)


class ClusterModel(Base):
    __tablename__ = "clusters"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.run_id", ondelete="CASCADE"), nullable=False)
    label = Column(String, nullable=False)
    rule_name = Column(String, nullable=False)
    violation_count = Column(Integer, nullable=False)
    evidence = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=False)


class ViolationModel(Base):
    __tablename__ = "violations"

    violation_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.run_id", ondelete="CASCADE"), nullable=True)
    cluster_id = Column(String, ForeignKey("clusters.id", ondelete="SET NULL"), nullable=True)
    record_id = Column(String, nullable=False)
    policy_id = Column(String, nullable=False)
    rule_name = Column(String, nullable=False)
    resource_kind = Column(String, nullable=False)
    resource_name = Column(String, nullable=False)
    namespace = Column(String, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, nullable=True)
    raw_result = Column(JSON, nullable=True)


class RecommendationModel(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True)
    cluster_id = Column(String, ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    rationale = Column(Text, nullable=False)


class DecisionModel(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(
        String, ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False
    )
    decision = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
