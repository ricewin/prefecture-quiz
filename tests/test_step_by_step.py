"""Unit tests for app/common/step_by_step.py"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


class MockSessionState(dict):
    """Mock class that behaves like Streamlit's session state"""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        self[name] = value


class TestStepByStep:
    """Test cases for StepByStep class"""

    def test_initialize_state(self):
        """初期状態の設定"""
        # Mock Streamlit session state
        mock_session_state = MockSessionState()
        
        # Mock streamlit module
        mock_st = MagicMock()
        mock_st.session_state = mock_session_state
        mock_st.fragment = lambda cls: cls
        
        sys.modules['streamlit'] = mock_st
        sys.modules['streamlit.runtime.state.session_state_proxy'] = MagicMock()
        
        # Import after mocking
        from common.step_by_step import StepByStep
        
        step = StepByStep()
        
        # now=0, rst=Falseが設定される
        assert step.ss.get("now") == 0
        assert step.ss.get("rst") == False

    def test_countup(self):
        """ステップカウントアップ"""
        mock_session_state = MockSessionState({"now": 0, "rst": False})
        
        mock_st = MagicMock()
        mock_st.session_state = mock_session_state
        mock_st.fragment = lambda cls: cls
        
        sys.modules['streamlit'] = mock_st
        sys.modules['streamlit.runtime.state.session_state_proxy'] = MagicMock()
        
        from common.step_by_step import StepByStep
        
        step = StepByStep()
        initial_now = step.ss["now"]
        
        step.countup(reset=False)
        
        # nowが1増加する
        assert step.ss["now"] == initial_now + 1
        assert step.ss["rst"] == False

    def test_countdown(self):
        """ステップカウントダウン"""
        mock_session_state = MockSessionState({"now": 2, "rst": False})
        
        mock_st = MagicMock()
        mock_st.session_state = mock_session_state
        mock_st.fragment = lambda cls: cls
        
        sys.modules['streamlit'] = mock_st
        sys.modules['streamlit.runtime.state.session_state_proxy'] = MagicMock()
        
        from common.step_by_step import StepByStep
        
        step = StepByStep()
        initial_now = step.ss["now"]
        
        step.countdown()
        
        # nowが1減少する
        assert step.ss["now"] == initial_now - 1

    def test_reset(self):
        """リセット処理"""
        mock_session_state = MockSessionState({"now": 5, "rst": True})
        
        mock_st = MagicMock()
        mock_st.session_state = mock_session_state
        mock_st.fragment = lambda cls: cls
        
        sys.modules['streamlit'] = mock_st
        sys.modules['streamlit.runtime.state.session_state_proxy'] = MagicMock()
        
        from common.step_by_step import StepByStep
        
        step = StepByStep()
        step.reset()
        
        # now=0に戻る
        assert step.ss["now"] == 0

    def test_change_state(self):
        """状態変更処理"""
        mock_session_state = MockSessionState({
            "now": 1,
            "rst": False,
            "sample": "test_sample",
            "sample_prev": "test_prev",
            "correct_count": 5,
            "wrong_answers": ["answer1", "answer2"],
            "remaining_municipalities": ["city1", "city2"]
        })
        
        mock_st = MagicMock()
        mock_st.session_state = mock_session_state
        mock_st.fragment = lambda cls: cls
        
        sys.modules['streamlit'] = mock_st
        sys.modules['streamlit.runtime.state.session_state_proxy'] = MagicMock()
        
        from common.step_by_step import StepByStep
        
        step = StepByStep()
        step.change_state()
        
        # セッション状態がクリアされる
        assert step.ss["sample"] is None
        assert step.ss["sample_prev"] is None
        assert step.ss["correct_count"] == 0
        assert step.ss["wrong_answers"] == []
        assert step.ss["remaining_municipalities"] is None
