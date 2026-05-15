# ============================================================
# map_engine.py  –  Xử lý Dữ liệu, Chấm điểm & Bản đồ
#
# Luồng:
#   1. Load CSV (quán thật) & normalize dữ liệu
#   2. Score từng quán theo kết quả Fuzzy (40+30+30 – khoảng cách)
#   3. Trả về Top-5 quán phù hợp nhất
#   4. Vẽ Folium map (tất cả quán / chỉ route)
#   5. Tính đường ngắn nhất bằng OSMnx + NetworkX (Dijkstra)
# ============================================================

import folium
import networkx as nx
import pandas as pd
import numpy as np
import os, tempfile
from math import radians, cos, sin, asin, sqrt

try:
    import osmnx as ox
    OSMNX_OK = True
except ImportError:
    OSMNX_OK = False

# Tên file CSV mặc định (hỗ trợ cả 2 cách đặt tên phổ biến)
_CSV_CANDIDATES = [
    "AI_DatasetFood.csv",    # tên file gốc được upload
    "AI.DatasetFood.csv",    # tên cũ trong code Claude trước
    "AI.FOODAPP.csv",        # tên trong untitled3.py
]


# ============================================================
# PHẦN 1 – LOAD & NORMALIZE DỮ LIỆU CSV
# ============================================================

def _normalize_str(s: str) -> str:
    """Strip + chuẩn hoá typo thường gặp trong CSV."""
    if not isinstance(s, str):
        return ""
    s = s.strip()
    alias = {
        "healhy meal":        "Healthy meal",
        "healthy meal":       "Healthy meal",
        "full meal":          "Full meal",
        "fast food":          "Fast food",
        "snack":              "Snack",
        "snack/ fast food":   "Fast food",
        "drinks":             "Drinks",
        "drink":              "Drinks",
        "desserts":           "Dessert",
        "dessert":            "Dessert",
    }
    return alias.get(s.lower(), s)


def _parse_coords(coord_str: str):
    """
    Tách chuỗi tọa độ "lat, lng" → (float, float).
    Dùng index dấu phẩy để tách chính xác không phụ thuộc khoảng trắng.
    """
    try:
        comma_idx = coord_str.index(",")
        lat = float(coord_str[:comma_idx].strip())
        lng = float(coord_str[comma_idx + 1:].strip())
        return lat, lng
    except Exception:
        return None, None


def _price_to_label(price_vnd: float) -> str:
    """Chuyển giá VND thực tế → nhãn Price để so khớp Fuzzy output."""
    if price_vnd <= 80_000:
        return "Cheap"
    if price_vnd <= 400_000:
        return "Moderate"
    return "Expensive"


def _find_csv(csv_path: str) -> str:
    """
    Tìm file CSV theo thứ tự ưu tiên:
    1. Đường dẫn được truyền vào trực tiếp
    2. Các tên file mặc định trong _CSV_CANDIDATES
    Raise FileNotFoundError nếu không tìm thấy.
    """
    if os.path.exists(csv_path):
        return csv_path
    for candidate in _CSV_CANDIDATES:
        if os.path.exists(candidate):
            print(f"[map_engine] Dùng file CSV: {candidate}")
            return candidate
    raise FileNotFoundError(
        f"Không tìm thấy file CSV. "
        f"Hãy đổi tên file thành '{_CSV_CANDIDATES[0]}' và đặt cùng thư mục với app.py"
    )


def load_restaurants(csv_path: str = "Ai_DatasetFood.csv") -> pd.DataFrame:
    """
    Load CSV, normalize các cột và thêm lat/lng/price_label.
    Trả về DataFrame sạch, sẵn sàng để chấm điểm.
    """
    actual_path = _find_csv(csv_path)
    df = pd.read_csv(actual_path)

    # Chuẩn hoá meal_type (sửa typo "Healhy meal" → "Healthy meal")
    df['meal_type']          = df['meal_type'].apply(_normalize_str)
    # Bỏ khoảng trắng thừa ở cuisine
    df['cuisine_suggestion'] = df['cuisine_suggestion'].str.strip()

    # Tách tọa độ từ cột coords dạng "lat, lng"
    coords    = df['coords'].apply(_parse_coords)
    df['lat'] = coords.apply(lambda x: x[0])
    df['lng'] = coords.apply(lambda x: x[1])

    # Thêm nhãn giá để so khớp với Fuzzy output
    df['price_label'] = df['price'].apply(_price_to_label)

    # Loại bỏ hàng thiếu tọa độ hợp lệ
    df = df.dropna(subset=['lat', 'lng']).reset_index(drop=True)
    return df


# ============================================================
# PHẦN 2 – TÍNH KHOẢNG CÁCH & CHẤM ĐIỂM
# ============================================================

