# tests/test_geo_utils.py
import pytest
from src.data_sources.grant_analysis.geo_utils import ZipDistance


def test_zip_coordinates(mock_db):
    zip_dist = ZipDistance(mock_db)
    coords = zip_dist.get_zip_coordinates("90210")
    assert coords == (34.0901, -118.4065)


def test_unknown_zip(mock_db):
    zip_dist = ZipDistance(mock_db)
    coords = zip_dist.get_zip_coordinates("99999")  # Not in mock data
    assert coords is None


def test_distance_calculation(mock_db):
    zip_dist = ZipDistance(mock_db)
    distance = zip_dist.calculate_distance("90210", "10001")
    assert distance is not None
    assert 2400 < distance < 2500  # Approximate cross-country distance