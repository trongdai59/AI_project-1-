# ============================================================
# app_desktop.py – AN Y | Desktop UI version
# Chuyển giao diện từ mobile mockup sang web app máy tính
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import time

from fuzzy_engine import run_fuzzy, temp_to_weather_score
from map_engine import load_restaurants, score_and_rank, build_result_map, build_route_map, map_to_html

st.set_page_config(
    page_title="ĂN Ý – Thấu ý, hợp bụng.",
    page_icon="🍜",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800;900&display=swap');
:root{
  --primary:#EE4D2D; --primary-dark:#C73E24; --primary-light:#FFF0ED;
  --bg:#F6F7FB; --card:#FFFFFF; --text:#202124; --muted:#6B7280;
  --border:#E8EAF0; --green:#00B14F; --blue:#0B74E5;
  --shadow:0 10px 28px rgba(15,23,42,.08); --radius:20px;
  --phone-w:405px; --phone-h:900px;
}
html,body,[class*="css"]{font-family:'Be Vietnam Pro',sans-serif!important;}
html,body{background:#e8ebf2!important;}
.stApp{
  background:radial-gradient(circle at top,#ffffff 0,#e8ebf2 58%,#d8dce6 100%)!important;
  color:var(--text)!important;
}
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], section[data-testid="stSidebar"]{display:none!important;}
.block-container{
  width:min(var(--phone-w), calc(100vw - 20px))!important;
  max-width:var(--phone-w)!important;
  height:min(var(--phone-h), calc(100vh - 28px))!important;
  min-height:620px!important;
  margin:14px auto 28px!important;
  padding:14px 14px 24px!important;
  background:var(--bg)!important;
  border:10px solid #111827!important;
  border-radius:38px!important;
  box-shadow:0 25px 70px rgba(15,23,42,.28)!important;
  overflow-y:auto!important;
  overflow-x:hidden!important;
  scroll-behavior:smooth!important;
  scrollbar-width:thin!important;
  scrollbar-color:rgba(238,77,45,.65) transparent!important;
}
.block-container:before{
  content:"";display:block;width:118px;height:5px;border-radius:999px;background:#111827;
  margin:0 auto 10px;opacity:.95;
  position:sticky;top:0;z-index:30;
}
.block-container::-webkit-scrollbar{width:6px;}
.block-container::-webkit-scrollbar-track{background:transparent;}
.block-container::-webkit-scrollbar-thumb{background:rgba(238,77,45,.55);border-radius:999px;}
.block-container::-webkit-scrollbar-thumb:hover{background:rgba(238,77,45,.78);}
[data-testid="stVerticalBlock"]{gap:.72rem!important;}
.any-topbar{
  background:linear-gradient(135deg,#EE4D2D,#FF7A3D);
  border-radius:24px;padding:14px 15px;margin-bottom:12px;
  box-shadow:0 12px 28px rgba(238,77,45,.22);color:white;
}
.any-topbar-row{display:flex;flex-direction:column;align-items:flex-start;justify-content:flex-start;gap:10px;}
.brand{display:flex;align-items:center;gap:10px}.brand-icon{width:46px;height:46px;border-radius:16px;background:white;color:#EE4D2D;display:flex;align-items:center;justify-content:center;font-size:25px;box-shadow:0 8px 22px rgba(0,0,0,.14)}
.brand h1{font-size:25px;line-height:1;margin:0;font-weight:900}.brand p{margin:3px 0 0;color:rgba(255,255,255,.82);font-size:12px;font-weight:600}
.nav-wrap{display:flex;gap:7px;align-items:center;width:100%;overflow:hidden}.nav-pill{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.28);border-radius:999px;padding:8px 10px;color:white;font-size:11px;font-weight:700;max-width:58%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.weather-pill{background:white;color:#EE4D2D;border-radius:999px;padding:8px 10px;font-size:11px;font-weight:800;white-space:nowrap;max-width:42%;overflow:hidden;text-overflow:ellipsis;}
.hero-card{background:linear-gradient(135deg,#EE4D2D,#FF7A3D);border-radius:24px;padding:18px;color:white;min-height:auto;box-shadow:var(--shadow);position:relative;overflow:hidden}.hero-card:after{content:"";position:absolute;right:-78px;bottom:-88px;width:190px;height:190px;border-radius:50%;background:rgba(255,255,255,.08)}
.hero-card h2{font-size:25px;font-weight:900;line-height:1.18;margin:0 0 9px}.hero-card p{color:rgba(255,255,255,.78);font-size:12px;line-height:1.55;max-width:100%;margin-bottom:0;}
.card{background:white;border:1px solid var(--border);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow);margin-bottom:12px}.card-title{font-size:16px;font-weight:900;margin:0 0 11px;display:flex;align-items:center;gap:8px}.muted{color:var(--muted);font-size:12px}.stat-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:9px;margin-top:14px}.stat{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.18);border-radius:16px;padding:10px}.stat b{display:block;font-size:16px}.stat span{font-size:11px;color:rgba(255,255,255,.72)}
.stButton>button{background:var(--primary)!important;color:white!important;border:0!important;border-radius:15px!important;padding:10px 8px!important;font-weight:800!important;font-size:12px!important;box-shadow:0 8px 18px rgba(238,77,45,.22)!important;transition:.18s!important;width:100%!important;min-height:38px!important}.stButton>button:hover{background:var(--primary-dark)!important;transform:translateY(-1px)!important}.stButton>button:disabled{opacity:.48!important;box-shadow:none!important;}
.stTextInput input,.stNumberInput input,.stTextArea textarea{border-radius:14px!important;border:1.5px solid var(--border)!important;padding:10px 12px!important;background:white!important;font-size:13px!important}.stSelectbox [data-baseweb="select"]>div{border-radius:14px!important;border:1.5px solid var(--border)!important}.stSlider [role="slider"]{background:var(--primary)!important}.stSlider{padding-top:0!important} label, .stCaption, [data-testid="stMarkdownContainer"] p{font-size:12px!important;}
.tag{display:inline-block;padding:4px 8px;border-radius:999px;font-size:11px;font-weight:800;margin:2px}.tag-red{background:#FFF0ED;color:#EE4D2D}.tag-green{background:#E8F8EF;color:#00B14F}.tag-blue{background:#EBF3FD;color:#0B74E5}.tag-gray{background:#F3F4F6;color:#6B7280}.rest-card{background:white;border:1px solid var(--border);border-radius:18px;padding:13px;margin-bottom:10px;box-shadow:0 8px 20px rgba(15,23,42,.055)}.rest-name{font-size:15px;font-weight:900;margin-bottom:3px}.rest-dish{color:#6B7280;font-size:12px;margin-bottom:9px}.rank-badge{float:right;background:#FFF0ED;color:#EE4D2D;border-radius:999px;padding:4px 9px;font-size:11px;font-weight:900}.fuzzy-banner{background:linear-gradient(135deg,#EE4D2D,#FF7A3D);border-radius:22px;padding:15px;color:white;box-shadow:0 12px 28px rgba(238,77,45,.21);margin-bottom:10px}.fuzzy-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}.fuzzy-item{background:rgba(255,255,255,.16);border-radius:15px;padding:10px}.fuzzy-item small{display:block;color:rgba(255,255,255,.72);font-weight:700;text-transform:uppercase;font-size:9px}.fuzzy-item b{font-size:13px}.order-item{background:white;border:1px solid var(--border);border-radius:18px;padding:13px;margin-bottom:10px;box-shadow:0 8px 20px rgba(15,23,42,.055)}
[data-testid="stHorizontalBlock"]{gap:.65rem!important;}
iframe{border-radius:18px!important;overflow:hidden!important;}
hr{margin:10px 0!important;}
div[data-testid="stDialog"] div[role="dialog"]{max-height:86vh!important;overflow-y:auto!important;border-radius:24px!important;}
@media(max-width:480px){
  .block-container{width:calc(100vw - 10px)!important;height:calc(100vh - 10px)!important;min-height:560px!important;border-width:7px!important;border-radius:31px!important;margin:5px auto 16px!important;padding:11px 11px 20px!important;}
  .hero-card h2{font-size:23px}.brand h1{font-size:23px}.any-topbar{padding:13px;border-radius:22px}.card{padding:14px}.fuzzy-banner{padding:13px}
}
</style>
""", unsafe_allow_html=True)


def _init():
    defaults = {
        "state":"home", "user_name":"", "user_phone":"", "user_address":"279 Nguyen Tri Phuong, Dien Hong, TPHCM",
        "user_lat":10.76094, "user_lng":106.66858, "budget":150000, "hunger":5.0, "time_wait":30,
        "health":5.0, "temp_c":28.0, "is_raining":False, "weather_desc":"Thời tiết đẹp", "weather_emoji":"",
        "fuzzy_result":None, "df":None, "top5":None, "result_map_html":None, "route_map_html":None,
        "selected_rest":None, "dist_km":0.0, "eta_min":15, "route_method":"", "history":[], "radius_km":3.0,
        "signed_in":False,
    }
    for k,v in defaults.items(): st.session_state.setdefault(k,v)
_init()

@st.cache_data(ttl=600)
def _fetch_weather(lat,lng):
    try:
        url=(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,precipitation,weather_code&timezone=Asia%2FHo_Chi_Minh")
        cur=requests.get(url,timeout=5).json()["current"]
        temp=float(cur["temperature_2m"]); rain=float(cur.get("precipitation",0))>0
        if rain: return temp, True, "Đang mưa", ""
        if temp>32: return temp, False, "Nắng nóng", ""
        return temp, False, "Thời tiết đẹp", ""
    except Exception: return 28.0, False, "Thời tiết đẹp", ""

@st.cache_data
def _load_df(): return load_restaurants("AI.DatasetFood.csv")

def _fmt_vnd(n): return f"{int(n):,}".replace(",", ".")+"đ"
def _go(state): st.session_state.state=state; st.rerun()

def _geocode_address(address):
    try:
        r=requests.get("https://nominatim.openstreetmap.org/search",params={"q":address+", Viet Nam","format":"json","limit":1},headers={"User-Agent":"AnYApp/1.0"},timeout=6)
        js=r.json()
        if js: return float(js[0]["lat"]), float(js[0]["lon"])
    except Exception: pass
    return None, None

def _boot_weather():
    if st.session_state.temp_c == 28.0:
        t,r,d,e=_fetch_weather(st.session_state.user_lat, st.session_state.user_lng)
        st.session_state.temp_c=t; st.session_state.is_raining=r; st.session_state.weather_desc=d; st.session_state.weather_emoji=e

def topbar(active="home"):
    st.markdown(f"""
    <div class="any-topbar"><div class="any-topbar-row">
      <div class="brand"><div class="brand-icon">🍜</div><div><h1>ĂN Ý</h1><p>Thấu ý, hợp bụng.</p></div></div>
      <div class="nav-wrap">
        <div class="nav-pill"> {st.session_state.user_address[:36]}...</div>
        <div class="weather-pill">{st.session_state.weather_emoji} {st.session_state.temp_c}°C – {st.session_state.weather_desc}</div>
      </div>
    </div></div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="small")
    with c1:
        if st.button("Trang chủ", key="nav_home", disabled=active=="home"): _go("home")
    with c2:
        if st.button("Kết quả", key="nav_result", disabled=active=="result" or st.session_state.top5 is None): _go("result")
    with c3:
        if st.button("Đơn hàng", key="nav_history", disabled=active=="history"): _go("history")
    with c4:
        if st.button("Hồ sơ", key="nav_profile", disabled=active=="profile"): _go("profile")

def page_signin():
    left=st.container(); right=st.container()
    with left:
        st.markdown("""<div class='hero-card'><h2>Ăn đúng món,<br>đúng ngân sách,<br>đúng cảm xúc.</h2><p>Phân tích ngân sách, độ đói, thời gian chờ, mục tiêu dinh dưỡng và thời tiết, sau đó gợi ý quán ăn phù hợp trên bản đồ.</p><div class='stat-grid'><div class='stat'><b>AI</b><span>Fuzzy Logic</span></div><div class='stat'><b>Map</b><span>Vị trí quán</span></div><div class='stat'><b>Food</b><span>Gợi ý món</span></div><div class='stat'><b>Fast</b><span>Đặt nhanh</span></div></div></div>""", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='card'><div class='card-title'>ĐĂNG NHẬP</div>", unsafe_allow_html=True)
        name=st.text_input("Họ và tên", value=st.session_state.user_name, placeholder="Nguyễn Văn A")
        phone=st.text_input("Số điện thoại", value=st.session_state.user_phone, placeholder="09xxxxxxxx")
        addr=st.text_input("Địa chỉ giao hàng", value=st.session_state.user_address)
        if st.button("Đăng nhập"):
            if not name.strip(): st.error("Vui lòng nhập tên của bạn!")
            else:
                st.session_state.user_name=name.strip(); st.session_state.user_phone=phone.strip(); st.session_state.user_address=addr.strip() or st.session_state.user_address
                lat,lng=_geocode_address(st.session_state.user_address)
                if lat and lng: st.session_state.user_lat=lat; st.session_state.user_lng=lng
                st.session_state.signed_in=True; _go("home")
        st.markdown("</div>", unsafe_allow_html=True)

def page_home():
    topbar("home")
    left=st.container(); right=st.container()
    with left:
        st.markdown("<div class='card'><div class='card-title'>Thiết lập nhu cầu</div>", unsafe_allow_html=True)
        budget=st.number_input("Ngân sách",10000,10000000,st.session_state.budget,10000,format="%d")
        st.caption(f"≈ {_fmt_vnd(budget)}")
        hunger=st.slider("Mức độ đói (0–10)",0.0,10.0,st.session_state.hunger,0.5)
        time_wait=st.slider("Thời gian chờ tối đa",15,60,st.session_state.time_wait,5,format="%d phút")
        health=st.slider("Mục tiêu dinh dưỡng: 0 = ăn kiêng, 10 = tăng cơ",0.0,10.0,st.session_state.health,0.5)
        radius=st.slider("Bán kính tìm quán",1.0,8.0,st.session_state.radius_km,0.5,format="%.1f km")
        if st.button("Tìm món"):
            st.session_state.budget=budget; st.session_state.hunger=hunger; st.session_state.time_wait=time_wait; st.session_state.health=health; st.session_state.radius_km=radius
            wscore=temp_to_weather_score(st.session_state.temp_c, st.session_state.is_raining)
            result=run_fuzzy(float(budget),float(hunger),float(time_wait),float(health),wscore)
            st.session_state.fuzzy_result=result
            df=_load_df(); st.session_state.df=df
            top5=score_and_rank(df,result["price_label"],result["meal_label"],result["cuisine_label"],st.session_state.user_lat,st.session_state.user_lng,st.session_state.radius_km)
            st.session_state.top5=top5
            m=build_result_map(top5,st.session_state.user_lat,st.session_state.user_lng,st.session_state.radius_km)
            st.session_state.result_map_html=map_to_html(m)
            _go("result")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown(f"""<div class='hero-card'><h2>Xin chào, {st.session_state.user_name or 'bạn'} 👋</h2><p>Điền nhu cầu ở bên trái, hệ thống sẽ phân tích bằng AI và hiển thị kết quả ở dạng dashboard mobile: bản đồ, top quán phù hợp, chi phí và trạng thái đơn hàng.</p><div class='stat-grid'><div class='stat'><b>{_fmt_vnd(st.session_state.budget)}</b><span>Ngân sách</span></div><div class='stat'><b>{st.session_state.hunger}/10</b><span>Độ đói</span></div><div class='stat'><b>{st.session_state.time_wait} phút</b><span>Thời gian chờ</span></div><div class='stat'><b>{st.session_state.radius_km} km</b><span>Bán kính</span></div></div></div>""", unsafe_allow_html=True)
        if st.session_state.selected_rest:
            r=st.session_state.selected_rest
            st.markdown(f"<div class='card'><div class='card-title'>Đơn đang giao...</div><b>{r['name']}</b><p class='muted'>Dự kiến giao khoảng {st.session_state.eta_min} phút.</p></div>", unsafe_allow_html=True)

def page_result():
    topbar("result")
    result=st.session_state.fuzzy_result; top5=st.session_state.top5
    if result is None or top5 is None:
        st.info("Chưa có kết quả. Hãy bấm TÌM MÓN NGAY ở trang chủ."); return
    st.markdown(f"""<div class='fuzzy-banner'><div class='card-title' style='color:white'>Món ngon cho bạn nè.</div><div class='fuzzy-grid'><div class='fuzzy-item'><small>Loại bữa ăn</small><b>{result['meal_vi']}</b></div><div class='fuzzy-item'><small>Ẩm thực</small><b>{result['cuisine_vi']}</b></div><div class='fuzzy-item'><small>Khoảng giá</small><b>{result['price_vi']}</b></div><div class='fuzzy-item'><small>Calo</small><b>{result['calo_vi']}</b></div></div></div>""", unsafe_allow_html=True)
    st.write("")
    left=st.container(); right=st.container()
    with left:
        st.markdown("<div class='card'><div class='card-title'>Bản đồ hàng quán</div>", unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("Phạm vi 3 km"):
                st.session_state.radius_km=3.0; _rebuild_map()
        with c2:
            if st.button("Phạm vi 5 km"):
                st.session_state.radius_km=5.0; _rebuild_map()
        if st.session_state.result_map_html: components.html(st.session_state.result_map_html, height=355, scrolling=False)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='card'><div class='card-title'>Quán ăn đề xuất</div>", unsafe_allow_html=True)
        seen=set(); rank=1
        for _,row in top5.iterrows():
            if row['name'] in seen: continue
            seen.add(row['name'])
            st.markdown(f"""<div class='rest-card'><span class='rank-badge'>#{rank}</span><div class='rest-name'>{row['name']}</div><div class='rest-dish'>{row['main_dish']}</div><span class='tag tag-red'>{_fmt_vnd(row['price'])}</span><span class='tag tag-green'>{row['calo_estimate(kcal)']} kcal</span><span class='tag tag-blue'>{row['dist_km']} km</span><span class='tag tag-gray'>{row['cuisine_suggestion']}</span></div>""", unsafe_allow_html=True)
            if st.button(f"Đặt món", key=f"order_{rank}"):
                st.session_state.selected_rest=row.to_dict(); _show_order_confirm(row.to_dict())
            rank += 1
            if rank>5: break
        st.markdown("</div>", unsafe_allow_html=True)

def _rebuild_map():
    result=st.session_state.fuzzy_result; df=st.session_state.df
    if result is None or df is None: return
    top5=score_and_rank(df,result["price_label"],result["meal_label"],result["cuisine_label"],st.session_state.user_lat,st.session_state.user_lng,st.session_state.radius_km)
    st.session_state.top5=top5
    st.session_state.result_map_html=map_to_html(build_result_map(top5,st.session_state.user_lat,st.session_state.user_lng,st.session_state.radius_km))
    st.rerun()

@st.dialog("Xác nhận đặt món")
def _show_order_confirm(rest):
    st.markdown(f"**{rest['name']}**  \n{rest['main_dish']}  \nĐơn giá: **{_fmt_vnd(rest['price'])}**")
    qty=st.number_input("Số lượng",1,20,1,1)
    note=st.text_area("Ghi chú cho quán", placeholder="VD: ít cay, không hành...")
    delivery=15000; total=int(rest['price'])*qty+delivery
    st.markdown(f"### Tổng cộng: {_fmt_vnd(total)}")
    name=st.text_input("Họ tên người nhận", value=st.session_state.user_name)
    phone=st.text_input("Số điện thoại", value=st.session_state.user_phone)
    addr=st.text_input("Địa chỉ giao hàng", value=st.session_state.user_address)
    if st.button("✅ XÁC NHẬN ĐẶT HÀNG"):
        st.session_state.user_name=name; st.session_state.user_phone=phone; st.session_state.user_address=addr
        m_route,dist,eta,method=build_route_map(st.session_state.user_lat,st.session_state.user_lng,rest['lat'],rest['lng'],rest['name'])
        st.session_state.route_map_html=map_to_html(m_route); st.session_state.dist_km=dist; st.session_state.eta_min=eta; st.session_state.route_method=method
        st.session_state.history.insert(0,{"time":datetime.now().strftime("%d/%m/%Y %H:%M"),"name":rest['name'],"dish":rest['main_dish'],"price":_fmt_vnd(rest['price']),"qty":qty,"total":_fmt_vnd(total),"address":addr,"status":"Đang giao","note":note})
        st.success("Đặt món thành công!"); time.sleep(.6); _go("delivering")

def page_delivering():
    topbar("history")
    left=st.container(); right=st.container()
    with left:
        st.markdown("<div class='card'><div class='card-title'>Đặt hàng thành công</div>", unsafe_allow_html=True)
        r=st.session_state.selected_rest
        if r:
            st.markdown(f"<b>{r['name']}</b><p class='muted'>{r['main_dish']}</p><span class='tag tag-blue'>{st.session_state.dist_km} km</span><span class='tag tag-green'>~{st.session_state.eta_min} phút</span>", unsafe_allow_html=True)
        st.markdown("<hr><b>Trạng thái</b><p>✅ Đặt hàng thành công</p><p>🍳 Đang chuẩn bị món</p><p>🛵 Shipper đang lấy hàng</p></div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='card'><div class='card-title'>🗺️ Đường giao hàng</div>", unsafe_allow_html=True)
        if st.session_state.route_map_html: components.html(st.session_state.route_map_html, height=355, scrolling=False)
        st.markdown("</div>", unsafe_allow_html=True)

def page_history():
    topbar("history")
    st.markdown("<div class='card'><div class='card-title'>📋 Lịch sử đơn hàng</div>", unsafe_allow_html=True)
    if not st.session_state.history: st.info("Chưa có đơn hàng nào.")
    else:
        for h in st.session_state.history:
            st.markdown(f"""<div class='order-item'><div style='display:flex;justify-content:space-between;gap:18px'><div><b>{h['name']}</b><p class='muted'>{h['dish']} × {h.get('qty',1)} · {h['time']}</p><p class='muted'>📍 {h['address']}</p></div><div style='text-align:right'><span class='tag tag-green'>{h.get('status','Đã đặt')}</span><h3 style='color:#EE4D2D'>{h.get('total',h['price'])}</h3></div></div></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def page_profile():
    topbar("profile")
    left=st.container(); right=st.container()
    with left:
        st.markdown(f"""<div class='card'><div class='card-title'>Hồ sơ cá nhân</div><h2>{st.session_state.user_name or 'Người dùng'}</h2><p class='muted'>☎️ {st.session_state.user_phone or 'Chưa cập nhật SĐT'}</p><p class='muted'>📍 {st.session_state.user_address}</p><span class='tag tag-red'>{len(st.session_state.history)} đơn hàng</span><span class='tag tag-blue'>{st.session_state.user_lat:.5f}, {st.session_state.user_lng:.5f}</span></div>""", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='card'><div class='card-title'>Cập nhật địa chỉ</div>", unsafe_allow_html=True)
        new_addr=st.text_input("Địa chỉ mới", placeholder="123 Lê Văn Việt, TP.HCM")
        if st.button("Cập nhật địa chỉ"):
            if new_addr.strip():
                lat,lng=_geocode_address(new_addr.strip())
                if lat and lng:
                    st.session_state.user_address=new_addr.strip(); st.session_state.user_lat=lat; st.session_state.user_lng=lng; st.success("Đã cập nhật địa chỉ."); st.rerun()
                else: st.warning("Không tìm thấy tọa độ. Hãy nhập địa chỉ rõ hơn.")
            else: st.error("Vui lòng nhập địa chỉ mới.")
        st.markdown("</div>", unsafe_allow_html=True)

def main():
    _boot_weather()
    if not st.session_state.signed_in:
        page_signin(); return
    state=st.session_state.state
    if state=="home": page_home()
    elif state=="result": page_result()
    elif state=="delivering": page_delivering()
    elif state=="history": page_history()
    elif state=="profile": page_profile()
    else: page_home()

if __name__ == "__main__": main()
