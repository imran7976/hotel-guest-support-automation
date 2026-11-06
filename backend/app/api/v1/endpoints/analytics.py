from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.analytics import DashboardKPIs, DailySummaryReport
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardKPIs)
def get_dashboard_analytics(db: Session = Depends(get_db)):
    return AnalyticsService.get_dashboard_kpis(db)


@router.get("/daily-summary", response_model=DailySummaryReport)
def get_daily_summary(
    report_date: Optional[date] = Query(None, description="Date for summary (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_daily_summary(db, target_date=report_date)

