import streamlit as st
import requests

# ── Page config ──
st.set_page_config(
    page_title="House Price Predictor",
    page_icon="🏠",
    layout="centered"
)

API_URL = "https://house-price-predictor-n1of.onrender.com"

# ── Header ──
st.title("🏠 House Price Predictor")
st.markdown("**XGBoost + Optuna | RMSLE: 0.1276 | R²: 0.919 | Top 25% Kaggle**")

# ── API Health check ──
try:
    health = requests.get(f"{API_URL}/health", timeout=3).json()
    st.success(f"✅ API Status: {health['status']} | Model loaded: {health['model_loaded']}")
except Exception:
    st.error("❌ FastAPI not reachable. Make sure api.py is running on port 8000.")
    st.stop()

st.divider()

# ── Input tabs ──
tab1, tab2, tab3, tab4 = st.tabs([
    "📐 Size & Structure",
    "📅 Age & Condition",
    "🚗 Garage & Extras",
    "📍 Location"
])

inputs = {}

with tab1:
    inputs['OverallQual'] = st.slider(
        "Overall Quality (1–10)", 1, 10, 7,
        help="1 = Very Poor, 10 = Excellent"
    )
    inputs['GrLivArea'] = st.number_input(
        "Above Ground Living Area (sqft)", min_value=300, max_value=6000, value=1800
    )
    inputs['TotalBsmtSF'] = st.number_input(
        "Total Basement Area (sqft)", min_value=0, max_value=3000, value=900
    )
    inputs['FirstFlrSF'] = st.number_input(
        "1st Floor Area (sqft)", min_value=300, max_value=4000, value=1000
    )

with tab2:
    year_built = st.number_input("Year Built", min_value=1870, max_value=2010, value=1995)
    year_remod = st.number_input("Year Remodeled", min_value=1950, max_value=2010, value=2005)
    yr_sold    = st.selectbox("Year Sold", [2006, 2007, 2008, 2009, 2010], index=4)

    inputs['YearBuilt']    = year_built
    inputs['YearRemodAdd'] = year_remod
    inputs['YrSold']       = yr_sold

    house_age = yr_sold - year_built
    remod_age = yr_sold - year_remod
    is_remod  = year_built != year_remod

    st.info(
        f"House Age: **{house_age} yrs** | "
        f"Remodel Age: **{remod_age} yrs** | "
        f"Remodeled: **{'Yes' if is_remod else 'No'}**"
    )

with tab3:
    inputs['GarageCars'] = st.selectbox("Garage Capacity (cars)", [0, 1, 2, 3, 4], index=2)
    inputs['GarageArea'] = st.number_input(
        "Garage Area (sqft)", min_value=0, max_value=1500, value=400
    )
    inputs['Fireplaces'] = st.selectbox("Fireplaces", [0, 1, 2, 3], index=1)
    inputs['FullBath']   = st.selectbox("Full Bathrooms", [0, 1, 2, 3, 4], index=2)
    inputs['HalfBath']   = st.selectbox("Half Bathrooms", [0, 1, 2], index=1)

with tab4:
    inputs['Neighborhood'] = st.selectbox("Neighborhood", [
        'NAmes', 'CollgCr', 'OldTown', 'Edwards', 'Somerst', 'NridgHt',
        'Gilbert', 'Sawyer', 'NWAmes', 'SawyerW', 'Mitchel', 'BrkSide',
        'Crawfor', 'IDOTRR', 'Timber', 'NoRidge', 'StoneBr', 'SWISU',
        'ClearCr', 'MeadowV', 'Blmngtn', 'BrDale', 'Veenker', 'NPkVill', 'Blueste'
    ])
    inputs['LotArea']     = st.number_input(
        "Lot Area (sqft)", min_value=1000, max_value=50000, value=8000
    )
    inputs['LotFrontage'] = st.number_input(
        "Lot Frontage (ft)", min_value=0, max_value=200, value=70
    )

# ── Predict button ──
st.divider()

if st.button("🔍 Predict Price", type="primary", use_container_width=True):

    with st.spinner("Calling prediction API..."):

        try:
            response = requests.post(
                f"{API_URL}/predict",
                json=inputs,
                timeout=10
            )

            result = response.json()

            if "predicted_price" in result:

                st.success("Prediction completed successfully!")

                st.metric(
                    "Predicted House Price",
                    f"${result['predicted_price']:,.0f}"
                )

            else:
                st.error(f"Unexpected response: {result}")

        except Exception as e:
            st.error(f"API Error: {e}")


# ── Model info expander ──
with st.expander("📊 Model Performance Details"):

    st.markdown("""
    **Model:** XGBoost Regressor

    **Hyperparameter Tuning:** Optuna

    **Performance Metrics**
    - RMSE: 21,500
    - R²: 0.919
    - RMSLE: 0.1276
    - MAPE: 11.4%

    **Dataset**
    - Ames Housing Dataset
    - 1,460 training samples
    - 200+ engineered features

    **Leaderboard Performance**
    - Top 25% Kaggle Submission
    """)
# ── Footer ──
st.divider()
st.markdown("""
**Stack:** XGBoost + Optuna · MLflow experiment tracking · FastAPI backend · Streamlit frontend  
**Data:** Ames Housing Dataset · 1,460 training samples · 200+ features
""")
