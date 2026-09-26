"""Tests for the execution drivers.

The important ones are at the bottom: a driver must be able to report success
while leaving the problem in place, because that is the case post-action
verification exists to catch (thesis 8, test case TC08).
"""
import platform

import pytest

from app.services.execution import (
    ExecutionError,
    SimulatedDriver,
    SimulatedSystem,
    get_driver,
    reset_driver,
)


@pytest.fixture
def driver():
    return SimulatedDriver(SimulatedSystem())


@pytest.fixture(autouse=True)
def _clean_driver_cache():
    reset_driver()
    yield
    reset_driver()


# --------------------------------------------------------------------------
# Driver selection
# --------------------------------------------------------------------------

def test_simulated_driver_is_always_available():
    assert SimulatedDriver().is_available() is True


def test_explicit_simulated_selection():
    assert get_driver("simulated").name == "simulated"


def test_auto_selects_simulated_off_windows():
    expected = "powershell" if platform.system() == "Windows" else "simulated"
    assert get_driver("auto").name == expected


def test_powershell_falls_back_off_windows():
    """Asking for powershell on macOS must not crash the app - it degrades to
    the simulated driver so remediation stays testable."""
    if platform.system() == "Windows":
        pytest.skip("fallback only applies off Windows")
    assert get_driver("powershell").name == "simulated"


def test_unknown_driver_is_rejected():
    with pytest.raises(ExecutionError):
        get_driver("magic")


def test_get_driver_caches_one_instance():
    assert get_driver() is get_driver()


# --------------------------------------------------------------------------
# Allow-list: only registered actions, never free-form commands
# --------------------------------------------------------------------------

def test_unregistered_action_is_refused(driver):
    with pytest.raises(ExecutionError):
        driver.execute("rm_rf_everything")


def test_command_string_cannot_be_passed_as_an_action(driver):
    with pytest.raises(ExecutionError):
        driver.execute("Remove-Item C:\\ -Recurse -Force")


def test_supports_reports_registered_actions(driver):
    assert driver.supports("clear_temp_files") is True
    assert driver.supports("not_an_action") is False


# --------------------------------------------------------------------------
# State capture
# --------------------------------------------------------------------------

def test_capture_state_does_not_change_anything(driver):
    first = driver.capture_state("disk")
    second = driver.capture_state("disk")
    assert first == second


def test_unknown_scope_is_rejected(driver):
    with pytest.raises(ExecutionError):
        driver.capture_state("nonsense")


def test_capture_all_covers_every_scope(driver):
    state = driver.capture_state("all")
    for scope in ("disk", "processes", "network", "services", "startup", "updates"):
        assert scope in state


# --------------------------------------------------------------------------
# Actions actually change the world
# --------------------------------------------------------------------------

def test_clear_temp_files_frees_disk_space(driver):
    before = driver.system.disk_free_gb
    result = driver.execute("clear_temp_files")
    assert result.success is True
    assert driver.system.disk_free_gb > before
    assert driver.system.temp_files_mb == 0


def test_result_carries_before_and_after_state(driver):
    result = driver.execute("clear_temp_files")
    assert result.state_before["disk_free_gb"] < result.state_after["disk_free_gb"]


def test_kill_process_removes_it(driver):
    pid = driver.system.processes[0].pid
    result = driver.execute("kill_process_by_id", {"pid": pid})
    assert result.success is True
    assert driver.system.find_process(pid) is None


def test_kill_unknown_process_fails_without_raising(driver):
    """A failed action is a result, not an exception - the orchestrator needs
    to record it, not crash."""
    result = driver.execute("kill_process_by_id", {"pid": 999999})
    assert result.success is False
    assert result.error


def test_restart_service_starts_a_stopped_service(driver):
    assert driver.system.services["Spooler"] == "stopped"
    result = driver.execute("restart_service", {"service_name": "Spooler"})
    assert result.success is True
    assert driver.system.services["Spooler"] == "running"


def test_restart_service_requires_a_name(driver):
    result = driver.execute("restart_service", {})
    assert result.success is False


def test_flush_dns_empties_the_cache(driver):
    assert driver.system.dns_cache_entries > 0
    driver.execute("flush_dns")
    assert driver.system.dns_cache_entries == 0


def test_reset_winsock_repairs_stack_and_needs_reboot(driver):
    assert driver.system.winsock_healthy is False
    driver.execute("reset_winsock")
    assert driver.system.winsock_healthy is True
    assert driver.system.reboot_required is True


