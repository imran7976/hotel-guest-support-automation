from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class KnowledgeBase(BaseModel):
    category: str
    title: str
    content: str
    keywords: Optional[str] = None
    is_active: bool = True


class KnowledgeCreate(KnowledgeBase):
    pass


class KnowledgeUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[str] = None
    is_active: Optional[bool] = None


class KnowledgeResponse(KnowledgeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeSearchQuery(BaseModel):
    query: str
    category: Optional[str] = None
    limit: int = 5

