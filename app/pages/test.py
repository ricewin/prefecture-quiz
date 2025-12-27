import random
from typing import List, Tuple

import pandas as pd
import pydeck as pdk
import streamlit as st

NUM_QUESTIONS = 10

# 都道府県・県庁所在地・緯度経度（代表）
PREFECTURES: List[Tuple[str, str, float, float]] = [
    ("北海道", "札幌市", 43.06417, 141.34694),
    ("青森県", "青森市", 40.82444, 140.74),
    ("岩手県", "盛岡市", 39.70361, 141.1525),
    ("宮城県", "仙台市", 38.26889, 140.87194),
    ("秋田県", "秋田市", 39.71861, 140.1025),
    ("山形県", "山形市", 38.24056, 140.36333),
    ("福島県", "福島市", 37.75, 140.46778),
    ("茨城県", "水戸市", 36.365, 140.47144),
    ("栃木県", "宇都宮市", 36.5551, 139.8828),
    ("群馬県", "前橋市", 36.39111, 139.06083),
    ("埼玉県", "さいたま市", 35.86166, 139.6455),
    ("千葉県", "千葉市", 35.60472, 140.12333),
    ("東京都", "新宿区", 35.69384, 139.70361),
    ("神奈川県", "横浜市", 35.4437, 139.638),
    ("新潟県", "新潟市", 37.91667, 139.03639),
    ("富山県", "富山市", 36.69528, 137.21139),
    ("石川県", "金沢市", 36.56111, 136.65622),
    ("福井県", "福井市", 36.06528, 136.22194),
    ("山梨県", "甲府市", 35.66444, 138.56833),
    ("長野県", "長野市", 36.65139, 138.18111),
    ("岐阜県", "岐阜市", 35.42333, 136.76056),
    ("静岡県", "静岡市", 34.97556, 138.38278),
    ("愛知県", "名古屋市", 35.18144, 136.9064),
    ("三重県", "津市", 34.72943, 136.5086),
    ("滋賀県", "大津市", 35.00444, 135.86833),
    ("京都府", "京都市", 35.02139, 135.75556),
    ("大阪府", "大阪市", 34.69374, 135.50218),
    ("兵庫県", "神戸市", 34.69139, 135.18306),
    ("奈良県", "奈良市", 34.68528, 135.80472),
    ("和歌山県", "和歌山市", 34.22583, 135.1675),
    ("鳥取県", "鳥取市", 35.50111, 134.235),
    ("島根県", "松江市", 35.46806, 133.05056),
    ("岡山県", "岡山市", 34.66167, 133.935),
    ("広島県", "広島市", 34.39639, 132.45944),
    ("山口県", "山口市", 34.18583, 131.47139),
    ("徳島県", "徳島市", 34.07028, 134.55444),
    ("香川県", "高松市", 34.34278, 134.04639),
    ("愛媛県", "松山市", 33.83944, 132.76556),
    ("高知県", "高知市", 33.55972, 133.53111),
    ("福岡県", "福岡市", 33.60639, 130.41806),
    ("佐賀県", "佐賀市", 33.24944, 130.29889),
    ("長崎県", "長崎市", 32.75028, 129.87778),
    ("熊本県", "熊本市", 32.80306, 130.70778),
    ("大分県", "大分市", 33.23806, 131.6125),
    ("宮崎県", "宮崎市", 31.91111, 131.42389),
    ("鹿児島県", "鹿児島市", 31.59306, 130.55778),
    ("沖縄県", "那覇市", 26.2125, 127.68111),
]


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
            "capital_to_pref_input": "県庁所在地（市名）を見て都道府県を当てる（入力式）",
            "pref_to_capital_mc": "都道府県名を見て県庁所在地を選ぶ（4択）",
            "map_capital_mc": "地図上に県庁所在地を表示 → 都道府県を選ぶ（4択・pydeck）",
        }

    # ---------- state mutators (callbacks) ----------
    def start_quiz(self):
        """Start or restart quiz: generate questions and MC options and initialize session state."""
        mode = st.session_state.get("selected_mode", "capital_to_pref_input")
        sample = random.sample(PREFECTURES, k=NUM_QUESTIONS)
        st.session_state.quiz = sample
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.answered = [
            None
        ] * NUM_QUESTIONS  # (user_answer, correct_answer, is_correct, pref, cap, lat, lon)
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

    def show_hint(self):
        """Mark current question as shown (incorrect) without changing score."""
        idx = st.session_state.index
        mode = st.session_state.get("mode", "capital_to_pref_input")
        pref, cap, lat, lon = st.session_state.quiz[idx]
        if mode == "capital_to_pref_input":
            st.session_state.answered[idx] = (
                st.session_state.get("answer_input", ""),
                pref,
                False,
                pref,
                cap,
                lat,
                lon,
            )
        elif mode == "pref_to_capital_mc":
            key = f"mc_choice_{idx}"
            st.session_state.answered[idx] = (
                st.session_state.get(key, ""),
                cap,
                False,
                pref,
                cap,
                lat,
                lon,
            )
        else:
            key = f"mc_choice_{idx}"
            st.session_state.answered[idx] = (
                st.session_state.get(key, ""),
                pref,
                False,
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
        st.title("都道府県あてゲーム（クラス分割版、保存機能なし）")
        st.write("モードを選んで「ゲームをスタート」を押してください。")

        # start screen
        if "quiz" not in st.session_state:
            default_mode = st.session_state.get(
                "selected_mode", "capital_to_pref_input"
            )
            st.radio(
                "出題モード",
                options=list(self.modes.keys()),
                format_func=lambda x: self.modes[x],
                key="selected_mode",
                index=list(self.modes.keys()).index(default_mode),
            )
            cols = st.columns([1, 1])
            with cols[0]:
                st.button("ゲームをスタート", on_click=self.start_quiz)
            with cols[1]:
                st.button(
                    "サンプル実行（同じモードで即スタート）", on_click=self.start_quiz
                )
            st.write("---")
            st.info("モードを選択してから「ゲームをスタート」を押してください。")
            return  # stop rendering further

        # in-quiz UI
        quiz = st.session_state.quiz
        idx = st.session_state.index
        score = st.session_state.score
        answered = st.session_state.answered
        show_answer = st.session_state.show_answer
        mode = st.session_state.get("mode", "capital_to_pref_input")

        # finished
        if idx >= NUM_QUESTIONS:
            st.subheader("結果")
            st.write(f"正解数: {st.session_state.score} / {NUM_QUESTIONS}")
            st.write("---")
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
            st.write("---")
            cols = st.columns([1, 1, 1])
            with cols[0]:
                st.button("もう一度（同モードで再開）", on_click=self.start_quiz)
            with cols[1]:
                st.button(
                    "スタート画面に戻る（モード選択）", on_click=self.reset_to_start
                )
            with cols[2]:
                st.button(
                    "セッションを初期化して最初から", on_click=self.reset_to_start
                )
            # show simple per-pref stats for this session
            stats = {}
            for entry in answered:
                if not entry:
                    continue
                _, _, is_correct, pref, cap, lat, lon = entry
                rec = stats.setdefault(
                    pref,
                    {
                        "pref": pref,
                        "cap": cap,
                        "lat": lat,
                        "lon": lon,
                        "attempts": 0,
                        "corrects": 0,
                    },
                )
                rec["attempts"] += 1
                rec["corrects"] += 1 if is_correct else 0
            if stats:
                rows = []
                for v in stats.values():
                    attempts = v["attempts"]
                    corrects = v["corrects"]
                    rate = corrects / attempts if attempts > 0 else None
                    rows.append(
                        {
                            "都道府県": v["pref"],
                            "県庁所在地": v["cap"],
                            "試行回数": attempts,
                            "正解数": corrects,
                            "正答率": round(rate, 3) if rate is not None else None,
                        }
                    )
                df = pd.DataFrame(rows).sort_values("正答率")
                st.subheader("今回セッションの都道府県ごとの正答率")
                st.dataframe(df.reset_index(drop=True))
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

        st.markdown(f"### 問題 {idx + 1} / {NUM_QUESTIONS}")

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
            st.write(
                "地図上に表示された地点（県庁所在地）を見て、正しい都道府県を選んでください。"
            )
            map_data = pd.DataFrame([{"lat": lat, "lon": lon, "name": cap}])
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position=["lon", "lat"],
                get_radius=5000,
                get_fill_color=[255, 0, 0],
                pickable=True,
            )
            view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=7, pitch=0)
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "{name}"},  # type: ignore
            )
            st.pydeck_chart(deck)
            # use mc_map_options generated at start
            options = st.session_state.get("mc_map_options", [])
            if not options:
                options = self._generate_mc_map_options_for_sample(quiz)
                st.session_state.mc_map_options = options
            choice_key = f"mc_choice_{idx}"
            st.radio(
                "都道府県（4択）を選んでください", options=options[idx], key=choice_key
            )

        # 操作ボタン（callbacks are methods so they update session_state safely）
        cols = st.columns([1, 1, 1])
        with cols[0]:
            if not show_answer:
                st.button("回答する", on_click=self.submit_answer)
        with cols[1]:
            if not show_answer:
                st.button("答えを見る（ヒント）", on_click=self.show_hint)
        with cols[2]:
            if show_answer:
                st.button("次へ", on_click=self.next_question)

        # 回答表示
        if show_answer:
            user_ans, correct_ans, is_correct, _pref, _cap, _lat, _lon = (
                st.session_state.answered[idx]
            )
            user_display = user_ans if user_ans else "（未回答）"
            if is_correct:
                st.success(
                    f"正解！ 正解は **{correct_ans}** です。あなた: {user_display}"
                )
            else:
                st.error(
                    f"不正解。正解は **{correct_ans}** です。あなた: {user_display}"
                )
            st.write(f"現在の正解数: **{st.session_state.score} / {idx + 1}**")
        else:
            st.info("入力／選択して「回答する」を押してください。")

        # footer
        st.write("---")
        st.write(f"進捗: {idx} / {NUM_QUESTIONS} (正解: {st.session_state.score})")
        st.button(
            "リセットして最初から（スタート画面へ）", on_click=self.reset_to_start
        )


if __name__ == "__main__":
    app = QuizApp()
    app.run()
