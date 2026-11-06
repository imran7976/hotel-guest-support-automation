from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.knowledge import HotelKnowledge
from app.services.knowledge_service import KnowledgeService
from app.core.logging import logger

INTENT_TO_CATEGORY_MAP = {
    "check_in_information": "check_in_out",
    "check_out_information": "check_in_out",
    "wifi_issues": "wifi",
    "cancellation": "cancellation",
    "hotel_facilities": "facilities",
    "payment_inquiry": "policies",
    "maintenance_requests": "contact"
}


class RAGEngine:
    @staticmethod
    def retrieve(
        db: Session,
        query: str,
        category: Optional[str] = None,
        limit: int = 3
    ) -> List[HotelKnowledge]:
        """
        Retrieves relevant hotel policies and guides from hotel_knowledge table.
        Maps inquiry intent to knowledge category where applicable.
        """
        mapped_cat = INTENT_TO_CATEGORY_MAP.get(category, category)
        lower_q = query.lower()

        # Context-aware category refinement
        if any(w in lower_q for w in ["breakfast", "dining", "restaurant", "food", "buffet", "dinner", "room service"]):
            mapped_cat = "dining"
        elif any(w in lower_q for w in ["pet", "dog", "smoking", "smoke", "cigarette", "vape"]):
            mapped_cat = "policies"
        elif any(w in lower_q for w in ["wifi", "wi-fi", "internet", "password"]):
            mapped_cat = "wifi"
        elif any(w in lower_q for w in ["check in", "check-in", "check out", "check-out", "checkout", "luggage", "early arrival"]):
            mapped_cat = "check_in_out"

        results = KnowledgeService.search_relevant(
            db=db,
            query_text=query,
            category=mapped_cat,
            limit=limit
        )
        logger.debug(f"RAG retrieval found {len(results)} relevant entries for query: '{query}'")
        return results

    @staticmethod
    def format_context_for_prompt(knowledge_items: List[HotelKnowledge]) -> str:
        if not knowledge_items:
            return "No verified hotel knowledge matches found. Instruct the guest that details will be confirmed with the front desk."
        
        formatted_blocks = []
        for i, item in enumerate(knowledge_items, 1):
            formatted_blocks.append(
                f"[Document {i} - Category: {item.category} | Title: {item.title}]\n{item.content}"
            )
        return "\n\n".join(formatted_blocks)

