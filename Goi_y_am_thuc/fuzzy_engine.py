# ============================================================
# fuzzy_engine.py  –  Hệ Điều Khiển Mờ Tập Trung (Single FIS)
#
# Kiến trúc: 1 ControlSystem duy nhất xử lý toàn bộ
# (theo mô hình untitled3.py - Decoupled nhưng cùng 1 system)
#
# 5 Đầu vào → 4 Đầu ra:
#   Budget (VND)    → Price Range  (Cheap / Moderate / Expensive)
#   Health (0-10)   → Calories     (Low / Medium / High)
#   Hunger (0-10)   ↗ Meal Type    (Snack/Drinks/Dessert/Fast food/Healthy meal/Full meal)
#   Time (phút)     ↗
#   Weather (0-10)  → Cuisine      (Vietnamese/Thai/Chinese/Western/Japanese/Korean)
# ============================================================

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ============================================================
# PHẦN 1 – CÁC BIẾN ĐẦU VÀO (Antecedents)
# Thông số trimf lấy đúng theo AI_Tapmo.docx
# ============================================================

# --- Ngân sách (Budget): 0 → 10.000.000 VNĐ ---
# Chia 1.001 điểm (bước 10.000) để đủ độ phân giải mà không quá nặng
budget_u = np.arange(0, 10_000_001, 10_000)
budget = ctrl.Antecedent(budget_u, 'Budget')
budget['Cheap']    = fuzz.trimf(budget_u, [0,         40_000,    100_000])
budget['Moderate'] = fuzz.trimf(budget_u, [60_000,   150_000,    500_000])
budget['High']     = fuzz.trimf(budget_u, [500_000,  1_000_000,  3_000_000])
budget['VeryHigh'] = fuzz.trimf(budget_u, [3_000_000, 5_000_000, 10_000_000])

# --- Mức độ đói (Hunger): 0 → 10 ---
hunger_u = np.arange(0, 10.05, 0.05)
hunger = ctrl.Antecedent(hunger_u, 'Hunger')
hunger['Light']       = fuzz.trimf(hunger_u, [0,  0,  4])   # Đỉnh: 0
hunger['Hungry']      = fuzz.trimf(hunger_u, [2,  5,  8])   # Đỉnh: 5
hunger['VeryHungry']  = fuzz.trimf(hunger_u, [6,  8, 10])   # Đỉnh: 8
hunger['Starving']    = fuzz.trimf(hunger_u, [8, 10, 10])   # Đỉnh: 10

# --- Thời gian chờ (Time): 0 → 120 phút ---
# App dùng slider 15–60 phút nhưng universe rộng hơn để trimf đúng hình
time_u = np.arange(0, 121, 1)
time = ctrl.Antecedent(time_u, 'Time')
time['VeryShort'] = fuzz.trimf(time_u, [10, 15, 25])   # Dưới 25 phút
time['Short']     = fuzz.trimf(time_u, [15, 30, 45])   # ~30 phút
time['Medium']    = fuzz.trimf(time_u, [30, 50, 70])   # ~50 phút
time['Long']      = fuzz.trimf(time_u, [50, 70, 90])   # ≥60 phút

# --- Thời tiết (Weather): 0 (Rainy/Lạnh) → 10 (Nóng) ---
# Quy đổi từ nhiệt độ thực (Open-Meteo) dùng temp_to_weather_score():
#   Đang mưa → 0.0  | < 20°C → 2.0  | 20-30°C → 6.6  | >30°C → 9.0
weather_u = np.arange(0, 10.05, 0.05)
weather = ctrl.Antecedent(weather_u, 'Weather')
weather['Rainy']  = fuzz.trimf(weather_u, [0,   0,   3.3])  # Mưa: đỉnh 0
weather['Cold']   = fuzz.trimf(weather_u, [0,   3.3, 6.6])  # Lạnh: đỉnh 3.3
weather['Normal'] = fuzz.trimf(weather_u, [3.3, 6.6, 10])   # Thường: đỉnh 6.6
weather['Hot']    = fuzz.trimf(weather_u, [6.6, 10,  10])   # Nóng: đỉnh 10

# --- Mục tiêu sức khỏe (Health): 0 → 10 ---
health_u = np.arange(0, 10.05, 0.05)
health = ctrl.Antecedent(health_u, 'Health')
health['Diet']     = fuzz.trimf(health_u, [0,  0,  5])   # Ăn kiêng: đỉnh 0
health['Balanced'] = fuzz.trimf(health_u, [0,  5, 10])   # Cân bằng: đỉnh 5
health['Bulking']  = fuzz.trimf(health_u, [5, 10, 10])   # Tăng cơ: đỉnh 10


