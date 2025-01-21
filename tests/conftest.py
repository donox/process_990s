# tests/conftest.py
import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_db():
    mock_conn = Mock()
    mock_cursor = MagicMock()  # Changed to MagicMock

    zip_data = {
        "90210": (34.0901, -118.4065),
        "10001": (40.7500, -73.9967),
        "12345": (42.8140, -73.9407)
    }

    def mock_execute(query, params=None):
        mock_cursor._last_query = query
        mock_cursor._last_params = params

    def mock_fetchone():
        if mock_cursor._last_query.strip().lower().startswith("select latitude, longitude"):
            zipcode = mock_cursor._last_params[0]
            return zip_data.get(zipcode)
        return None

    mock_cursor.execute = mock_execute
    mock_cursor.fetchone = mock_fetchone

    # Create a context manager for cursor
    cm = MagicMock()
    cm.__enter__.return_value = mock_cursor
    cm.__exit__.return_value = None
    mock_conn.cursor.return_value = cm

    return mock_conn