def test_disable_startup_item_turns_it_off(driver):
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    assert driver.system.startup_items["Spotify"] is False


def test_disabling_saves_what_it_removed(driver):
    """The real action copies the startup command to a key of its own first.

    Without that record there is nothing to restore, and the rollback the
    contract advertises could not be performed on a real machine.
    """
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    assert "Spotify" in driver.system.startup_backup


def test_enable_startup_item_puts_it_back(driver):
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    result = driver.execute("enable_startup_item", {"item_name": "Spotify"})
    assert result.success is True
    assert driver.system.startup_items["Spotify"] is True


def test_enabling_an_item_this_system_never_disabled_fails(driver):
    """It restores a saved command and cannot invent one."""
    result = driver.execute("enable_startup_item", {"item_name": "OneDrive"})
    assert result.success is False
    assert "no saved startup command" in (result.error or "").lower()


def test_a_self_restoring_item_comes_back_on_its_own(driver):
    """Teams re-registers itself, as it does in reality.

    The command succeeds and the machine is unchanged, which is the failure
    only a post-check can see.
    """
    result = driver.execute("disable_startup_item", {"item_name": "Teams"})
    assert result.success is True
    assert driver.system.startup_items["Teams"] is True


def test_simulated_startup_state_follows_the_windows_model(driver):
    """Same four fields as the PowerShell driver reports, and no command text."""
    from app.services.startup_state import read_startup_record

    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    snapshot = driver.capture_state("startup")

    for name, record in snapshot.items():
        assert read_startup_record(record) == record, name
    for command in driver.system.startup_commands.values():
        assert command not in json.dumps(snapshot)
    assert "Spotify.exe" not in json.dumps(snapshot)


def test_disabling_saves_the_command_it_removed_unchanged(driver):
    before = driver.capture_state("startup")["Spotify"]
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    after = driver.capture_state("startup")["Spotify"]

    assert after["enabled"] is False
    assert after["backup_exists"] is True
    assert after["backup_command_sha256"] == before["enabled_command_sha256"]


def test_enabling_restores_the_saved_command_and_consumes_the_copy(driver):
    original = driver.capture_state("startup")["Spotify"]["enabled_command_sha256"]
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    driver.execute("enable_startup_item", {"item_name": "Spotify"})
    after = driver.capture_state("startup")["Spotify"]

    assert after["enabled_command_sha256"] == original
    assert after["backup_exists"] is False


def test_disabling_an_item_that_is_not_registered_fails(driver):
    """Mirrors the real action, which reads the Run value first and stops."""
    driver.execute("disable_startup_item", {"item_name": "Spotify"})
    result = driver.execute("disable_startup_item", {"item_name": "Spotify"})

    assert result.success is False
    assert "not found" in (result.error or "")
    assert "Spotify" in driver.system.startup_backup


def test_close_browser_tabs_releases_memory(driver):
    before = driver.system.total_memory_mb()
    result = driver.execute("close_browser_tabs")
    assert result.success is True
    assert driver.system.total_memory_mb() < before


def test_read_only_action_leaves_state_unchanged(driver):
    before = driver.capture_state("disk")
    driver.execute("check_disk_space")
    assert driver.capture_state("disk") == before


# --------------------------------------------------------------------------
# Fault injection - the verification-failure scenario (TC08)
# --------------------------------------------------------------------------

def test_injected_fault_reports_success(driver):
    driver.inject_fault("clear_temp_files")
    result = driver.execute("clear_temp_files")
    assert result.success is True


def test_injected_fault_changes_nothing(driver):
    """The command 'worked' and the problem remains. This is exactly the case
    that must not be reported as a resolved ticket."""
    driver.inject_fault("clear_temp_files")
    before = driver.system.disk_free_gb
    result = driver.execute("clear_temp_files")
    assert result.success is True
    assert driver.system.disk_free_gb == before
    assert result.state_before == result.state_after


def test_injected_fault_is_flagged_for_evaluation(driver):
    """Evaluation data must separate injected failures from genuine ones."""
    driver.inject_fault("clear_temp_files")
    assert driver.execute("clear_temp_files").fault_injected is True


def test_normal_execution_is_not_flagged_as_faulted(driver):
    assert driver.execute("clear_temp_files").fault_injected is False


def test_faults_can_be_cleared(driver):
    driver.inject_fault("clear_temp_files")
    driver.clear_faults()
    result = driver.execute("clear_temp_files")
    assert result.fault_injected is False
    assert result.state_before != result.state_after


