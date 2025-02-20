from unittest.mock import MagicMock, patch
from sqlmodel import select
from app.tests_pre_start import init, logger

def test_init_successful_connection() -> None:
    # Create a session factory mock that returns a session with working exec
    session_mock = MagicMock()
    session_mock.exec.return_value = MagicMock()

    with (
        patch("sqlmodel.Session", MagicMock(return_value=session_mock)),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            init(MagicMock())  # Pass a mock engine
            connection_successful = True
        except Exception as e:
            connection_successful = False
            print(f"Connection failed with: {e}")

        assert connection_successful, "The database connection should be successful and not raise an exception."