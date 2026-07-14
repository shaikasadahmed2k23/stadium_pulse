"""
Lightweight FAQ knowledge base. For a hackathon timeline, simple keyword
matching to retrieve relevant context is enough — avoids needing a full
vector DB setup just for a handful of FAQ topics.
"""

FAQ_DATA = {
    "restroom": "Restrooms are located near every concourse, marked with clear signage. Nearest to Section 101 is at Concourse A.",
    "food": "Concessions are available at Section 101 and both concourses. Most stands accept card and mobile payment.",
    "parking": "Parking is available at Lots A, B, and C. Lot C is closest to Gate 2 and fills up fastest on match days.",
    "ticket": "Tickets can be validated at any gate using the QR code in your FIFA app. Lost tickets can be re-issued at the Box Office near Gate 1.",
    "schedule": "Match schedules and kickoff times are available on the official FIFA World Cup 2026 app and stadium screens.",
    "lost_child": "If you've lost track of a child, immediately alert the nearest staff member or go to the Guest Services desk at Concourse A.",
    "wifi": "Free stadium Wi-Fi is available under network 'FIFA2026-FanZone', no password required.",
    "medical": "Medical stations are located at Concourse A and Concourse B, marked with a red cross sign.",
}


class FAQKnowledge:
    def get_relevant_context(self, message: str) -> str:
        message_lower = message.lower()
        matches = [
            value for key, value in FAQ_DATA.items()
            if key.replace("_", " ") in message_lower or key in message_lower
        ]
        return " ".join(matches) if matches else "No specific FAQ match — answer generally and helpfully."


faq_knowledge = FAQKnowledge()