def test_fault_affects_only_the_named_action(driver):
    driver.inject_fault("clear_temp_files")
    result = driver.execute("flush_dns")
    assert result.fault_injected is False
    assert driver.system.dns_cache_entries == 0


# --------------------------------------------------------------------------
# Result shape
# --------------------------------------------------------------------------

def test_result_is_serialisable_for_audit(driver):
    import json

    payload = json.dumps(driver.execute("check_disk_space").to_dict())
    restored = json.loads(payload)
    assert restored["driver"] == "simulated"
    assert restored["action_id"] == "check_disk_space"


def test_result_names_the_driver_used(driver):
    assert driver.execute("check_disk_space").driver == "simulated"


# --------------------------------------------------------------------------
# Scenario: the machine starts broken, and can be fixed
# --------------------------------------------------------------------------

def test_low_disk_scenario_can_be_resolved(driver):
    assert driver.system.disk_free_gb < 10
    driver.execute("clear_temp_files")
    driver.execute("empty_recycle_bin")
    driver.execute("windows_disk_cleanup")
    assert driver.system.disk_free_gb > 10


def test_starting_state_represents_a_real_problem(driver):
    """Scenarios should not have to set up the fault first."""
    assert driver.system.disk_free_gb < 10
    assert driver.system.services["Spooler"] == "stopped"
    assert driver.system.winsock_healthy is False


# --------------------------------------------------------------------------
# Windows startup snapshot
#
# The PowerShell driver could not read the startup scope at all, so every
# startup remediation on a real machine post-checked as inconclusive and no
# rollback could ever be verified there. These tests run the parsing on any
# host; the query itself needs Windows.
# --------------------------------------------------------------------------

import json
import subprocess
from types import SimpleNamespace

from app.services.execution.powershell import PowerShellDriver


def _driver_reading(monkeypatch, stdout, returncode=0):
    driver = PowerShellDriver.__new__(PowerShellDriver)
    driver.timeout_seconds = 5
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: SimpleNamespace(stdout=stdout, stderr="", returncode=returncode),
    )
    return driver


TEAMS_COMMAND = r'"C:\Users\someone\AppData\Local\Microsoft\Teams\Update.exe" --processStart "Teams.exe"'
RECORDER_COMMAND = r'"C:\Program Files\ScreenRecorder\recorder.exe" --tray'


def test_startup_snapshot_reads_enabled_and_disabled_items(monkeypatch):
    from app.services.startup_state import startup_record

    reported = {
        "Teams": startup_record(TEAMS_COMMAND, None),
        "ScreenRecorder": startup_record(None, RECORDER_COMMAND),
    }
    driver = _driver_reading(monkeypatch, json.dumps(reported))
    assert driver.capture_state("startup") == reported


def test_a_disabled_item_stays_in_the_snapshot(monkeypatch):
    """It must read as disabled with a saved copy, not vanish.

    A missing key means "cannot tell" to the post-check, which is a different
    answer from "turned off" - and the difference decides whether a rollback
    is judged to have restored the machine.
    """
    from app.services.startup_state import startup_record

    reported = {"ScreenRecorder": startup_record(None, RECORDER_COMMAND)}
    driver = _driver_reading(monkeypatch, json.dumps(reported))
    snapshot = driver.capture_state("startup")

    assert snapshot["ScreenRecorder"]["enabled"] is False
    assert snapshot["ScreenRecorder"]["backup_exists"] is True


def test_an_old_true_false_snapshot_is_not_trusted(monkeypatch):
    """The format before fingerprints. It is left out rather than read, so the
    checks refuse before acting and report inconclusive after."""
    driver = _driver_reading(monkeypatch, '{"Teams":true,"ScreenRecorder":false}')
    assert driver.capture_state("startup") == {}


def test_a_command_in_the_snapshot_never_gets_through(monkeypatch):
    """If the query ever printed a command instead of its hash, the record is
    dropped and the text goes no further than this parser."""
    from app.services.startup_state import startup_record

    leaky = {**startup_record(TEAMS_COMMAND, None), "enabled_command_sha256": TEAMS_COMMAND}
    extra = {**startup_record(None, RECORDER_COMMAND), "command": RECORDER_COMMAND}
    driver = _driver_reading(monkeypatch, json.dumps({"Teams": leaky, "ScreenRecorder": extra}))
    snapshot = driver.capture_state("startup")

    assert "Teams" not in snapshot
    assert set(snapshot["ScreenRecorder"]) == {
        "enabled", "backup_exists", "enabled_command_sha256", "backup_command_sha256",
    }
    text = json.dumps(snapshot)
    assert "Update.exe" not in text and "recorder.exe" not in text


