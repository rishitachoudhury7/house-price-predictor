import streamlit as st
import requests

# ── Page config ──
st.set_page_config(
    page_title="The Appraisal | House Price Predictor",
    page_icon="🏛",
    layout="centered"
)

API_URL = "https://house-price-api-docker.onrender.com"

# ── Custom CSS — Appraisal Ledger theme ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
}

.ledger-header {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 2.4rem;
    color: #F2EDE4;
    border-bottom: 2px solid #8B6F47;
    padding-bottom: 0.4rem;
    margin-bottom: 0.1rem;
    letter-spacing: 0.5px;
}

.ledger-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #8B6F47;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1.6rem;
}

.stamp-box {
    border: 1px solid #5C7A6B;
    background: rgba(92,122,107,0.08);
    border-radius: 2px;
    padding: 0.7rem 1rem;
    font-size: 0.85rem;
    color: #5C7A6B;
    margin-bottom: 1.5rem;
}

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #8B6F47;
    border-left: 3px solid #8B6F47;
    padding-left: 8px;
    margin: 1.8rem 0 0.8rem 0;
}

div.stButton > button {
    background-color: #C4502E !important;
    color: #F2EDE4 !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 0.7rem 1rem !important;
}
div.stButton > button:hover {
    background-color: #a83f23 !important;
}

.valuation-result {
    border: 2px solid #C4502E;
    border-radius: 2px;
    padding: 1.6rem;
    text-align: center;
    margin: 1.5rem 0;
    background: rgba(196,80,46,0.06);
}
.valuation-label {
    font-size: 0.75rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #8B6F47;
    margin-bottom: 0.3rem;
}
.valuation-price {
    font-family: 'Fraunces', serif;
    font-size: 3rem;
    font-weight: 600;
    color: #F2EDE4;
}
.valuation-range {
    font-size: 0.8rem;
    color: #5C7A6B;
    margin-top: 0.4rem;
}

.house-sketch {
    text-align: center;
    margin: 1rem 0 1.5rem 0;
}

footer, .reportview-container .main footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ── Header — letterhead style ──
st.markdown('<div class="ledger-header">The Appraisal</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ledger-sub">Automated property valuation · XGBoost + Optuna · RMSLE 0.1276</div>',
    unsafe_allow_html=True
)

# ── Blueprint house sketch (SVG, reacts subtly to inputs later if desired) ──
st.markdown("""
<div class="house-sketch">
<svg width="180" height="110" viewBox="0 0 180 110" xmlns="http://www.w3.org/2000/svg">
  <polygon points="20,55 90,15 160,55" fill="none" stroke="#8B6F47" stroke-width="1.5"/>
  <rect x="30" y="55" width="120" height="45" fill="none" stroke="#8B6F47" stroke-width="1.5"/>
  <rect x="45" y="70" width="18" height="30" fill="none" stroke="#5C7A6B" stroke-width="1"/>
  <rect x="85" y="70" width="16" height="16" fill="none" stroke="#5C7A6B" stroke-width="1"/>
  <rect x="118" y="70" width="16" height="16" fill="none" stroke="#5C7A6B" stroke-width="1"/>
  <line x1="90" y1="15" x2="90" y2="5" stroke="#8B6F47" stroke-width="1"/>
</svg>
</div>
""", unsafe_allow_html=True)

# ── API Health check ──
try:
    health = requests.get(f"{API_URL}/health", timeout=60).json()
    if health.get("status") == "healthy":
        st.markdown(
            '<div class="stamp-box">◆ SURVEYOR ONLINE — model loaded and ready for inspection</div>',
            unsafe_allow_html=True
        )
    else:
        st.error("Surveyor unavailable — model not loaded.")
        st.stop()
except Exception:
    st.error("Surveyor unreachable. The valuation office (API) may be waking up — please retry in a moment.")
    st.stop()

