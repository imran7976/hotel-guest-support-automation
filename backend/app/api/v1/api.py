from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    guests,
    conversations,
    bookings,
    escalations,
    knowledge,
    analytics,
    ai,
    webhooks
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(guests.router, prefix="/guests", tags=["Guests"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(escalations.router, prefix="/escalations", tags=["Escalations"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & KPIs"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Operations"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks & n8n"])