def test_the_windows_query_prints_only_fingerprints_of_values():
    """Every registry value the query reads goes through the hash first.

    The query itself needs Windows to run; this guards the one property that
    matters for privacy against a later edit that prints a value directly.
    """
    query = PowerShellDriver._STARTUP_QUERY
    reads = query.count("GetValue($name)")

    assert "SHA256" in query
    assert reads == 2
    assert query.count("Get-AutoOpsFingerprint ($key.GetValue($name))") == reads
    assert "-Depth" in query


# --------------------------------------------------------------------------
# The startup-programs diagnostic reports names only
#
# It used to select Name, Command and Location, so every run stored each
# program's full command line - paths, user names, arguments - and its
# registry or folder location, in the execution result, the API response and
# the chat. The command itself needs Windows; these tests pin what it asks for.
# --------------------------------------------------------------------------

import re


def _startup_programs_command():
    from app.services.agents.action_executor_agent import ActionExecutorAgent

    return ActionExecutorAgent().actions["get_startup_programs"].command_template


def test_the_startup_programs_diagnostic_never_asks_for_the_command_line():
    # The WMI class is named Win32_StartupCommand; nothing else may say Command.
    without_class = _startup_programs_command().replace("Win32_StartupCommand", "")
    assert "Command" not in without_class


def test_the_startup_programs_diagnostic_never_asks_for_the_location():
    assert "Location" not in _startup_programs_command()


def test_the_startup_programs_diagnostic_reads_the_name_and_nothing_else():
    """Each startup entry is touched through one property, and it is Name.
    No other selection, expansion or formatting of the entry exists."""
    command = _startup_programs_command()

    assert re.findall(r"\$_\.(\w+)", command) == ["Name"]
    assert "Select-Object" not in command
    assert "Format-" not in command
    assert "ExpandProperty" not in command


def test_the_startup_programs_output_is_a_json_array_of_unique_sorted_names():
    """Piping into ConvertTo-Json prints nothing for zero programs and a bare
    string for one; passing the array as -InputObject gives [] and ["x"]."""
    command = _startup_programs_command()

    assert "ConvertTo-Json -InputObject $names" in command
    assert "$names = @(" in command
    assert "| ConvertTo-Json" not in command
    assert "Sort-Object -Unique" in command


def test_an_unreadable_startup_list_fails_instead_of_reading_as_empty():
    """Without Stop, an access error would still print [] and exit 0, which
    says nothing starts at logon when nobody could tell."""
    assert "Win32_StartupCommand -ErrorAction Stop" in _startup_programs_command()


def test_the_windows_driver_runs_the_names_only_command(monkeypatch):
    """What reaches powershell.exe is the registered command, unaltered, and
    its output is passed back as it came."""
    from app.services.execution import powershell as ps

    commands = []

    def fake_run(argv, **_kwargs):
        commands.append(argv[-1])
        if argv[-1] == PowerShellDriver._STARTUP_QUERY:
            return SimpleNamespace(stdout="{}", stderr="", returncode=0)
        return SimpleNamespace(stdout='["OneDrive","Teams"]', stderr="", returncode=0)

    monkeypatch.setattr(ps.platform, "system", lambda: "Windows")
    monkeypatch.setattr(subprocess, "run", fake_run)

    result = PowerShellDriver().execute("get_startup_programs")

    executed = [c for c in commands if c != PowerShellDriver._STARTUP_QUERY]
    assert executed == [_startup_programs_command()]
    assert json.loads(result.output) == ["OneDrive", "Teams"]


def test_the_simulated_startup_programs_output_holds_no_path_or_argument(driver):
    output = driver.execute("get_startup_programs").output

    for command in driver.system.startup_commands.values():
        assert command not in output
    assert "\\" not in output and ".exe" not in output and "--" not in output


def test_an_unreadable_snapshot_is_empty_not_invented(monkeypatch):
    driver = _driver_reading(monkeypatch, "", returncode=1)
    assert driver.capture_state("startup") == {}


def test_a_broken_snapshot_does_not_raise(monkeypatch):
    driver = _driver_reading(monkeypatch, "not json at all")
    assert driver.capture_state("startup") == {}


class _FakeService:
    def __init__(self, name, status):
        self._name, self._status = name, status

    def name(self):
        return self._name

    def status(self):
        if self._status is None:
            raise PermissionError("Access is denied")
        return self._status


