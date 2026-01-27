"""Unit tests for app/common/step_by_step.py"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


class MockSessionState(dict):
    """Mock class that behaves like Streamlit's session state"""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        self[name] = value


@pytest.fixture
def step_by_step_factory(monkeypatch):
    """Factory fixture to create StepByStep instances with a mocked Streamlit environment."""

    def _factory(initial_state=None):
        # Prepare mock session state
        mock_session_state = MockSessionState(initial_state or {})

        # Mock streamlit module
        mock_st = MagicMock()
        mock_st.session_state = mock_session_state
        mock_st.fragment = lambda cls: cls

        # Safely insert mocks into sys.modules; monkeypatch will restore afterwards
        monkeypatch.setitem(sys.modules, "streamlit", mock_st)
        monkeypatch.setitem(
            sys.modules,
            "streamlit.runtime.state.session_state_proxy",
            MagicMock(),
        )

        # Import after mocking
        from common.step_by_step import StepByStep

        return StepByStep()

    return _factory


class TestStepByStep:
    """Test cases for StepByStep class"""

    def test_initialize_state(self, step_by_step_factory):
        """初期状態の設定"""
        # Create StepByStep with an empty mocked session state
        step = step_by_step_factory()

        # now=0, rst=Falseが設定される
        assert step.ss.get("now") == 0
        assert step.ss.get("rst") == False

    def test_countup(self, step_by_step_factory):
        """ステップカウントアップ"""
        # Initialize with now=0, rst=False in mocked session state
        step = step_by_step_factory({"now": 0, "rst": False})
        initial_now = step.ss["now"]

        step.countup(reset=False)

        # nowが1増加する
        assert step.ss["now"] == initial_now + 1
        # rst parameter is correctly stored
        assert step.ss["rst"] == False

    def test_countdown(self, step_by_step_factory):
        """ステップカウントダウン"""
        # Initialize with now=2, rst=False in mocked session state
        step = step_by_step_factory({"now": 2, "rst": False})
        initial_now = step.ss["now"]

        step.countdown()

        # nowが1減少する
        assert step.ss["now"] == initial_now - 1

    def test_reset(self, step_by_step_factory):
        """リセット処理"""
        # Initialize with now=5, rst=True in mocked session state
        step = step_by_step_factory({"now": 5, "rst": True})
        step.reset()

        # now=0に戻る
        assert step.ss["now"] == 0

    def test_change_state(self, step_by_step_factory):
        """状態変更処理"""
        # Initialize with various session state values
        step = step_by_step_factory({
            "now": 1,
            "rst": False,
            "sample": "test_sample",
            "sample_prev": "test_prev",
            "correct_count": 5,
            "wrong_answers": ["answer1", "answer2"],
            "remaining_municipalities": ["city1", "city2"]
        })

        step.change_state()

        # セッション状態がクリアされる
        assert step.ss["sample"] is None
        assert step.ss["sample_prev"] is None
        assert step.ss["correct_count"] == 0
        assert step.ss["wrong_answers"] == []
        assert step.ss["remaining_municipalities"] is None
