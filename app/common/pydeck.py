import pydeck as pdk
import streamlit as st
from common.utils import get_geojson_center

ss = st.session_state


@st.fragment
def make_map(
    data,
    has_tip: bool = False,
    zoom: int = 4,
    min_zoom: int = 4,
    max_zoom: int = 12,
    area_code: int = 1,
    map_provider: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    get_line_width: int = 100,
):
    if has_tip:
        area = f"<b>{{N03_00{area_code}}}</b>"
    else:
        area = "<b>どこかな？</b>"

    if None in (lat, lon):
        lat, lon = get_geojson_center(data)

    view_state = pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=zoom,
        min_zoom=min_zoom,
        max_zoom=max_zoom,
        pitch=0,
        bearing=0,
    )

    geojson = pdk.Layer(
        "GeoJsonLayer",
        data,
        id="geojson",
        pickable=True,
        opacity=0.1,
        get_fill_color=[178, 255, 255],  # チェレステ
        get_line_color=[136, 141, 144],  # スカイグレー
        get_line_width=get_line_width,
    )

    tooltip = {
        "html": area,
        "style": {
            "background-color": "#515254",  # アスファルト
            "color": "aliceblue",
            "font-family": "Noto Sans JP, sans-serif",
            "border-radius": "50% 20% / 10% 40%",
        },
    }

    r = pdk.Deck(
        map_style="dark_no_labels",
        map_provider=map_provider,  # type: ignore
        layers=[geojson],
        initial_view_state=view_state,
        tooltip=tooltip,  # type: ignore
    )

    choose_map(r)


@st.fragment
def choose_map(r):
    event = st.pydeck_chart(r, height=700, on_select="rerun")

    if obj := event.selection.objects:  # type: ignore
        # with st.expander("*Detailed information on the selected region.*"):
        #     st.caption(obj.geojson[0]["properties"]["N03_001"])
        #     st.caption(obj.geojson[0]["properties"]["N03_007"])
        #     st.write(obj)

        ss.indices = event.selection.indices["geojson"][0]  # type: ignore
        ss.event = obj
