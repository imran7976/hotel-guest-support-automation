import secrets
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.workflow_log import WorkflowLog
from app.schemas.webhook import WebhookInquiryPayload, WebhookCallbackPayload, WorkflowLogResponse
from app.schemas.ai import ProcessInquiryRequest, ProcessInquiryResponse
from app.core.config import settings
from app.core.logging import logger
from app.core.rate_limiter import rate_limit_public_endpoint

router = APIRouter()


@router.post(
    "/guest-inquiry",
    response_model=ProcessInquiryResponse,
    dependencies=[Depends(rate_limit_public_endpoint)]
)
def webhook_guest_inquiry(
    payload: WebhookInquiryPayload,
    db: Session = Depends(get_db),
    x_webhook_token: Optional[str] = Header(None)
):
    """
    Inbound webhook endpoint called by n8n or external hotel channels.
    Validates token if configured, processes inquiry, and logs execution.
    """
    if settings.N8N_WEBHOOK_AUTH_TOKEN and settings.ENVIRONMENT != "test":
        if not x_webhook_token or not secrets.compare_digest(x_webhook_token, settings.N8N_WEBHOOK_AUTH_TOKEN):
            raise HTTPException(status_code=403, detail="Invalid or missing webhook authentication token")

    # Delegate to AI processing orchestrator (import inside handler to avoid circular imports)
    from app.ai.response_generator import AIGuestSupportOrchestrator

    req = ProcessInquiryRequest(
        guest_name=payload.guest_name,
        email=payload.email,
        inquiry_message=payload.inquiry_message,
        booking_reference=payload.booking_reference,
        inquiry_category=payload.inquiry_category,
        channel=payload.channel or "webhook"
    )

    try:
        response = AIGuestSupportOrchestrator.process_inquiry(db=db, request=req)

        # Log successful workflow execution
        log = WorkflowLog(
            workflow_name="Guest Inquiry Processing",
            trigger_event="webhook_guest_inquiry",
            status="success",
            payload_json={
                "guest_email": payload.email,
                "intent": response.intent,
                "confidence": response.confidence,
                "requires_human": response.requires_human
            }
        )
        db.add(log)
        db.commit()

        return response
    except Exception as e:
        logger.error(f"Error processing webhook guest inquiry: {str(e)}", exc_info=True)
        # Log failure
        log = WorkflowLog(
            workflow_name="Guest Inquiry Processing",
            trigger_event="webhook_guest_inquiry",
            status="failed",
            error_message=str(e),
            payload_json={"guest_email": payload.email, "message": payload.inquiry_message}
        )
        db.add(log)
        db.commit()
        raise HTTPException(status_code=500, detail="Internal workflow error processing inquiry")


@router.post("/n8n-callback", status_code=status.HTTP_200_OK)
def n8n_callback(
    payload: WebhookCallbackPayload,
    db: Session = Depends(get_db)
):
    """Records asynchronous callback executions from n8n nodes."""
    log = WorkflowLog(
        workflow_name=payload.workflow_name,
        execution_id=payload.execution_id,
        trigger_event=payload.trigger_event,
        status=payload.status,
        error_message=payload.error_message,
        payload_json=payload.payload
    )
    db.add(log)
    db.commit()
    return {"status": "recorded", "id": log.id}


@router.get("/logs", response_model=List[WorkflowLogResponse])
def get_workflow_logs(
    workflow_name: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(WorkflowLog)
    if workflow_name and workflow_name != "all":
        query = query.filter(WorkflowLog.workflow_name == workflow_name)
    if status and status != "all":
        query = query.filter(WorkflowLog.status == status)
    return query.order_by(WorkflowLog.created_at.desc()).offset(skip).limit(limit).all()

