"""Template module ??adjust description here."""

import re
from modules.base import BaseModule, Message, Response

_CMD_RE = re.compile(r"^(?:template)\s+(.+)$", re.IGNORECASE | re.DOTALL)


class TemplateModule(BaseModule):
    COMMANDS = ["template"]
    VOICE_INFO = {
        "command": "template <text>",
        "examples": [
            ("example input", "template example input"),
        ],
    }

    def can_handle(self, msg: Message) -> bool:
        return bool(_CMD_RE.match(msg.text.strip()))

    def handle(self, msg: Message) -> Response | None:
        m = _CMD_RE.match(msg.text.strip())
        if not m:
            return None
        text = m.group(1).strip()
        if not text:
            return Response(text="What would you like to log?")
        display = text[:45].rstrip()
        self.db.add_entry("template", text, msg.sender, msg.sender_phone)
        return Response(text=f"Saved: {display}")