def haversine(lat1, lng1, lat2, lng2) -> float:
    """Khoảng cách đường chim bay (km) theo công thức Haversine."""
    R = 6371
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return round(R * 2 * asin(sqrt(a)), 2)


def score_and_rank(df: pd.DataFrame,
                   fuzzy_price: str, fuzzy_meal: str, fuzzy_cuisine: str,
                   user_lat: float, user_lng: float,
                   radius_km: float = 3.0) -> pd.DataFrame:
    """
    Chấm điểm từng quán và trả về Top-5.

    Bảng điểm (theo AI_Logic.docx):
        Khớp Price   → +40 điểm
        Khớp Meal    → +30 điểm
        Khớp Cuisine → +30 điểm
        Khoảng cách  → -10 điểm/km  (đảm bảo luôn có kết quả)
    """
    df = df.copy()

    # Tính khoảng cách từng quán đến vị trí user
    df['dist_km'] = df.apply(
        lambda r: haversine(user_lat, user_lng, r['lat'], r['lng']), axis=1
    )

    # Lọc trong bán kính – nếu trống lấy 20 quán gần nhất (không bao giờ rỗng)
    nearby = df[df['dist_km'] <= radius_km].copy()
    if nearby.empty:
        nearby = df.nsmallest(20, 'dist_km').copy()

    def _score(row):
        s = 0
        if row['price_label']        == fuzzy_price:   s += 40
        if row['meal_type']          == fuzzy_meal:    s += 30
        if row['cuisine_suggestion'] == fuzzy_cuisine: s += 30
        s -= row['dist_km'] * 10   # Phạt khoảng cách
        return round(s, 2)

    nearby['score'] = nearby.apply(_score, axis=1)
    top5 = nearby.nlargest(5, 'score').reset_index(drop=True)
    return top5


# ============================================================
# PHẦN 3 – VẼ BẢN ĐỒ FOLIUM
# ============================================================

ORANGE = "#f97316"    # Màu cam chủ đạo của app


def _user_icon():
    """Icon vị trí người dùng (chấm xanh dương)."""
    return folium.DivIcon(
        html=(
            '<div style="width:16px;height:16px;background:#3b82f6;'
            'border-radius:50%;border:3px solid white;'
            'box-shadow:0 2px 8px rgba(0,0,0,0.4);"></div>'
        ),
        icon_size=(16, 16), icon_anchor=(8, 8),
    )


def _rest_icon(rank: int = 0):
    """Icon quán ăn: quán top-1 màu cam, còn lại xanh lá."""
    color = ORANGE if rank == 0 else "#22c55e"
    return folium.DivIcon(
        html=(
            f'<div style="background:{color};color:white;'
            f'border-radius:50%;width:28px;height:28px;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:14px;box-shadow:0 2px 6px rgba(0,0,0,0.35);">🍽️</div>'
        ),
        icon_size=(28, 28), icon_anchor=(14, 14),
    )


def build_result_map(top5: pd.DataFrame,
                     user_lat: float, user_lng: float,
                     radius_km: float = 3.0) -> folium.Map:
    """
    Bản đồ State 1 – Result:
        - Tâm: vị trí user
        - Hiển thị top-5 quán với icon nhà hàng
        - Click icon → popup: tên quán, món đại diện, giá, calo, khoảng cách
        - Vòng tròn bán kính 3km (hoặc tuỳ chỉnh)
    """
    m = folium.Map(location=[user_lat, user_lng], zoom_start=13,
                   tiles="cartodbpositron")

    # Vòng tròn bán kính (đứt nét)
    folium.Circle(
        location=[user_lat, user_lng],
        radius=radius_km * 1000,
        color=ORANGE, fill=True, fill_opacity=0.05,
        weight=2, dash_array="6 4",
    ).add_to(m)

    # Marker vị trí người dùng
    folium.Marker(
        location=[user_lat, user_lng],
        popup=folium.Popup("📍 Vị trí của bạn", max_width=150),
        tooltip="Bạn đang ở đây",
        icon=_user_icon(),
    ).add_to(m)

    # Marker từng quán trong top-5
    for i, row in top5.iterrows():
        popup_html = (
            f"<div style='font-family:sans-serif;min-width:160px;'>"
            f"<b style='font-size:13px;color:{ORANGE};'>{row['name']}</b><br/>"
            f"<hr style='margin:4px 0;border-color:#eee;'/>"
            f"🍽️ <b>{row['main_dish']}</b><br/>"
            f"📂 {row['meal_type']} · {row['cuisine_suggestion']}<br/>"
            f"💰 {int(row['price']):,}đ &nbsp;|&nbsp; 🔥 {row['calo_estimate(kcal)']} kcal<br/>"
            f"🛵 ~{row['dist_km']} km"
            f"</div>"
        )
        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{'🥇' if i == 0 else f'#{i + 1}'} {row['name']}",
            icon=_rest_icon(rank=i),
        ).add_to(m)

    return m