# ============================================================
# PHẦN 2 – CÁC BIẾN ĐẦU RA (Consequents)
# ============================================================

# --- Loại bữa ăn (MealType): trục 0–60, mỗi danh mục 10 đơn vị ---
meal_u = np.arange(0, 61, 1)
meal_out = ctrl.Consequent(meal_u, 'MealType', defuzzify_method='centroid')
meal_out['Snack']         = fuzz.trimf(meal_u, [0,   5,  10])
meal_out['Drinks']        = fuzz.trimf(meal_u, [10, 15,  20])
meal_out['Dessert']       = fuzz.trimf(meal_u, [20, 25,  30])
meal_out['Fast food']     = fuzz.trimf(meal_u, [30, 35,  40])
meal_out['Healthy meal']  = fuzz.trimf(meal_u, [40, 45,  50])
meal_out['Full meal']     = fuzz.trimf(meal_u, [50, 55,  60])

# --- Gợi ý ẩm thực (Cuisine): trục 0–60 ---
cuisine_u = np.arange(0, 61, 1)
cuisine_out = ctrl.Consequent(cuisine_u, 'Cuisine', defuzzify_method='centroid')
cuisine_out['Vietnamese'] = fuzz.trimf(cuisine_u, [0,   5,  10])
cuisine_out['Thai']       = fuzz.trimf(cuisine_u, [10, 15,  20])
cuisine_out['Chinese']    = fuzz.trimf(cuisine_u, [20, 25,  30])
cuisine_out['Western']    = fuzz.trimf(cuisine_u, [30, 35,  40])
cuisine_out['Japanese']   = fuzz.trimf(cuisine_u, [40, 45,  50])
cuisine_out['Korean']     = fuzz.trimf(cuisine_u, [50, 55,  60])

# --- Khoảng giá (Price): trục VNĐ 0–5.000.000 ---
price_u = np.arange(0, 5_000_001, 5_000)
price_out = ctrl.Consequent(price_u, 'Price', defuzzify_method='centroid')
price_out['Cheap']     = fuzz.trimf(price_u, [0,        45_000,    80_000])
price_out['Moderate']  = fuzz.trimf(price_u, [50_000,  150_000,   450_000])
price_out['Expensive'] = fuzz.trimf(price_u, [300_000, 5_000_000, 5_000_000])

# --- Năng lượng ước tính (Calories): trục 0–10 ---
calo_u = np.arange(0, 10.05, 0.05)
calo_out = ctrl.Consequent(calo_u, 'Calories', defuzzify_method='centroid')
calo_out['Low']    = fuzz.trimf(calo_u, [0,  0,  5])
calo_out['Medium'] = fuzz.trimf(calo_u, [0,  5, 10])
calo_out['High']   = fuzz.trimf(calo_u, [5, 10, 10])


# ============================================================
# PHẦN 3 – BỘ LUẬT MỜ (Fuzzy Rules)
# Kiến trúc: Single ControlSystem (theo untitled3.py)
# 4 nhóm luật độc lập chạy trong 1 hệ thống
# ============================================================