def _driver_with_services(monkeypatch, services):
    import psutil

    monkeypatch.setattr(psutil, "win_service_iter", lambda: services, raising=False)
    driver = PowerShellDriver.__new__(PowerShellDriver)
    driver.timeout_seconds = 5
    return driver


def test_services_snapshot_maps_names_to_run_states(monkeypatch):
    """Without this the post-check for a service restart could never see the
    service, so it reported inconclusive on every real machine."""
    driver = _driver_with_services(monkeypatch, [
        _FakeService("Spooler", "stopped"),
        _FakeService("Dnscache", "running"),
    ])
    assert driver.capture_state("services") == {"Spooler": "stopped", "Dnscache": "running"}


def test_a_service_that_cannot_be_read_is_left_out_not_guessed(monkeypatch):
    """A protected service is one this process cannot speak for.

    Leaving it out makes the post-check say inconclusive, which is true.
    Inventing a state for it would make the post-check say something false.
    """
    driver = _driver_with_services(monkeypatch, [
        _FakeService("ProtectedThing", None),
        _FakeService("Dnscache", "running"),
    ])
    assert driver.capture_state("services") == {"Dnscache": "running"}


def test_services_are_empty_when_they_cannot_be_enumerated(monkeypatch):
    import psutil

    def explode():
        raise RuntimeError("not Windows")

    monkeypatch.setattr(psutil, "win_service_iter", explode, raising=False)
    driver = PowerShellDriver.__new__(PowerShellDriver)
    driver.timeout_seconds = 5
    assert driver.capture_state("services") == {}


class _Addr:
    def __init__(self, family, address):
        self.family, self.address = family, address


class _Stat:
    def __init__(self, isup):
        self.isup = isup


def _driver_with_network(monkeypatch, addrs, stats, dns=None):
    import socket

    import psutil

    monkeypatch.setattr(psutil, "net_if_addrs", lambda: addrs)
    monkeypatch.setattr(psutil, "net_if_stats", lambda: stats)

    driver = PowerShellDriver.__new__(PowerShellDriver)
    driver.timeout_seconds = 5
    monkeypatch.setattr(driver, "_dns_cache_entries", lambda: dns)
    return driver, socket


def test_connected_means_a_usable_address_not_merely_an_interface(monkeypatch):
    """It used to mean "this machine has network cards", which a laptop in a
    drawer also has - and the adapter reset reads this field."""
    import socket

    driver, _ = _driver_with_network(
        monkeypatch,
        {"Ethernet": [_Addr(socket.AF_INET, "192.168.1.48")]},
        {"Ethernet": _Stat(isup=True)},
    )
    assert driver.capture_state("network")["connected"] is True


def test_an_interface_that_is_down_is_not_connected(monkeypatch):
    import socket

    driver, _ = _driver_with_network(
        monkeypatch,
        {"Ethernet": [_Addr(socket.AF_INET, "192.168.1.48")]},
        {"Ethernet": _Stat(isup=False)},
    )
    assert driver.capture_state("network")["connected"] is False


def test_the_address_windows_assigns_when_it_failed_is_not_connected(monkeypatch):
    """169.254.x.x is what Windows gives itself when DHCP got no answer."""
    import socket

    driver, _ = _driver_with_network(
        monkeypatch,
        {"Wi-Fi": [_Addr(socket.AF_INET, "169.254.10.4")]},
        {"Wi-Fi": _Stat(isup=True)},
    )
    assert driver.capture_state("network")["connected"] is False


def test_loopback_alone_is_not_connected(monkeypatch):
    import socket

    driver, _ = _driver_with_network(
        monkeypatch,
        {"Loopback": [_Addr(socket.AF_INET, "127.0.0.1")]},
        {"Loopback": _Stat(isup=True)},
    )
    assert driver.capture_state("network")["connected"] is False


def test_the_dns_cache_size_is_reported_when_it_can_be_read(monkeypatch):
    import socket

    driver, _ = _driver_with_network(
        monkeypatch,
        {"Ethernet": [_Addr(socket.AF_INET, "10.0.0.5")]},
        {"Ethernet": _Stat(isup=True)},
        dns=37,
    )
    assert driver.capture_state("network")["dns_cache_entries"] == 37


def test_an_unreadable_dns_cache_is_left_out_so_the_check_refuses(monkeypatch):
    import socket

    driver, _ = _driver_with_network(
        monkeypatch,
        {"Ethernet": [_Addr(socket.AF_INET, "10.0.0.5")]},
        {"Ethernet": _Stat(isup=True)},
        dns=None,
    )
    assert "dns_cache_entries" not in driver.capture_state("network")