def build_route_map(user_lat: float, user_lng: float,
                    rest_lat: float, rest_lng: float,
                    rest_name: str) -> tuple:
    """
    Bản đồ State 3 – Delivering:
        - Chỉ hiện user + quán đã đặt (ẩn tất cả quán khác)
        - Vẽ đường ngắn nhất bằng OSMnx + Dijkstra
        - Fallback: đường thẳng Haversine nếu không có mạng

    Returns:
        (folium.Map, dist_km, time_min, method)
        method = "osmnx" | "fallback"
    """
    dist_km  = haversine(user_lat, user_lng, rest_lat, rest_lng)
    time_min = max(5, int((dist_km / 20) * 60))   # Tốc độ TB 20km/h

    clat = (user_lat + rest_lat) / 2
    clng = (user_lng + rest_lng) / 2
    m = folium.Map(location=[clat, clng], zoom_start=15,
                   tiles="cartodbpositron")

    # Marker người dùng & quán đã chọn
    folium.Marker(location=[user_lat, user_lng],
                  tooltip="📍 Bạn", icon=_user_icon()).add_to(m)
    folium.Marker(
        location=[rest_lat, rest_lng],
        tooltip=f"🍽️ {rest_name}",
        icon=folium.DivIcon(
            html=(
                f'<div style="background:{ORANGE};color:white;'
                f'padding:4px 8px;border-radius:8px;font-size:11px;'
                f'font-weight:700;white-space:nowrap;'
                f'box-shadow:0 2px 6px rgba(0,0,0,.3);">🍽️ {rest_name}</div>'
            ),
            icon_size=(160, 28), icon_anchor=(80, 28),
        ),
    ).add_to(m)

    # ── Thử OSMnx + Dijkstra ──────────────────────────────────────
    if OSMNX_OK:
        try:
            buf = 0.015   # Buffer ~ 1.5km mỗi chiều để đảm bảo có đường
            G = ox.graph_from_bbox(
                max(user_lat, rest_lat) + buf,
                min(user_lat, rest_lat) - buf,
                max(user_lng, rest_lng) + buf,
                min(user_lng, rest_lng) - buf,
                network_type="drive", simplify=True,
            )
            orig   = ox.nearest_nodes(G, user_lng, user_lat)
            dest   = ox.nearest_nodes(G, rest_lng, rest_lat)
            route  = nx.shortest_path(G, orig, dest, weight="length")
            coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]

            actual_km  = round(nx.path_weight(G, route, weight="length") / 1000, 2)
            actual_min = max(5, int((actual_km / 20) * 60))

            # Đường đi Dijkstra (màu cam)
            folium.PolyLine(
                locations=coords, color=ORANGE, weight=5, opacity=0.9,
                tooltip=f"🛵 {actual_km} km – ~{actual_min} phút",
            ).add_to(m)

            # Label giữa đường
            mid = coords[len(coords) // 2]
            folium.Marker(
                location=mid,
                icon=folium.DivIcon(
                    html=(
                        f'<div style="background:{ORANGE};color:white;'
                        f'padding:3px 10px;border-radius:14px;'
                        f'font-size:11px;font-weight:700;white-space:nowrap;'
                        f'box-shadow:0 2px 6px rgba(0,0,0,.25);">'
                        f'🛵 {actual_km} km · {actual_min} phút</div>'
                    ),
                    icon_size=(150, 24), icon_anchor=(75, 12),
                ),
            ).add_to(m)

            return m, actual_km, actual_min, "osmnx"

        except Exception as e:
            print(f"[map_engine] OSMnx/Dijkstra lỗi: {e} → dùng fallback")

    # ── Fallback: đường thẳng Haversine ──────────────────────────
    folium.PolyLine(
        locations=[[user_lat, user_lng], [rest_lat, rest_lng]],
        color=ORANGE, weight=4, opacity=0.75, dash_array="10 6",
        tooltip=f"~{dist_km} km (đường chim bay)",
    ).add_to(m)

    return m, dist_km, time_min, "fallback"


# ============================================================
# PHẦN 4 – EXPORT HTML cho Streamlit components
# ============================================================

def map_to_html(m: folium.Map) -> str:
    """
    Xuất folium.Map → chuỗi HTML thuần.
    Fix lỗi WinError 32 trên Windows.
    """
    import tempfile
    import os
    import time

    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".html",
            delete=False,
            mode="w",
            encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name

        m.save(tmp_path)

        with open(tmp_path, "r", encoding="utf-8") as f:
            html = f.read()

        return html

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                time.sleep(0.1)
                os.remove(tmp_path)
            except PermissionError:
                pass