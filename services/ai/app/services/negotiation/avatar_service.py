class AvatarService:

    @staticmethod
    def build_avatar_payload(text: str):

        emotion = "neutral"

        lower = text.lower()

        if "risk" in lower:
            emotion = "serious"

        if "great" in lower or "good" in lower:
            emotion = "happy"

        visemes = [
            {"time": 0.0, "value": "A"},
            {"time": 0.2, "value": "E"},
            {"time": 0.4, "value": "O"},
            {"time": 0.6, "value": "U"},
        ]

        return {
            "emotion": emotion,
            "visemes": visemes,
            "animation": "talking"
        }