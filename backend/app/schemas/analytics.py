from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class InquiryCategoryStat(BaseModel):
    category: str
    count: int
    percentage: float


class RecentActivity(BaseModel):
    id: str
    type: str  # inquiry, escalation, booking, resolution
    title: str
    description: str
    timestamp: str
    priority: Optional[str] = None


class DashboardKPIs(BaseModel):
    total_inquiries: int
    today_inquiries: int
    ai_resolved_inquiries: int
    pending_escalations: int
    resolved_escalations: int
    active_conversations: int
    average_response_time_ms: float
    resolution_rate_percent: float
    category_distribution: List[InquiryCategoryStat]
    recent_activities: List[RecentActivity]


class DailySummaryReport(BaseModel):
    report_date: str
    total_inquiries: int
    resolved_by_ai: int
    escalated_to_staff: int
    top_categories: List[Dict[str, Any]]
    unresolved_complaints_count: int
    ai_summary_text: str
    generated_at: str

