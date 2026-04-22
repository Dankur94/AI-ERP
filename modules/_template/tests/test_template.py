"""Tests fuer das Template-Modul."""

from modules._template.module import TemplateModule
from modules.base import Message


class FakeDB:
    def __init__(self):
        self.entries = []

    def add_entry(self, entry_type, text, sender, sender_phone=""):
        self.entries.append({"type": entry_type, "text": text, "sender": sender})


def test_can_handle():
    mod = TemplateModule({}, FakeDB())
    assert mod.can_handle(Message(text="template hello", sender="Test"))
    assert not mod.can_handle(Message(text="unknown hello", sender="Test"))


def test_handle_saves_entry():
    db = FakeDB()
    mod = TemplateModule({}, db)
    resp = mod.handle(Message(text="template test eintrag", sender="Test"))
    assert resp is not None
    assert "Saved" in resp.text
    assert len(db.entries) == 1
