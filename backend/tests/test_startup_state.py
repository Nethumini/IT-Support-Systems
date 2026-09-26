"""Tests for the startup-item state model.

A startup snapshot used to record only True/False, so a rollback could be
judged by "is it enabled?" alone - which a rollback that did nothing passes
whenever the item was already enabled. Each item now carries two flags and two
fingerprints. These tests pin down what counts as a readable record, and that
no command line survives into one.
"""
import json

from app.services.startup_state import (
    BACKUP_COMMAND_SHA256,
    BACKUP_EXISTS,
    ENABLED,
    ENABLED_COMMAND_SHA256,
    command_fingerprint,
    read_startup_record,
    read_startup_snapshot,
    startup_record,
)

COMMAND = r'"C:\Users\someone\AppData\Local\App\app.exe" --token=do-not-publish'
OTHER = r'"C:\Program Files\Other\other.exe"'


def test_the_fingerprint_is_plain_sha256_over_utf8():
    """The PowerShell query computes SHA-256 over UTF-8 in lower-case hex.

    The standard test vector pins this side to the same algorithm, so a
    fingerprint read on Windows and one made by the simulator are comparable.
    """
    assert command_fingerprint("abc") == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_different_commands_have_different_fingerprints():
    assert command_fingerprint(COMMAND) != command_fingerprint(OTHER)


def test_a_record_holds_flags_and_fingerprints_only():
    record = startup_record(COMMAND, OTHER)

    assert set(record) == {ENABLED, BACKUP_EXISTS, ENABLED_COMMAND_SHA256, BACKUP_COMMAND_SHA256}
    assert record[ENABLED] is True and record[BACKUP_EXISTS] is True
    assert record[ENABLED_COMMAND_SHA256] == command_fingerprint(COMMAND)
    assert record[BACKUP_COMMAND_SHA256] == command_fingerprint(OTHER)
    text = json.dumps(record)
    assert "app.exe" not in text and "do-not-publish" not in text


def test_an_absent_value_has_no_fingerprint():
    record = startup_record(None, COMMAND)
    assert record[ENABLED] is False
    assert record[ENABLED_COMMAND_SHA256] is None


def test_a_complete_record_reads_back_unchanged():
    record = startup_record(COMMAND, None)
    assert read_startup_record(record) == record


def test_the_old_true_false_form_is_unreadable():
    """What an agent that has not been updated sends. It proves nothing about
    which command is registered, so it must not be read as if it did."""
    assert read_startup_record(True) is None
    assert read_startup_record(False) is None


def test_a_flag_without_its_fingerprint_is_unreadable():
    record = startup_record(COMMAND, None)
    record[ENABLED_COMMAND_SHA256] = None
    assert read_startup_record(record) is None


def test_a_fingerprint_without_its_flag_is_unreadable():
    record = startup_record(None, COMMAND)
    record[ENABLED_COMMAND_SHA256] = command_fingerprint(OTHER)
    assert read_startup_record(record) is None


def test_a_command_where_a_fingerprint_belongs_is_refused():
    """A driver that leaked the text instead of hashing it must not have the
    text carried any further."""
    record = startup_record(COMMAND, None)
    record[ENABLED_COMMAND_SHA256] = COMMAND
    assert read_startup_record(record) is None


def test_flags_must_be_real_booleans():
    record = startup_record(COMMAND, None)
    record[ENABLED] = "true"
    assert read_startup_record(record) is None

    record = startup_record(COMMAND, None)
    record[BACKUP_EXISTS] = 0
    assert read_startup_record(record) is None


def test_unknown_fields_are_not_carried():
    record = {**startup_record(COMMAND, None), "command": COMMAND}
    parsed = read_startup_record(record)

    assert parsed is not None
    assert "command" not in parsed
    assert "app.exe" not in json.dumps(parsed)


def test_upper_case_fingerprints_are_accepted_and_normalised():
    record = startup_record(COMMAND, None)
    record[ENABLED_COMMAND_SHA256] = record[ENABLED_COMMAND_SHA256].upper()
    assert read_startup_record(record)[ENABLED_COMMAND_SHA256] == command_fingerprint(COMMAND)


def test_a_snapshot_keeps_readable_items_and_leaves_out_the_rest():
    snapshot = read_startup_snapshot({
        "Good": startup_record(COMMAND, None),
        "Old": True,
        "Leaky": {**startup_record(None, COMMAND), BACKUP_COMMAND_SHA256: COMMAND},
        "": startup_record(OTHER, None),
    })
    assert set(snapshot) == {"Good"}


def test_a_snapshot_that_is_not_a_mapping_is_empty():
    assert read_startup_snapshot(["Teams"]) == {}
    assert read_startup_snapshot(None) == {}
