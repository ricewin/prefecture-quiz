# Prefecture quiz

都道府県クイズ

---

ANNOUNCEMENT: This app uses open data content[^1].  
お知らせ：このアプリはオープンデータのコンテンツを利用しています。

---

[![CI](https://github.com/ricewin/prefecture-quiz/actions/workflows/ci.yml/badge.svg)](https://github.com/ricewin/prefecture-quiz/actions/workflows/ci.yml)
[![Zenn](https://img.shields.io/badge/Zenn-pfirsich-turquoise?logo=zenn)](https://zenn.dev/pfirsich)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

シンプルで教育用やデモに最適なアプリです。

## CONTENTS

以下のページを用意しています。

1. 地図上に県庁所在地を表示し、都道府県をあてるクイズ
1. 都道府県および市町村の場所を覚えるページ

## Development

### Running Tests

This project uses pytest for testing. To run the tests:

```bash
# Install dependencies with development packages
uv sync

# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=app --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_quiz.py

# Run tests in verbose mode
uv run pytest -v
```

For more details about the test plan, see [TEST_PLAN.md](TEST_PLAN.md).

[^1]:
    出典：[国土交通省国土数値情報ダウンロードサイト](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html)
    [「国土数値情報（行政区域データ）」（国土交通省）](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html)を加工して作成
