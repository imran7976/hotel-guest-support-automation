import pytest
from app.services.knowledge_service import KnowledgeService
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate


def test_knowledge_crud(db_session):
    # Create
    item = KnowledgeService.create(
        db_session,
        KnowledgeCreate(
            category="facilities",
            title="Tennis Courts",
            content="Two floodlit championship tennis courts open from 7:00 AM to 9:00 PM.",
            keywords="tennis, court, sport"
        )
    )
    assert item.id is not None
    assert item.title == "Tennis Courts"

    # Search
    results = KnowledgeService.search_relevant(db_session, "What time are the tennis courts open?", category="facilities")
    assert len(results) > 0
    assert any("Tennis Courts" in r.title for r in results)

    # Update
    updated = KnowledgeService.update(
        db_session,
        item.id,
        KnowledgeUpdate(title="Grand Tennis Courts")
    )
    assert updated.title == "Grand Tennis Courts"

    # Delete
    deleted = KnowledgeService.delete(db_session, item.id)
    assert deleted is True


def test_knowledge_api(client):
    res = client.get("/api/v1/knowledge")
    assert res.status_code == 200
    assert len(res.json()) >= 10

