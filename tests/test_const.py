"""Unit tests for app/common/const.py"""

import sys
from pathlib import Path

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from common.const import Const


class TestConst:
    """Test cases for Const class"""

    def test_prefectures_count(self):
        """都道府県データの件数"""
        const = Const()
        # 47都道府県存在する（重複を除く）
        unique_prefectures = set([pref[0] for pref in const.prefectures])
        assert len(unique_prefectures) == 47

    def test_prefecture_data_format(self):
        """データフォーマットの確認"""
        const = Const()
        # (都道府県名, 市町村名, 緯度, 経度)の形式
        for pref_data in const.prefectures:
            assert len(pref_data) == 4
            prefecture, city, lat, lon = pref_data
            assert isinstance(prefecture, str)
            assert isinstance(city, str)
            assert isinstance(lat, (int, float))
            assert isinstance(lon, (int, float))

    def test_coordinate_range(self):
        """座標の範囲チェック"""
        const = Const()
        # 緯度: 24-46, 経度: 123-154の範囲内
        for pref_data in const.prefectures:
            _, _, lat, lon = pref_data
            assert 24.0 <= lat <= 46.0, f"Latitude {lat} out of range"
            assert 123.0 <= lon <= 154.0, f"Longitude {lon} out of range"

    def test_num_questions(self):
        """クイズ問題数の設定"""
        const = Const()
        # デフォルト値が10
        assert const.num_questions == 10
