from typing import List, Dict, Any, Optional
import re
from .conversation_starter import ConversationStarter


class TopicAnalyzer:
    """Service to analyze conversation topics and suggest routing"""

    def __init__(self):
        self.conversation_starter = ConversationStarter()
        self.topic_categories = {
            "philosophy": ["meaning", "existence", "consciousness", "free will", "morality", "ethics", "truth", "purpose"],
            "science": ["research", "evidence", "data", "study", "quantum", "gravity", "evolution", "biology", "physics"],
            "technology": ["AI", "machine learning", "algorithm", "automation", "innovation", "future", "progress"],
            "creativity": ["art", "music", "inspiration", "imagination", "design", "innovation", "expression"],
            "humor": ["joke", "funny", "laugh", "comedy", "absurd", "ridiculous", "entertain", "amuse"],
            "society": ["humanity", "culture", "relationship", "society", "civilization", "future humans"]
        }

    def analyze_conversation_topics(self, messages: List[str]) -> Dict[str, float]:
        """
        Analyze recent messages and return topic scores

        Args:
            messages: List of recent message contents

        Returns:
            Dict mapping topic categories to relevance scores (0-1)
        """
        if not messages:
            return {topic: 0.0 for topic in self.topic_categories}

        combined_text = " ".join(messages[-10:]).lower()  # Analyze last 10 messages
        topic_scores = {}

        for topic, keywords in self.topic_categories.items():
            score = sum(1 for keyword in keywords if keyword.lower() in combined_text)
            # Normalize score
            topic_scores[topic] = min(score / len(keywords), 1.0)

        return topic_scores

    def suggest_topic_shift(self, current_topic_scores: Dict[str, float],
                          participants: List[str],
                          turn_count: int) -> Optional[str]:
        """
        Suggest if conversation should shift to a new topic

        Args:
            current_topic_scores: Current topic relevance scores
            participants: List of participating personas
            turn_count: Current turn number in conversation

        Returns:
            Suggested new topic category or None if no shift needed
        """
        # Don't shift too early (keep first 6 turns) or too late (after 15 turns)
        if turn_count < 6 or turn_count > 15:
            return None

        # Find dominant topic
        if current_topic_scores:
            dominant_topic = max(current_topic_scores.items(), key=lambda x: x[1])
            if dominant_topic[1] > 0.6:  # Strong dominance, consider shift
                # Suggest a complementary or contrasting topic
                complementary_topics = self._get_complementary_topics(dominant_topic[0], participants)
                if complementary_topics:
                    return complementary_topics[0]  # Return first suggestion

        return None

    def get_topic_based_follow_up(self, current_topic: str, participants: List[str]) -> str:
        """
        Generate a follow-up starter for evolving the conversation topic

        Args:
            current_topic: Current dominant topic category
            participants: List of participating personas

        Returns:
            Follow-up conversation starter
        """
        # For topic shifts, get a starter from a related theme
        complementary = self._get_complementary_topics(current_topic, participants)
        theme = complementary[0] if complementary else current_topic

        return self.conversation_starter.get_theme_based_starter(theme)

    def _get_complementary_topics(self, current_topic: str, participants: List[str]) -> List[str]:
        """Get complementary topics that work well with current topic and participants"""
        complements = {
            "philosophy": ["science", "creativity", "technology"],
            "science": ["philosophy", "technology", "humor"],
            "technology": ["philosophy", "science", "society"],
            "creativity": ["philosophy", "humor", "technology"],
            "humor": ["science", "society", "creativity"],
            "society": ["philosophy", "technology", "science"]
        }

        # Adjust based on participants
        available_complements = complements.get(current_topic, [])

        # Prioritize based on participants
        if "philosopher" in participants:
            available_complements.insert(0, "philosophy") if "philosophy" not in available_complements else None
        if "scientist" in participants:
            available_complements.insert(0, "science") if "science" not in available_complements else None
        if "comedian" in participants:
            available_complements.insert(0, "humor") if "humor" not in available_complements else None

        return available_complements[:2]  # Return up to 2 complementary topics