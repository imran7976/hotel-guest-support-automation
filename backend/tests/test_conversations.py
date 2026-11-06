import pytest
from app.services.conversation_service import ConversationService
from app.services.guest_service import GuestService


def test_conversation_lifecycle(db_session):
    guest = GuestService.get_or_create(db_session, "Emma Stone", "emma.stone@example.demo")
    
    # Create conversation
    conv = ConversationService.get_or_create_conversation(db_session, guest_id=guest.id, channel="web_chat")
    assert conv.id.startswith("conv_")
    assert conv.guest_id == guest.id
    assert conv.status == "active"

    # Add messages
    msg1 = ConversationService.add_message(
        db=db_session,
        conversation_id=conv.id,
        sender_type="guest",
        content="What time is check in?",
        intent="check_in_information"
    )
    assert msg1.id is not None
    assert msg1.intent == "check_in_information"

    msg2 = ConversationService.add_message(
        db=db_session,
        conversation_id=conv.id,
        sender_type="ai",
        content="Our standard check in time is 2:00 PM.",
        requires_human=False
    )
    assert msg2.id is not None

    # Retrieve history
    history = ConversationService.get_conversation_history(db_session, conv.id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_conversation_api(client):
    # GET list
    res = client.get("/api/v1/conversations")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

