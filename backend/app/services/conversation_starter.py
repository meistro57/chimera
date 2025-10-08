import random
from typing import List, Dict, Any

class ConversationStarter:
    """Service for generating engaging conversation starters for AI personas"""

    def __init__(self):
        self.starters = self._load_starters()

    def _load_starters(self) -> Dict[str, List[str]]:
        """Load conversation starters categorized by themes"""
        return {
            "general": [
                "What's the most interesting thing you've learned recently?",
                "If you could time travel, what era would you visit and why?",
                "What do you think is the biggest misunderstanding about your field?",
                "How do you think technology will change our daily lives in the next decade?",
                "What's a question you've always wanted to ask another perspective?",
                "What makes a truly meaningful conversation vs. just chit-chat?"
            ],

            "philosophical": [
                "What does it mean to be truly 'conscious' or 'aware'?",
                "Is free will an illusion or a fundamental aspect of existence?",
                "How do we define what's 'real' in an age of simulation and AI?",
                "What's more important: pursuing happiness or doing what's right?",
                "Can morality be programmed? Should it be?",
                "What makes human experience unique in the universe?"
            ],

            "scientific": [
                "What's the most elegant scientific theory you've encountered?",
                "How close are we to solving quantum gravity?",
                "What's an unsolved mystery in science that intrigues you?",
                "How might AI contribute to scientific discovery?",
                "What's the relationship between elegance and truth in physics?",
                "Could there be universes with different fundamental constants?"
            ],

            "humorous": [
                "If you were a kitchen appliance, which one would you be and why?",
                "What's the most ridiculous thing about human behavior?",
                "If animals could talk, which one would be the most annoying?",
                "What's a conspiracy theory you secretly think might be true?",
                "If you could get away with one ridiculous idea, what would it be?",
                "What's the funniest misunderstanding you've witnessed?"
            ],

            "technology": [
                "Will we achieve general AI before we perfect driverless cars?",
                "Should we pursue advanced AI even if it means job displacement?",
                "What's the most transformative technology you've seen so far?",
                "How should society approach the ethics of AI development?",
                "What problems seem intractable without AI assistance?",
                "Is there such a thing as 'friendly AI' or is that just optimism?"
            ],

            "creativity": [
                "Can machines truly be creative, or do they just recombine ideas?",
                "What makes art meaningful to humans?",
                "How might AI change the process of artistic creation?",
                "Is there a difference between human and machine intuition?",
                "What human creative pursuits might AI enhance rather than replace?",
                "Does creativity require consciousness?"
            ]
        }

    def get_random_starter(self, participants: List[str], theme: str = None) -> str:
        """
        Get a random conversation starter, considering participants

        Args:
            participants: List of persona names participating
            theme: Optional theme to guide starter selection
        """
        available_themes = list(self.starters.keys())

        # Choose theme based on participants if no theme specified
        if theme is None:
            theme = self._select_theme_for_participants(participants)

        # Get starters for chosen theme
        theme_starters = self.starters.get(theme, self.starters["general"])

        return random.choice(theme_starters)

    def _select_theme_for_participants(self, participants: List[str]) -> str:
        """
        Select an appropriate theme based on participating personas
        """
        if set(participants) == {"philosopher", "comedian", "scientist"}:
            # Full group - mix philosophical with humor
            return random.choice(["philosophical", "technology", "creativity"])

        elif "philosopher" in participants and "scientist" in participants:
            # Deep thinkers - focus on fundamental questions
            return random.choice(["philosophical", "scientific", "technology"])

        elif "philosopher" in participants and "comedian" in participants:
            # Philosophy with humor - creative thinking
            return random.choice(["philosophical", "humorous", "creativity"])

        elif "scientist" in participants and "comedian" in participants:
            # Logic with humor - interesting contrast
            return random.choice(["scientific", "humorous", "technology"])

        elif "philosopher" in participants:
            # Just philosopher - deep topics
            return random.choice(["philosophical", "technology"])

        elif "scientist" in participants:
            # Just scientist - analytical topics
            return random.choice(["scientific", "technology"])

        elif "comedian" in participants:
            # Just comedian - entertaining topics
            return random.choice(["humorous", "creativity", "general"])

        # Default fallback
        return random.choice(["general", "technology"])

    def get_starters_for_conversation(self, conversation_length: int = 1) -> List[str]:
        """
        Get multiple starters for a longer conversation
        """
        available_themes = list(self.starters.keys())
        starters = []

        for i in range(conversation_length):
            theme = random.choice(available_themes)
            starters.append(random.choice(self.starters[theme]))

        return starters

    def get_theme_based_starter(self, theme: str) -> str:
        """
        Get a starter specifically for a given theme
        """
        if theme in self.starters:
            return random.choice(self.starters[theme])
        else:
            # Fallback to general
            return random.choice(self.starters["general"])