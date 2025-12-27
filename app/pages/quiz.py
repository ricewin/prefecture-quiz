import random

import pandas as pd
import pydeck as pdk
import streamlit as st
from common.const import Const

CONST = Const()

NUM_QUESTIONS = CONST.num_questions
PREFECTURES = CONST.prefectures


def normalize_name(name: str) -> str:
    if name is None:
        return ""

    s = name.strip().replace("　", "").replace(" ", "").lower()
    for suf in ("県", "都", "府", "道"):
        if s.endswith(suf):
            s = s[: -len(suf)]
            break

    return s


class QuizApp:
    def __init__(self):
        # mode keys: "capital_to_pref_input", "pref_to_capital_mc", "map_capital_mc"
        self.modes = {
            # "pref_to_capital_mc": "都道府県名を見て地図から場所を当てよう",
            # "capital_to_pref_input": "市町村名を見て地図から場所を当てよう",
            "map_capital_mc": "地図上に県庁所在地を表示するので都道府県を当てよう",
        }

    # ---------- state mutators (callbacks) ----------
    def start_quiz(self):
        """Start or restart quiz: generate questions and MC options and initialize session state."""
        mode = st.session_state.get("selected_mode")
        sample = random.sample(PREFECTURES, k=NUM_QUESTIONS)
        st.session_state.quiz = sample
        st.session_state.index = 0
        st.session_state.score = 0

        # (user_answer, correct_answer, is_correct, pref, cap, lat, lon)
        st.session_state.answered = [None] * NUM_QUESTIONS
        st.session_state.show_answer = False
        st.session_state.mode = mode

        # widget initial value (safe to set here before widget instantiation)
        st.session_state.answer_input = ""

        # generate MC options once per session
        if mode in ("pref_to_capital_mc", "map_capital_mc"):
            st.session_state.mc_options = self._generate_mc_options_for_sample(sample)

        # map-specific pref options
        if mode == "map_capital_mc":
            st.session_state.mc_map_options = self._generate_mc_map_options_for_sample(
                sample
            )

    def submit_answer(self):
        """Handle answer submission for current question."""
        idx = st.session_state.index
        mode = st.session_state.get("mode", "capital_to_pref_input")
        pref, cap, lat, lon = st.session_state.quiz[idx]

        if mode == "capital_to_pref_input":
            user_input = st.session_state.get("answer_input", "")
            is_correct = (
                normalize_name(user_input) == normalize_name(pref)
                and normalize_name(user_input) != ""
            )

            if is_correct:
                st.session_state.score += 1

            st.session_state.answered[idx] = (
                user_input,
                pref,
                is_correct,
                pref,
                cap,
                lat,
                lon,
            )

        elif mode == "pref_to_capital_mc":
            key = f"mc_choice_{idx}"
            user_choice = st.session_state.get(key, "")
            is_correct = user_choice == cap

            if is_correct:
                st.session_state.score += 1

            st.session_state.answered[idx] = (
                user_choice,
                cap,
                is_correct,
                pref,
                cap,
                lat,
                lon,
            )

        else:  # map_capital_mc
            key = f"mc_choice_{idx}"
            user_choice = st.session_state.get(key, "")
            is_correct = user_choice == pref

            if is_correct:
                st.session_state.score += 1

            st.session_state.answered[idx] = (
                user_choice,
                pref,
                is_correct,
                pref,
                cap,
                lat,
                lon,
            )

        st.session_state.show_answer = True

    def next_question(self):
        """Advance to next question (callback-safe)."""
        prev_idx = st.session_state.index
        st.session_state.index = prev_idx + 1
        st.session_state.show_answer = False

        # clear previous per-question widget values (safe inside callback)
        mc_key = f"mc_choice_{prev_idx}"

        if mc_key in st.session_state:
            st.session_state[mc_key] = None

        st.session_state.answer_input = ""

    def reset_to_start(self):
        """Return to start screen (remove quiz-related keys)."""
        for k in [
            "quiz",
            "index",
            "score",
            "answered",
            "show_answer",
            "mode",
            "mc_options",
            "mc_map_options",
            "answer_input",
        ]:
            if k in st.session_state:
                del st.session_state[k]

    # ---------- helpers ----------
    def _generate_mc_options_for_sample(self, sample):
        capitals = [cap for (_pref, cap, _la, _lo) in PREFECTURES]
        mc_options = []

        for pref, cap, _la, _lo in sample:
            wrongs = random.sample([c for c in capitals if c != cap], k=3)
            opts = wrongs + [cap]
            random.shuffle(opts)
            mc_options.append(opts)

        return mc_options

    def _generate_mc_map_options_for_sample(self, sample):
        prefs = [p for (p, c, la, lo) in PREFECTURES]
        mc_opts = []

        for pref, cap, la, lo in sample:
            wrongs = random.sample([p for p in prefs if p != pref], k=3)
            opts = wrongs + [pref]
            random.shuffle(opts)
            mc_opts.append(opts)

        return mc_opts

    # ---------- UI rendering ----------
    def run(self):
        st.title(":material/crossword: 都道府県クイズ")

        # start screen
        if "quiz" not in st.session_state:
            st.subheader("モードを選んでゲームスタート！", divider="rainbow")

            default_mode = st.session_state.get("selected_mode", "map_capital_mc")
            st.radio(
                "出題モード",
                options=list(self.modes.keys()),
                format_func=lambda x: self.modes[x],
                key="selected_mode",
                index=list(self.modes.keys()).index(default_mode),
            )

            with st.container(horizontal=True):
                st.button("ゲームスタート", type="primary", on_click=self.start_quiz)

            st.write("---")
            st.write("モードを選択してからゲームスタートしてね")

            return  # stop rendering further

        # in-quiz UI
        quiz = st.session_state.quiz
        idx = st.session_state.index

        # score = st.session_state.score
        answered = st.session_state.answered
        show_answer = st.session_state.show_answer
        mode = st.session_state.get("mode", "capital_to_pref_input")

        # finished
        if idx >= NUM_QUESTIONS:
            st.subheader(
                f"結果: **正解は、{st.session_state.score} 問**でした！",
                divider="rainbow",
            )
            st.divider()
            st.write("詳しい結果：")

            for i, entry in enumerate(answered, start=1):
                if entry is None:
                    st.write(f"{i}. （未回答）")
                    continue

                user_ans, correct_ans, is_correct, pref, cap, lat, lon = entry
                user_display = user_ans or "（未回答）"
                qlabel = (
                    f"県庁所在地: {cap}"
                    if mode == "capital_to_pref_input"
                    else f"都道府県: {pref}"
                )
                result = "✅ 正解" if is_correct else "✖️ 不正解"
                st.write(
                    f"{i}. {qlabel} → 正解: {correct_ans} / あなた: {user_display} → {result}"
                )
            st.caption(f"正答率: *{(st.session_state.score / NUM_QUESTIONS):.0%}*")
            st.divider()

            with st.container(horizontal=True):
                st.button("スタート画面に戻る", on_click=self.reset_to_start)

            return

        # current question (safe unpack: quiz elements are (pref,cap,lat,lon) generated at start_quiz)
        item = quiz[idx]

        # conservative unpack fallback
        if isinstance(item, (list, tuple)) and len(item) >= 4:
            pref, cap, lat, lon = item[0], item[1], item[2], item[3]

        else:
            # fallback: try to find lat/lon from PREFECTURES list
            pref, cap = item[0], item[1]  # type: ignore
            found = next(
                (
                    (p, c, la, lo)
                    for (p, c, la, lo) in PREFECTURES
                    if p == pref or c == cap
                ),
                None,
            )

            if found:
                pref, cap, lat, lon = found

            else:
                pref, cap, lat, lon = pref, cap, 36.0, 138.0

        st.subheader(
            f"問題: {idx + 1} / {NUM_QUESTIONS}",
            divider="rainbow",
            text_alignment="right",
        )

        if mode == "capital_to_pref_input":
            st.write(f"県庁所在地: **{cap}**")
            st.text_input(
                "都道府県名を入力してください（例：大阪府 または 大阪）",
                key="answer_input",
                placeholder="例：千葉県、東京、沖縄",
            )

        elif mode == "pref_to_capital_mc":
            st.write(f"都道府県: **{pref}**")
            options = st.session_state.get("mc_options", [])

            # options[idx] should exist because start_quiz generated mc_options
            if not options:
                # fallback generation (shouldn't normally happen)
                options = self._generate_mc_options_for_sample(quiz)
                st.session_state.mc_options = options

            choice_key = f"mc_choice_{idx}"
            st.radio(
                "県庁所在地（4択）を選んでください",
                options=options[idx],
                key=choice_key,
            )

        else:  # map_capital_mc
            st.subheader("どーこだ？", divider="violet")
            st.caption("ポイントにカーソルを当てるとヒントが出るよ")
            map_data = pd.DataFrame([{"lat": lat, "lon": lon, "name": cap}])

            view_state = pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=12,
                min_zoom=12,
                max_zoom=12,
                pitch=0,
                interactive=False,
            )

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position=["lon", "lat"],
                get_radius=500,
                get_fill_color=[255, 0, 0],
                pickable=True,
            )

            tooltip = {
                "html": "<b>{name}</b>",
                "style": {
                    "background-color": "teal",
                    "color": "aliceblue",
                    "font-family": "Noto Sans JP, sans-serif",
                    "border-radius": "50% 20% / 10% 40%",
                },
            }

            deck = pdk.Deck(
                map_style="dark_no_labels",
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip,  # type: ignore
            )

            st.pydeck_chart(deck)

            # use mc_map_options generated at start
            options = st.session_state.get("mc_map_options", [])

            if not options:
                options = self._generate_mc_map_options_for_sample(quiz)
                st.session_state.mc_map_options = options

            choice_key = f"mc_choice_{idx}"
            st.radio(
                "都道府県を選んでね",
                options=options[idx],
                key=choice_key,
                horizontal=True,
            )

        # 操作ボタン（callbacks are methods so they update session_state safely）
        with st.container(horizontal=True):
            if not show_answer:
                st.button("回答する", type="primary", on_click=self.submit_answer)

            if show_answer:
                st.button("次へ", type="primary", on_click=self.next_question)

        # 回答表示
        with st.status("進捗", expanded=True) as status:
            if show_answer:
                user_ans, correct_ans, is_correct, _pref, _cap, _lat, _lon = (
                    st.session_state.answered[idx]
                )
                user_display = user_ans if user_ans else "（未回答）"

                if is_correct:
                    st.success(f"正解！ 正解は **{correct_ans}** です。")

                else:
                    st.info(f"不正解。正解は **{correct_ans}** です。")

                status.update(
                    label=f"現在の正解数: **{st.session_state.score} / {idx + 1}**",
                    state="complete",
                )

            else:
                status.update(
                    label="入力／選択して「回答する」を押してください。",
                    state="error",
                )
                st.info("地形から当ててみよう！")

            st.toast(f"進捗: {idx} / {NUM_QUESTIONS} (正解: {st.session_state.score})")

        with st.sidebar:
            st.button("リセットして最初から", on_click=self.reset_to_start)


if __name__ == "__main__":
    app = QuizApp()
    app.run()
