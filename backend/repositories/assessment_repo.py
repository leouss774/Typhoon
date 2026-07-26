"""
Assessment Repository — database access for Assessment and related models.
"""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from models.db import Assessment, EvaluationReport, ExpertForm


class AssessmentRepository:
    """CRUD operations for the Assessment model."""

    @staticmethod
    def get_by_id(db: Session, assessment_id: str) -> Assessment | None:
        return db.get(Assessment, assessment_id)

    @staticmethod
    def list_by_user(db: Session, user_id: str) -> list[Assessment]:
        return list(
            db.execute(
                select(Assessment)
                .where(Assessment.user_id == user_id)
                .order_by(desc(Assessment.created_at))
            ).scalars().all()
        )

    @staticmethod
    def create(db: Session, **kwargs) -> Assessment:
        assessment = Assessment(**kwargs)
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    def update_status(db: Session, assessment: Assessment, status: str) -> Assessment:
        assessment.status = status
        from sqlalchemy import func
        import datetime
        assessment.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
        return assessment

    @staticmethod
    def update_scores(db: Session, assessment: Assessment, **scores) -> Assessment:
        for key, value in scores.items():
            setattr(assessment, key, value)
        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    def delete(db: Session, assessment: Assessment) -> None:
        db.delete(assessment)
        db.commit()

    # ── Expert Forms ─────────────────────────────────────────────

    @staticmethod
    def get_expert_form(db: Session, assessment_id: str) -> ExpertForm | None:
        return db.execute(
            select(ExpertForm).where(ExpertForm.assessment_id == assessment_id)
        ).scalar_one_or_none()

    @staticmethod
    def upsert_expert_form(
        db: Session,
        assessment_id: str,
        fields_json: str,
        recommendations_json: str | None,
    ) -> ExpertForm:
        existing = AssessmentRepository.get_expert_form(db, assessment_id)
        if existing:
            existing.fields = fields_json
            existing.recommendations = recommendations_json
        else:
            existing = ExpertForm(
                assessment_id=assessment_id,
                fields=fields_json,
                recommendations=recommendations_json,
            )
            db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    # ── Evaluation Reports ───────────────────────────────────────

    @staticmethod
    def get_evaluation_report(db: Session, assessment_id: str) -> EvaluationReport | None:
        return db.execute(
            select(EvaluationReport).where(EvaluationReport.assessment_id == assessment_id)
        ).scalar_one_or_none()

    @staticmethod
    def upsert_evaluation_report(
        db: Session,
        assessment_id: str,
        global_score: int | None,
        sub_scores_json: str | None,
        report_content_json: str | None,
    ) -> EvaluationReport:
        from datetime import datetime, timezone
        existing = AssessmentRepository.get_evaluation_report(db, assessment_id)
        if existing:
            existing.global_score = global_score
            existing.sub_scores = sub_scores_json
            existing.report_content = report_content_json
            existing.generated_at = datetime.now(timezone.utc)
        else:
            existing = EvaluationReport(
                assessment_id=assessment_id,
                global_score=global_score,
                sub_scores=sub_scores_json,
                report_content=report_content_json,
            )
            db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
