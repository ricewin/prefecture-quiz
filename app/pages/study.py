import random

import streamlit as st
from common.pydeck import make_map
from common.step_by_step import StepByStep
from common.utils import load_data

ss = st.session_state
step = StepByStep()

if "event" not in ss:
    ss.event = None

if "sample" not in ss:
    ss.sample = None
    ss.sample_prev = None

if "correct_count" not in ss:
    ss.correct_count = 0

if "wrong_answers" not in ss:
    ss.wrong_answers = []


def change_step():
    ss.sample = None
    ss.sample_prev = None
    ss.correct_count = 0
    ss.wrong_answers = []
    ss.remaining_municipalities = None


def question(data, area_code, has_tip):
    def answer_question():
        ss.sample_prev = ss.sample

        if ss.remaining_municipalities:
            ss.sample = ss.remaining_municipalities.pop()
        else:
            if ss.correct_count == len(municipalities) - 1:
                st.toast("全問正解だよ！すごい！")

    def change_question():
        ss.sample_prev = ss.sample
        ss.sample = random.choice(ss.remaining_municipalities)

    def reset_question():
        ss.remaining_municipalities = None
        ss.correct_count = 0
        ss.wrong_answers = []
        st.toast("問題をリセットしたよ")

    municipalities = [
        feature["properties"][f"N03_00{area_code}"]
        for feature in data["features"]
        if feature["properties"].get(f"N03_00{area_code}") is not None
    ]

    if "remaining_municipalities" not in ss or ss.remaining_municipalities is None:
        ss.remaining_municipalities = municipalities.copy()
        random.shuffle(ss.remaining_municipalities)
        ss.sample = ss.remaining_municipalities.pop()
        ss.sample_prev = ss.sample

    sample = ss.sample
    correct = ss.sample_prev

    if not has_tip:
        with st.sidebar:
            if ss.remaining_municipalities or sample != correct:
                st.write(f"**{sample}** はどこかな？")
                st.caption("地図から選択して答えてね")

            on_tip = st.segmented_control(
                ":material/visibility: ヒント",
                ["みる", "みない"],
                default="みない",
                help="見ているときは答えられないよ",
            )
            has_tip = on_tip == "みる"

            with st.container(horizontal=True):
                disable_answer = has_tip
                disable_change = False

                if not ss.remaining_municipalities and sample == correct:
                    disable_answer = True
                    disable_change = True

                if st.button(
                    "答える",
                    type="primary",
                    disabled=disable_answer,
                    on_click=answer_question,
                ):
                    if obj := ss.event:
                        answer = obj.geojson[0]["properties"][f"N03_00{area_code}"]

                        if correct == answer:
                            st.toast("正解だよ！")
                            ss.correct_count += 1
                        else:
                            st.toast("おしい！")
                            if correct not in ss.wrong_answers:
                                ss.wrong_answers.append(correct)

                        st.toast(f"{answer}を選択したよ")
                    else:
                        st.toast("地図から選んでね")

                st.button(
                    "チェンジ",
                    disabled=disable_change,
                    on_click=change_question,
                )

                st.button(
                    "リセット",
                    type="tertiary",
                    on_click=reset_question,
                )

            with st.container(border=True):
                st.write(
                    ":material/stacks:",
                    len(municipalities) - len(ss.remaining_municipalities),
                    "/",
                    len(municipalities),
                )
                st.write(":material/kid_star:", ss.correct_count)
                st.write(":material/moon_stars:", len(ss.wrong_answers))

            if ss.wrong_answers:
                with st.popover("間違いを見る"):
                    for item in ss.wrong_answers:
                        st.write(f"- {item}")

    return has_tip


def step1(has_tip):
    data = load_data("prefecture")

    area_code = 1
    has_tip = question(data, area_code, has_tip)

    make_map(
        data,
        has_tip=has_tip,
        max_zoom=8,
    )


def step2(has_tip):
    if obj := ss.event:
        pref = obj.geojson[0]["properties"]["N03_001"]
        code = obj.geojson[0]["properties"]["N03_007"][:2]
        st.write(f"{pref}を選んだよ")
    else:
        st.info("都道府県から選択してね")
        return

    with st.sidebar:
        is_subprefecture = False
        zoom = 8
        min_zoom = 6
        if pref == "北海道":
            zoom = 6
            sub = st.segmented_control(
                ":material/orbit: どっち",
                options=["振興局", "市町村"],
                default="市町村",
                on_change=change_step,
                help="北海道だけ特別だよ",
            )
            is_subprefecture = sub == "振興局"
        elif pref == "東京都":
            zoom = 9
            min_zoom = 4

        area_code = 4
        if is_subprefecture:
            area_code = 2
            code += "_subprefecture"

    data = load_data(f"{code}")

    has_tip = question(data, area_code, has_tip)

    lat, lon = None, None
    if pref == "北海道":
        # 北海道は北方四島も含めると右に寄りすぎるので固定
        lat, lon = 43.5, 142.0
    elif pref == "東京都":
        # 東京都は島しょを含めた中心位置で描画すると海しか見えないので固定
        lat, lon = 35.7, 139.4
    elif pref == "沖縄県":
        # 沖縄県も離島を含めた中心位置で描画すると遠くなるので固定
        lat, lon = 26.5, 127.75

    make_map(
        data,
        has_tip=has_tip,
        zoom=zoom,
        min_zoom=min_zoom,
        area_code=area_code,
        map_provider="carto",
        lat=lat,
        lon=lon,
    )


def main():
    st.title(":material/lightbulb: 場所と地名を覚えよう")

    with st.sidebar:
        choice = st.segmented_control(
            ":material/question_mark: クイズ",
            ["する", "しない"],
            default="する",
            help="場所をあてよう",
        )
        has_tip = choice == "しない"

    try:
        if ss.now == 0:
            st.subheader("都道府県", divider="rainbow")
            step1(has_tip)

            st.caption("都道府県を選んでから次へ進むと市町村もできるよ")

        elif ss.now == 1:
            st.subheader("市町村", divider="rainbow")
            step2(has_tip)

        else:
            pass

    finally:
        step.buttons(ss.now)

        st.divider()
        st.caption(
            """
            [「国土数値情報（行政区域データ）」（国土交通省）](
            https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html)を加工して作成

            出典：[国土交通省国土数値情報ダウンロードサイト](
            https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html)
            """,
            text_alignment="right",
        )


main()
