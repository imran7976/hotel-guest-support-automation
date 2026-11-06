import pytest
from app.services.analytics_service import AnalyticsService


def test_dashboard_kpis_calculation(db_session):
    kpis = AnalyticsService.get_dashboard_kpis(db_session)
    assert kpis.total_inquiries >= 0
    assert kpis.average_response_time_ms > 0
    assert isinstance(kpis.category_distribution, list)
    assert isinstance(kpis.recent_activities, list)


def test_daily_summary_report(db_session):
    report = AnalyticsService.get_daily_summary(db_session)
    assert report.report_date is not None
    assert "Grand Azure" in report.ai_summary_text


def test_analytics_api_endpoints(client):
    res = client.get("/api/v1/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_inquiries" in data
    assert "category_distribution" in data

    res2 = client.get("/api/v1/analytics/daily-summary")
    assert res2.status_code == 200
    assert "ai_summary_text" in res2.json()

