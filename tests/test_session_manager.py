import pytest
from qa_evidence_collector.core.session_manager import SessionManager


def test_start_session():
    sm = SessionManager()
    sm.start("TC-001")
    assert sm.is_active
    assert sm.session_name == "TC-001"
    assert sm.steps == []


def test_start_with_empty_name_defaults():
    sm = SessionManager()
    sm.start("")
    assert sm.session_name == "Untitled Session"


def test_add_step_increments_number():
    sm = SessionManager()
    sm.start("TC-001")
    sm.add_step("img1.png", "Step one")
    sm.add_step("img2.png", "Step two")
    assert len(sm.steps) == 2
    assert sm.steps[0].step_number == 1
    assert sm.steps[1].step_number == 2


def test_delete_step_renumbers():
    sm = SessionManager()
    sm.start("TC-001")
    sm.add_step("img1.png")
    sm.add_step("img2.png")
    sm.add_step("img3.png")
    sm.delete_step(0)
    assert len(sm.steps) == 2
    assert sm.steps[0].step_number == 1
    assert sm.steps[1].step_number == 2


def test_move_step_renumbers():
    sm = SessionManager()
    sm.start("TC-001")
    sm.add_step("img1.png", "first")
    sm.add_step("img2.png", "second")
    sm.add_step("img3.png", "third")
    sm.move_step(0, 2)
    assert sm.steps[0].note == "second"
    assert sm.steps[1].note == "third"
    assert sm.steps[2].note == "first"
    assert sm.steps[2].step_number == 3


def test_update_note():
    sm = SessionManager()
    sm.start("TC-001")
    sm.add_step("img1.png", "old note")
    sm.update_note(0, "new note")
    assert sm.steps[0].note == "new note"


def test_serialise_roundtrip():
    sm = SessionManager()
    sm.start("TC-001")
    sm.add_step("img1.png", "hello")
    data = sm.to_dict()

    sm2 = SessionManager()
    sm2.load_dict(data)
    assert sm2.session_name == "TC-001"
    assert len(sm2.steps) == 1
    assert sm2.steps[0].note == "hello"