rules = [
    # ── NHÓM 1: Tài chính ─────────────────────────────────
    # Budget → Price Range
    ctrl.Rule(budget['Cheap'],                              price_out['Cheap']),
    ctrl.Rule(budget['Moderate'] | budget['High'],                           price_out['Moderate']),
    ctrl.Rule(budget['VeryHigh'],          price_out['Expensive']),

    # ── NHÓM 2: Dinh dưỡng ────────────────────────────────
    # Health + Hunger → Calories
    ctrl.Rule(health['Diet'],                               calo_out['Low']),
    ctrl.Rule(health['Balanced'],                           calo_out['Medium']),
    ctrl.Rule(health['Bulking'] | hunger['Starving'],       calo_out['High']),

    # ── NHÓM 3: Lịch trình ────────────────────────────────
    # Time + Hunger (+ Health) → Meal Type
    # Trường hợp: Hơi đói (Light)
    ctrl.Rule(hunger['Light'] & time['VeryShort'],          meal_out['Drinks']),
    ctrl.Rule(hunger['Light'] & time['Short'],              meal_out['Dessert']),
    ctrl.Rule(hunger['Light'] & time['Medium'],             meal_out['Snack']),
    ctrl.Rule(hunger['Light'] & time['Long'],               meal_out['Dessert']),
    # Trường hợp: Đói bình thường (Hungry)
    ctrl.Rule(hunger['Hungry'] & time['VeryShort'],         meal_out['Fast food']),
    ctrl.Rule(hunger['Hungry'] & time['Short'],             meal_out['Fast food']),
    ctrl.Rule(health['Diet'] & hunger['Hungry'],            meal_out['Healthy meal']),
    # Trường hợp: Rất đói (VeryHungry)
    ctrl.Rule(hunger['VeryHungry'] & time['VeryShort'],     meal_out['Fast food']),
    ctrl.Rule(hunger['VeryHungry'] & time['Short'],         meal_out['Fast food']),
    # Trường hợp: Đói cồn cào (Starving)
    ctrl.Rule(hunger['Starving'] & time['VeryShort'],       meal_out['Fast food']),
    ctrl.Rule(hunger['Starving'] & time['Short'],           meal_out['Fast food']),
    # Khi có đủ thời gian → Bữa chính (áp dụng mọi mức đói)
    ctrl.Rule(time['Medium'] | time['Long'],                meal_out['Full meal']),

    # ── NHÓM 4: Môi trường ────────────────────────────────
    # Weather → Cuisine (theo AI_Logic.docx)
    ctrl.Rule(weather['Rainy'],   cuisine_out['Vietnamese']),  # Mưa → Việt ấm cúng
    ctrl.Rule(weather['Cold'],    cuisine_out['Korean']),      # Lạnh → Hàn Quốc nóng hổi
    ctrl.Rule(weather['Normal'],  cuisine_out['Western']),     # Thường → Âu/Mỹ đa dạng
    ctrl.Rule(weather['Hot'],     cuisine_out['Thai']),        # Nóng → Thái thanh mát
]

# ============================================================
# PHẦN 4 – KHỞI TẠO HỆ ĐIỀU KHIỂN DUY NHẤT
# (Theo kiến trúc untitled3.py: 1 system, 1 simulation)
# ============================================================

food_ctrl = ctrl.ControlSystem(rules)    # Hệ điều khiển tổng hợp
food_sim  = ctrl.ControlSystemSimulation(food_ctrl)  # Bộ mô phỏng dùng chung


# ============================================================
# PHẦN 5 – HÀM CHUYỂN ĐỔI & PHÂN LOẠI NHÃN
# ============================================================

def temp_to_weather_score(temp_c: float, is_raining: bool) -> float:
    """
    Chuyển nhiệt độ thực (°C) + trạng thái mưa → thang điểm 0–10
    để đưa vào tập mờ Weather.
        Đang mưa  → 0.0  (Rainy – đỉnh 0)
        < 20°C    → 2.0  (Cold  – đỉnh 3.3)
        20–30°C   → 6.6  (Normal– đỉnh 6.6)
        > 30°C    → 9.0  (Hot   – đỉnh 10)
    """
    if is_raining:
        return 0.0
    if temp_c < 20:
        return 2.0
    if temp_c <= 30:
        return 6.6
    return 9.0


def _label_meal(val: float) -> str:
    """Dịch điểm giải mờ (0–60) → nhãn Meal Type."""
    if val <= 8:   return "Snack"
    if val <= 18:  return "Drinks"
    if val <= 28:  return "Dessert"
    if val <= 38:  return "Fast food"
    if val <= 48:  return "Healthy meal"
    return "Full meal"


def _label_cuisine(val: float) -> str:
    """Dịch điểm giải mờ (0–60) → nhãn Cuisine."""
    if val <= 8:   return "Vietnamese"
    if val <= 18:  return "Thai"
    if val <= 28:  return "Chinese"
    if val <= 38:  return "Western"
    if val <= 48:  return "Japanese"
    return "Korean"


def _label_price(val_vnd: float) -> str:
    """Dịch giá trị giải mờ (VNĐ) → nhãn Price Range."""
    if val_vnd <= 90_000:   return "Cheap"
    if val_vnd <= 400_000:  return "Moderate"
    return "Expensive"


def _label_calo(val: float) -> str:
    """Dịch điểm giải mờ (0–10) → nhãn Calories."""
    if val <= 3.5: return "Low"
    if val <= 6.5: return "Medium"
    return "High"


