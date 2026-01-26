"""Unit tests for app/common/utils.py"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import mock_open, patch

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from common.utils import load_data, get_geojson_center, get_geojson_bbox


class TestLoadData:
    """Test cases for load_data function"""

    def test_load_data_success(self):
        """データファイルの正常読み込み"""
        mock_data = {"type": "FeatureCollection", "features": []}
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = load_data("test_region")
            assert result == mock_data

    def test_load_data_file_not_found(self):
        """存在しないファイルの読み込み"""
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent_file")


class TestGetGeojsonCenter:
    """Test cases for get_geojson_center function"""

    def test_get_geojson_center_polygon(self):
        """Polygon型のGeoJSONの中心計算"""
        geojson = {
            "features": [
                {
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]
                        ]
                    }
                }
            ]
        }
        center_lat, center_lon = get_geojson_center(geojson)
        assert center_lat == 5.0
        assert center_lon == 5.0

    def test_get_geojson_center_multipolygon(self):
        """MultiPolygon型の中心計算"""
        geojson = {
            "features": [
                {
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [
                                [[0.0, 0.0], [5.0, 0.0], [5.0, 5.0], [0.0, 5.0], [0.0, 0.0]]
                            ],
                            [
                                [[5.0, 5.0], [10.0, 5.0], [10.0, 10.0], [5.0, 10.0], [5.0, 5.0]]
                            ]
                        ]
                    }
                }
            ]
        }
        center_lat, center_lon = get_geojson_center(geojson)
        assert center_lat == 5.0
        assert center_lon == 5.0

    def test_get_geojson_center_empty(self):
        """空のGeoJSON"""
        geojson = {"features": []}
        with pytest.raises(ValueError, match="GeoJSON に有効な座標が含まれていません"):
            get_geojson_center(geojson)

    def test_get_geojson_center_none_geometry(self):
        """geometry=Noneのケース"""
        geojson = {
            "features": [
                {"geometry": None},
                {
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]
                        ]
                    }
                }
            ]
        }
        center_lat, center_lon = get_geojson_center(geojson)
        assert center_lat == 5.0
        assert center_lon == 5.0


class TestGetGeojsonBbox:
    """Test cases for get_geojson_bbox function"""

    def test_get_geojson_bbox(self):
        """バウンディングボックスの計算"""
        geojson = {
            "features": [
                {
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]
                        ]
                    }
                }
            ]
        }
        bbox = get_geojson_bbox(geojson)
        assert bbox == [0.0, 0.0, 10.0, 10.0]  # [min_lon, min_lat, max_lon, max_lat]
