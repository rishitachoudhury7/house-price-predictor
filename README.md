# 🏛 The Appraisal — House Price Predictor

End-to-end machine learning system that predicts house sale prices on the Ames Housing dataset, deployed as a containerized API with a live web interface.

**Live demo:** [house-price-predictor-jfm2efkvhmgjczd8wqwa3z.streamlit.app](https://house-price-predictor-jfm2efkvhmgjczd8wqwa3z.streamlit.app)
**API (Docker, on Render):** [house-price-api-docker.onrender.com/docs](https://house-price-api-docker.onrender.com/docs)

> Free-tier hosting note: the API sleeps after 15 minutes of inactivity. The first request after a sleep can take 30–50 seconds to respond — this is expected, not a bug.

---

## What this project demonstrates

| Skill area | What was built |
|---|---|
| Data science | EDA, multicollinearity analysis, feature engineering, ordinal encoding |
| Modeling | Linear Regression → Random Forest → Random Forest (tuned) → XGBoost → XGBoost + Optuna |
| Hyperparameter tuning | RandomizedSearchCV, Optuna (100-trial Bayesian search) |
| MLOps | MLflow experiment tracking, model registry, versioning |
| Backend engineering | FastAPI with Pydantic request/response validation |
| Frontend engineering | Custom-designed Streamlit UI |
| DevOps | Docker containerization, deployed both natively and as a container, zero-downtime redeploys on Render |

---

## Results

| Model | RMSE | R² | RMSLE | MAPE |
|---|---|---|---|---|
| Linear Regression (baseline) | $83,073 | 0.10 | — | — |
| Random Forest | $29,031 | 0.890 | 0.1522 | 10.66% |
| Random Forest (RandomizedSearchCV tuned) | $28,634 | 0.893 | 0.1538 | 10.59% |
| XGBoost (log-target, engineered features) | $26,398 | 0.909 | 0.1331 | 9.18% |
| **XGBoost + Optuna (final)** | **$25,107** | **0.918** | **0.1272** | **8.72%** |

Final model places in the **top ~20–25%** of the Kaggle Ames Housing leaderboard by RMSLE — the competition's actual scoring metric.

**Why RMSLE matters more than RMSE here:** house prices are right-skewed (a few very expensive homes dominate squared error). RMSLE scores percentage error instead, so a $12k miss on a $80k house counts the same as a $75k miss on a $500k house — a fairer measure of real-world prediction quality.

---

## Architecture

```
Raw data (Kaggle Ames Housing, 1460 train + 1459 test rows)
        │
        ▼
Cleaning & null handling (neighborhood-median LotFrontage, etc.)
        │
        ▼
Feature engineering (TotalSF, TotalBath, HouseAge, RemodAge,
   IsRemodeled, TotalPorch, Has* binary flags)
        │
        ▼
Ordinal encoding (quality columns) + one-hot encoding (categoricals)
        │
        ▼
Log-transform target (log1p(SalePrice)) — corrects right-skew
        │
        ▼
XGBoost, tuned via Optuna (100 trials, RMSLE-optimized)
        │
        ▼
MLflow — experiment tracking + model registry (v1)
        │
        ▼
FastAPI backend ── containerized with Docker ── deployed on Render
        │
        ▼
Streamlit frontend ── deployed on Streamlit Cloud
```

---

## Tech stack

**ML:** Python, pandas, scikit-learn, XGBoost, Optuna
**MLOps:** MLflow (tracking + registry)
**Backend:** FastAPI, Pydantic, uvicorn
**Frontend:** Streamlit
**Infra:** Docker, Render, Streamlit Cloud
**Data:** [Ames Housing dataset](https://www.kaggle.com/c/house-prices-advanced-regression-techniques) (Kaggle)

---

## Repository structure

```
house-price-predictor/
├── House_Price_Kaggle01.ipynb   # Full training pipeline: EDA → modeling → MLflow logging
├── api.py                       # FastAPI backend — loads model, serves /predict
├── app.py                       # Streamlit frontend
├── Dockerfile                   # Container build for the API
├── requirements.txt
├── runtime.txt
├── feature_columns.json         # Exact column order the model expects
├── feature_defaults.json        # Median-fill values for fields the user doesn't set
├── xgb_model.pkl                # Serialized final model
├── data_description.txt         # Kaggle's original feature documentation
├── train.csv / test.csv
└── submission.csv                # Final Kaggle submission
```

---

## Running locally

**1. Clone and install**
```bash
git clone https://github.com/rishitachoudhury7/house-price-predictor.git
cd house-price-predictor
pip install -r requirements.txt
```

**2. Run the API**
```bash
python api.py
```
Visit `http://localhost:8000/docs` for interactive Swagger documentation.

**3. Run the frontend** (in a second terminal)
```bash
streamlit run app.py
```
Visit `http://localhost:8501`.

### Or run the API in Docker
```bash
docker build -t house-price-api .
docker run -p 8000:8000 house-price-api
```

---

## API reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Returns API and model load status |
| `/predict` | POST | Returns predicted price + confidence range for a given house |
| `/model-info` | GET | Returns model metadata and performance metrics |
| `/docs` | GET | Interactive Swagger UI |

**Example request to `/predict`:**
```json
{
  "OverallQual": 7,
  "GrLivArea": 1800,
  "TotalBsmtSF": 900,
  "FirstFlrSF": 1000,
  "GarageCars": 2,
  "GarageArea": 400,
  "Fireplaces": 1,
  "FullBath": 2,
  "HalfBath": 1,
  "LotArea": 8000,
  "LotFrontage": 70,
  "YearBuilt": 1995,
  "YearRemodAdd": 2005,
  "YrSold": 2010,
  "Neighborhood": "CollgCr"
}
```

**Example response:**
```json
{
  "predicted_price": 172016.0
}
```

---

## What I'd improve next

- Re-run Optuna's search on the corrected (post-bug-fix) feature set for a fully optimized model — the current Optuna params were tuned before a missing feature-engineering step was caught and fixed
- Add SHAP value explanations to the `/predict` response for per-prediction interpretability
- Move from pickle to ONNX for faster, framework-independent inference
- Add a CI/CD pipeline (GitHub Actions) to auto-test and redeploy on push
- Persist MLflow tracking to a remote backend (currently local SQLite) for true team collaboration

---

## Author

**Rishita Choudhury**
[GitHub](https://github.com/rishitachoudhury7) · Data Scientist (Fraud Analysis background, transitioning into ML/Data Engineering)
