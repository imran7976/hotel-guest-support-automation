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
        data = knowledge_in.model_dump(exclude_unset=True)
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
        Intelligent hybrid retrieval engine:
        1. Breaks search into tokens and cleans punctuation.
        2. Searches all active hotel knowledge documents without artificial category barriers.
        3. Scores matches across title, content, and keywords with category contextual boosts.
        """
        clean_text = query_text.lower().replace("?", " ").replace("!", " ").replace(".", " ").replace(",", " ")
        tokens = [t.strip() for t in clean_text.split() if len(t.strip()) > 2]
        
        # Stopwords filter
        stopwords = {"the", "and", "for", "with", "can", "you", "tell", "have", "what", "how", "when", "there", "this", "that", "are", "could", "would", "about", "does", "will"}
        tokens = [t for t in tokens if t not in stopwords]

        candidates = db.query(HotelKnowledge).filter(HotelKnowledge.is_active == True).all()

        if not tokens:
            if category and category != "other":
                cat_matches = [e for e in candidates if e.category == category]
                if cat_matches:
                    return cat_matches[:limit]
            return candidates[:limit]

        # Score candidates by relevance
        scored_entries = []
        for entry in candidates:
            score = 0
            title_lower = entry.title.lower()
            content_lower = entry.content.lower()
            keywords_lower = (entry.keywords or "").lower()
            searchable_text = f"{title_lower} {content_lower} {keywords_lower}"

            # Category boost
            if category and category != "other" and entry.category == category:
                score += 4

            for token in tokens:
                if token in title_lower:
                    score += 5
                elif token in keywords_lower:
                    score += 3
                elif token in content_lower:
                    score += 2

            if score > 0:
                scored_entries.append((score, entry))

        scored_entries.sort(key=lambda x: x[0], reverse=True)
        results = [entry for _, entry in scored_entries[:limit]]

        # Fallback if no keyword matches scored
        if not results:
            if category and category != "other":
                cat_matches = [e for e in candidates if e.category == category]
                if cat_matches:
                    return cat_matches[:limit]
            results = candidates[:limit]

        return results

