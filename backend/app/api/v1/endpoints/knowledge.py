from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.knowledge import (
    KnowledgeResponse,
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeSearchQuery
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.get("", response_model=List[KnowledgeResponse])
def get_knowledge(
    category: Optional[str] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return KnowledgeService.list_all(db, category=category, active_only=active_only, skip=skip, limit=limit)


@router.post("", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_entry(
    knowledge_in: KnowledgeCreate,
    db: Session = Depends(get_db)
):
    return KnowledgeService.create(db, knowledge_in)


@router.put("/{knowledge_id}", response_model=KnowledgeResponse)
def update_knowledge_entry(
    knowledge_id: int,
    knowledge_in: KnowledgeUpdate,
    db: Session = Depends(get_db)
):
    entry = KnowledgeService.update(db, knowledge_id, knowledge_in)
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return entry


@router.delete("/{knowledge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_entry(
    knowledge_id: int,
    db: Session = Depends(get_db)
):
    success = KnowledgeService.delete(db, knowledge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return None


@router.post("/search", response_model=List[KnowledgeResponse])
def search_knowledge(
    search_query: KnowledgeSearchQuery,
    db: Session = Depends(get_db)
):
    return KnowledgeService.search_relevant(
        db=db,
        query_text=search_query.query,
        category=search_query.category,
        limit=search_query.limit
    )

