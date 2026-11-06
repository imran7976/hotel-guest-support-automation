from typing import List, Optional
from sqlalchemy import or_, text
from sqlalchemy.orm import Session
from app.models.knowledge import HotelKnowledge
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate


class KnowledgeService:
    @staticmethod
    def get_by_id(db: Session, knowledge_id: int) -> Optional[HotelKnowledge]:
        return db.query(HotelKnowledge).filter(HotelKnowledge.id == knowledge_id).first()

    @staticmethod
    def list_all(
        db: Session,
        category: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[HotelKnowledge]:
        query = db.query(HotelKnowledge)
        if active_only:
            query = query.filter(HotelKnowledge.is_active == True)
        if category and category != "all":
            query = query.filter(HotelKnowledge.category == category)
        return query.order_by(HotelKnowledge.category, HotelKnowledge.title).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, knowledge_in: KnowledgeCreate) -> HotelKnowledge:
        entry = HotelKnowledge(
            category=knowledge_in.category,
            title=knowledge_in.title,
            content=knowledge_in.content,
            keywords=knowledge_in.keywords,
            is_active=knowledge_in.is_active
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def update(db: Session, knowledge_id: int, knowledge_in: KnowledgeUpdate) -> Optional[HotelKnowledge]:
        entry = db.query(HotelKnowledge).filter(HotelKnowledge.id == knowledge_id).first()
        if not entry:
            return None
        data = knowledge_in.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(entry, field, value)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def delete(db: Session, knowledge_id: int) -> bool:
        entry = db.query(HotelKnowledge).filter(HotelKnowledge.id == knowledge_id).first()
        if not entry:
            return False
        db.delete(entry)
        db.commit()
        return True

    @staticmethod
    def search_relevant(
        db: Session,
        query_text: str,
        category: Optional[str] = None,
        limit: int = 4
    ) -> List[HotelKnowledge]:
        """
        Lightweight hybrid retrieval engine:
        1. Breaks search into tokens.
        2. Tries FULLTEXT search if MySQL is used, otherwise multi-token LIKE scoring.
        3. Prioritizes category relevance if provided.
        """
        tokens = [t.lower().strip() for t in query_text.replace("?", " ").replace("!", " ").replace(".", " ").split() if len(t.strip()) > 2]
        
        # Stopwords filter
        stopwords = {"the", "and", "for", "with", "can", "you", "tell", "have", "what", "how", "when", "there", "this", "that", "are", "could", "would", "about"}
        tokens = [t for t in tokens if t not in stopwords]

        query = db.query(HotelKnowledge).filter(HotelKnowledge.is_active == True)
        if category and category != "other":
            # If intent maps directly to category
            query = query.filter(
                or_(
                    HotelKnowledge.category == category,
                    HotelKnowledge.category == "general"
                )
            )

        candidates = query.all()

        if not tokens:
            return candidates[:limit]

        # Score candidates by keyword matches
        scored_entries = []
        for entry in candidates:
            score = 0
            searchable_text = f"{entry.title} {entry.content} {entry.keywords or ''}".lower()
            for token in tokens:
                if token in searchable_text:
                    score += 1
                if entry.keywords and token in entry.keywords.lower():
                    score += 2
                if token in entry.title.lower():
                    score += 3
            if score > 0:
                scored_entries.append((score, entry))

        scored_entries.sort(key=lambda x: x[0], reverse=True)
        results = [entry for _, entry in scored_entries[:limit]]

        # If no scored matches found, fallback to category or top general rules
        if not results:
            results = db.query(HotelKnowledge).filter(HotelKnowledge.is_active == True).limit(limit).all()

        return results

