"""Unit tests for app/pages/quiz.py"""

from pages.quiz import normalize_name


class TestNormalizeName:
    """Test cases for normalize_name function"""

    def test_normalize_name_with_suffix(self):
        """都道府県名の正規化（接尾辞あり）"""
        assert normalize_name("大阪府") == "大阪"
        assert normalize_name("東京都") == "東京"
        assert normalize_name("京都府") == "京都"
        assert normalize_name("北海道") == "北海"
        assert normalize_name("千葉県") == "千葉"

    def test_normalize_name_without_suffix(self):
        """都道府県名の正規化（接尾辞なし）"""
        assert normalize_name("東京") == "東京"
        assert normalize_name("大阪") == "大阪"

    def test_normalize_name_with_spaces(self):
        """空白を含む文字列の正規化"""
        assert normalize_name("千葉　県") == "千葉"
        assert normalize_name("千葉 県") == "千葉"
        assert normalize_name("  千葉県  ") == "千葉"

    def test_normalize_name_none(self):
        """None値の処理"""
        assert normalize_name(None) == ""

    def test_normalize_name_empty(self):
        """空文字列の処理"""
        assert normalize_name("") == ""
        assert normalize_name("   ") == ""
