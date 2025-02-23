import pytest
import typer

from fcship.fcship.commands.verify import verify, VerificationError

def dummy_check_success():
    return None

def dummy_check_failure():
    raise VerificationError("Dummy", "failed")

def test_verify_all_success(monkeypatch):
    # For "all", override each check function to simulate success.
    monkeypatch.setattr("fcship.fcship.commands.verify.run_type_checking", lambda: None)
    monkeypatch.setattr("fcship.fcship.commands.verify.run_linting", lambda: None)
    monkeypatch.setattr("fcship.fcship.commands.verify.run_tests", lambda: None)
    monkeypatch.setattr("fcship.fcship.commands.verify.run_format_check", lambda: None)
    # Should complete without raising an exception.
    verify("all")

def test_verify_all_failure(monkeypatch):
    # Simulate a failure in one of the checks.
    monkeypatch.setattr("fcship.fcship.commands.verify.run_type_checking", dummy_check_failure)
    monkeypatch.setattr("fcship.fcship.commands.verify.run_linting", lambda: None)
    monkeypatch.setattr("fcship.fcship.commands.verify.run_tests", lambda: None)
    monkeypatch.setattr("fcship.fcship.commands.verify.run_format_check", lambda: None)
    # Expect a typer.Exit exception because finish_verification raises it on failures.
    with pytest.raises(typer.Exit):
        verify("all")

def test_verify_single_success(monkeypatch):
    # Test a single check ("type") success.
    monkeypatch.setattr("fcship.fcship.commands.verify.run_type_checking", lambda: None)
    verify("type")

def test_verify_single_failure(monkeypatch):
    # Test a single check ("lint") failure.
    monkeypatch.setattr("fcship.fcship.commands.verify.run_linting", dummy_check_failure)
    with pytest.raises(Exception):
        verify("lint")