# ── Input sections (no tabs — single scroll, ledger-style) ──
st.markdown('<div class="section-label">I. Structure & size</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    overall_qual = st.slider("Overall quality (1–10)", 1, 10, 7, help="1 = Very poor, 10 = Excellent")
    gr_liv_area  = st.number_input("Living area above ground (sqft)", 300, 6000, 1800)
with c2:
    total_bsmt   = st.number_input("Basement area (sqft)", 0, 3000, 900)
    first_flr    = st.number_input("1st floor area (sqft)", 300, 4000, 1000)

st.markdown('<div class="section-label">II. Age & condition</div>', unsafe_allow_html=True)
c3, c4, c5 = st.columns(3)
with c3:
    year_built = st.number_input("Year built", 1870, 2010, 1995)
with c4:
    year_remod = st.number_input("Year remodeled", 1950, 2010, 2005)
with c5:
    yr_sold = st.selectbox("Year sold", [2006, 2007, 2008, 2009, 2010], index=4)

house_age = yr_sold - year_built
remod_age = yr_sold - year_remod
is_remod  = year_built != year_remod
st.caption(f"Age at sale: {house_age} yrs  ·  Remodel age: {remod_age} yrs  ·  Remodeled: {'Yes' if is_remod else 'No'}")

st.markdown('<div class="section-label">III. Garage & extras</div>', unsafe_allow_html=True)
c6, c7, c8 = st.columns(3)
with c6:
    garage_cars = st.selectbox("Garage capacity (cars)", [0, 1, 2, 3, 4], index=2)
    garage_area = st.number_input("Garage area (sqft)", 0, 1500, 400)
with c7:
    fireplaces = st.selectbox("Fireplaces", [0, 1, 2, 3], index=1)
    full_bath  = st.selectbox("Full bathrooms", [0, 1, 2, 3, 4], index=2)
with c8:
    half_bath = st.selectbox("Half bathrooms", [0, 1, 2], index=1)

st.markdown('<div class="section-label">IV. Location</div>', unsafe_allow_html=True)
c9, c10 = st.columns(2)
with c9:
    neighborhood = st.selectbox("Neighborhood", [
        'NAmes', 'CollgCr', 'OldTown', 'Edwards', 'Somerst', 'NridgHt',
        'Gilbert', 'Sawyer', 'NWAmes', 'SawyerW', 'Mitchel', 'BrkSide',
        'Crawfor', 'IDOTRR', 'Timber', 'NoRidge', 'StoneBr', 'SWISU',
        'ClearCr', 'MeadowV', 'Blmngtn', 'BrDale', 'Veenker', 'NPkVill', 'Blueste'
    ])
    lot_area = st.number_input("Lot area (sqft)", 1000, 50000, 8000)
with c10:
    lot_frontage = st.number_input("Lot frontage (ft)", 0, 200, 70)

inputs = {
    "OverallQual": overall_qual, "GrLivArea": gr_liv_area, "TotalBsmtSF": total_bsmt,
    "FirstFlrSF": first_flr, "GarageCars": garage_cars, "GarageArea": garage_area,
    "Fireplaces": fireplaces, "FullBath": full_bath, "HalfBath": half_bath,
    "LotArea": lot_area, "LotFrontage": lot_frontage, "YearBuilt": year_built,
    "YearRemodAdd": year_remod, "YrSold": yr_sold, "Neighborhood": neighborhood
}

# ── Predict ──
st.markdown("<br>", unsafe_allow_html=True)
if st.button("ISSUE VALUATION", use_container_width=True):
    with st.spinner("Surveying the property..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=inputs, timeout=15)
            result = response.json()

            if "predicted_price" in result:
                price = result["predicted_price"]
                low  = price * (1 - 0.0885)
                high = price * (1 + 0.0885)
                st.markdown(f"""
                <div class="valuation-result">
                    <div class="valuation-label">Appraised value</div>
                    <div class="valuation-price">${price:,.0f}</div>
                    <div class="valuation-range">Range: ${low:,.0f} — ${high:,.0f} (±8.85% MAPE)</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Unexpected response: {result}")
        except Exception as e:
            st.error(f"Valuation office did not respond: {e}")

# ── Model performance — ledger footer ──
with st.expander("View surveyor's credentials (model performance)"):
    st.markdown("""
    | Metric | Score |
    |---|---|
    | RMSE | $24,897 |
    | R² | 0.919 |
    | RMSLE | 0.1276 |
    | MAPE | 8.85% |
    | Kaggle standing | Top 25% |
    | Training data | Ames Housing · 1,460 records · 270 features |
    """)

st.markdown(
    '<div style="text-align:center; color:#5C7A6B; font-size:0.75rem; margin-top:2rem; '
    'border-top:1px solid #3D4A42; padding-top:1rem;">'
    'XGBoost + Optuna · MLflow tracking · FastAPI · Streamlit — deployed on Render & Streamlit Cloud'
    '</div>',
    unsafe_allow_html=True
)
