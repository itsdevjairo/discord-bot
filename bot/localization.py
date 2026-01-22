from __future__ import annotations

from dataclasses import dataclass


MESSAGES = {
    "en": {
        "welcome": "👋 Welcome to {guild}, {member}!",
        "goodbye": "👋 {member} has left {guild}.",
        "auto_role_added": "✅ Assigned auto-role {role} to {member}.",
        "suggestion_received": "✅ Suggestion received! ID: {suggestion_id}",
        "ticket_created": "✅ Ticket created in {channel}.",
        "ticket_closed": "✅ Ticket closed. Transcript ID: {transcript_id}",
    },
    "nl": {
        "welcome": "👋 Welkom bij {guild}, {member}!",
        "goodbye": "👋 {member} heeft {guild} verlaten.",
        "auto_role_added": "✅ Auto-rol {role} toegevoegd aan {member}.",
        "suggestion_received": "✅ Suggestie ontvangen! ID: {suggestion_id}",
        "ticket_created": "✅ Ticket aangemaakt in {channel}.",
        "ticket_closed": "✅ Ticket gesloten. Transcript ID: {transcript_id}",
    },
}


@dataclass
class Localizer:
    language: str

    def t(self, key: str, **kwargs: object) -> str:
        bundle = MESSAGES.get(self.language, MESSAGES["en"])
        template = bundle.get(key, MESSAGES["en"].get(key, key))
        return template.format(**kwargs)