# ── Bản dịch tiếng Việt cho UI ─────────────────────────────
MEAL_VI = {
    "Snack":         "🍡 Ăn vặt",
    "Drinks":        "🧋 Đồ uống",
    "Dessert":       "🍨 Tráng miệng",
    "Fast food":     "🍔 Đồ ăn nhanh",
    "Healthy meal":  "🥗 Lành mạnh",
    "Full meal":     "🍽️ Bữa chính",
}
CUISINE_VI = {
    "Vietnamese":  "🇻🇳 Việt Nam",
    "Thai":        "🇹🇭 Thái Lan",
    "Chinese":     "🇨🇳 Trung Hoa",
    "Western":     "🌍 Âu / Mỹ",
    "Japanese":    "🇯🇵 Nhật Bản",
    "Korean":      "🇰🇷 Hàn Quốc",
}
PRICE_VI = {
    "Cheap":     "💚 Rẻ",
    "Moderate":  "🟡 Vừa",
    "Expensive": "🔴 Mắc",
}
CALO_VI = {
    "Low":    "🔵 Thấp  (<300 kcal)",
    "Medium": "🟡 Vừa  (300–700 kcal)",
    "High":   "🔴 Cao   (>700 kcal)",
}


# ============================================================
# PHẦN 6 – HÀM CHÍNH: Chạy toàn bộ hệ mờ
# ============================================================

def run_fuzzy(budget_vnd: float, hunger_val: float, time_val: float,
              health_val: float, weather_score: float) -> dict:
    """
    Chạy hệ điều khiển mờ duy nhất (single FIS) và trả về kết quả.

    Args:
        budget_vnd    : Ngân sách (VNĐ, 0 – 10.000.000)
        hunger_val    : Mức độ đói (0 – 10)
        time_val      : Thời gian chờ (phút, 15 – 60)
        health_val    : Mục tiêu sức khỏe (0 – 10)
        weather_score : Điểm thời tiết (0 – 10, từ temp_to_weather_score)

    Returns:
        dict: nhãn đầu ra, giá trị thô, nhãn tiếng Việt, và cờ success.
    """
    try:
        # Clip các giá trị về đúng vùng universe
        b = float(np.clip(budget_vnd,   0,    10_000_000))
        h = float(np.clip(hunger_val,   0,    10))
        t = float(np.clip(time_val,     10,   90))
        hl = float(np.clip(health_val,  0,    10))
        w = float(np.clip(weather_score, 0,   10))

        # Đưa 5 đầu vào vào bộ mô phỏng
        food_sim.input['Budget']  = b
        food_sim.input['Hunger']  = h
        food_sim.input['Time']    = t
        food_sim.input['Health']  = hl
        food_sim.input['Weather'] = w

        # Kích hoạt & giải mờ (defuzzification bằng centroid)
        food_sim.compute()

        # Đọc kết quả thô từ 4 đầu ra
        price_raw   = food_sim.output['Price']
        meal_raw    = food_sim.output['MealType']
        cuisine_raw = food_sim.output['Cuisine']
        calo_raw    = food_sim.output['Calories']

        # Chuyển điểm số → nhãn chữ
        price_label   = _label_price(price_raw)
        meal_label    = _label_meal(meal_raw)
        cuisine_label = _label_cuisine(cuisine_raw)
        calo_label    = _label_calo(calo_raw)

        return {
            "success":       True,
            # Nhãn tiếng Anh (dùng để so khớp CSV)
            "price_label":   price_label,
            "meal_label":    meal_label,
            "cuisine_label": cuisine_label,
            "calo_label":    calo_label,
            # Giá trị thô (dùng để debug / báo cáo đồ án)
            "price_raw":     round(price_raw, 0),
            "meal_raw":      round(meal_raw, 2),
            "cuisine_raw":   round(cuisine_raw, 2),
            "calo_raw":      round(calo_raw, 2),
            # Nhãn tiếng Việt (dùng hiển thị UI)
            "price_vi":      PRICE_VI.get(price_label,   price_label),
            "meal_vi":       MEAL_VI.get(meal_label,     meal_label),
            "cuisine_vi":    CUISINE_VI.get(cuisine_label, cuisine_label),
            "calo_vi":       CALO_VI.get(calo_label,    calo_label),
        }

    except Exception as e:
        # ── Fallback an toàn: trả kết quả mặc định nếu scikit-fuzzy lỗi ──
        print(f"[fuzzy_engine] Lỗi: {e}")
        return {
            "success":       False,
            "error":         str(e),
            "price_label":   "Moderate",
            "meal_label":    "Full meal",
            "cuisine_label": "Vietnamese",
            "calo_label":    "Medium",
            "price_raw":     150_000.0,
            "meal_raw":      55.0,
            "cuisine_raw":   5.0,
            "calo_raw":      5.0,
            "price_vi":      PRICE_VI["Moderate"],
            "meal_vi":       MEAL_VI["Full meal"],
            "cuisine_vi":    CUISINE_VI["Vietnamese"],
            "calo_vi":       CALO_VI["Medium"],
        }