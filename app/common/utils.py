import json

import requests
import streamlit as st
from common.const import Const

CONST = Const()

BASE_URL = CONST.base_url
BASE_DIR = CONST.base_dir
BASE_FILE = CONST.base_file


@st.cache_data(show_spinner="fetch data...")
def fetch_data(region: str, extension: str = ".json"):
    path = f"{BASE_URL}{BASE_FILE}{region}{extension}"

    response = requests.get(path)
    response.raise_for_status()
    return response.json()


@st.cache_data()
def load_data(region: str, extension: str = ".json"):
    path = f"{BASE_DIR}{region}{extension}"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


@st.cache_data
def get_geojson_center(geojson):
    def extract_coords(geometry):
        coords = []
        if geometry["type"] == "Polygon":
            coords.extend(geometry["coordinates"][0])
        elif geometry["type"] == "MultiPolygon":
            for polygon in geometry["coordinates"]:
                coords.extend(polygon[0])
        return coords

    all_coords = []
    for feature in geojson["features"]:
        geometry = feature.get("geometry")
        # geometry が None の場合はスキップ
        if geometry is None:
            continue

        coords = extract_coords(geometry)
        all_coords.extend(coords)

    if not all_coords:
        raise ValueError("GeoJSON に有効な座標が含まれていません")

    lon = [pt[0] for pt in all_coords]
    lat = [pt[1] for pt in all_coords]

    center_lon = (min(lon) + max(lon)) / 2
    center_lat = (min(lat) + max(lat)) / 2

    return center_lat, center_lon


@st.cache_data
def get_geojson_bbox(geojson):
    def extract_coords(geometry):
        coords = []
        if geometry["type"] == "Polygon":
            coords.extend(geometry["coordinates"][0])
        elif geometry["type"] == "MultiPolygon":
            for polygon in geometry["coordinates"]:
                coords.extend(polygon[0])
        return coords

    all_coords = []
    for feature in geojson["features"]:
        coords = extract_coords(feature["geometry"])
        all_coords.extend(coords)

    lon = [pt[0] for pt in all_coords]
    lat = [pt[1] for pt in all_coords]

    return [min(lon), min(lat), max(lon), max(lat)]
