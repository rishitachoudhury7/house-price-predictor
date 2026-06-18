from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import json
import mlflow.pyfunc
import os

app = FastAPI(title="House Price Prediction API")

# Load feature metadata
with open("feature_columns.json", "r") as f:
    FEATURE_COLUMNS = json.load(f)

with open("feature_defaults.json", "r") as f:
    FEATURE_DEFAULTS = json.load(f)

# Load model
MODEL = None
MODEL_PATH = None

try:
    mlruns_path = os.path.join(os.getcwd(), "mlruns")

    for root, dirs, files in os.walk(mlruns_path):
        if "MLmodel" in files:
            MODEL_PATH = root
            break

    if MODEL_PATH:
        MODEL = mlflow.pyfunc.load_model(MODEL_PATH)
        print(f"Model loaded from: {MODEL_PATH}")

except Exception as e:
    print("Model load error:", e)


class HouseInput(BaseModel):
    OverallQual: float = 7
    GrLivArea: float = 1800
    TotalBsmtSF: float = 900
    FirstFlrSF: float = 1000
    GarageCars: float = 2
    GarageArea: float = 400
    Fireplaces: float = 1
    FullBath: float = 2
    HalfBath: float = 1
    LotArea: float = 8000
    LotFrontage: float = 70
    YearBuilt: float = 1995
    YearRemodAdd: float = 2005
    YrSold: float = 2010
    Neighborhood: str = "CollgCr"


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": MODEL is not None
    }


@app.post("/predict")
def predict(data: HouseInput):

    row = FEATURE_DEFAULTS.copy()

    payload = data.dict()

    for k, v in payload.items():

        if k == "Neighborhood":
            col = f"Neighborhood_{v}"

            if col in row:
                row[col] = 1

        elif k in row:
            row[k] = v

    df = pd.DataFrame([row])

    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0

    df = df[FEATURE_COLUMNS]

    if MODEL is None:
        return {
            "error": "Model not loaded"
        }

    pred_log = MODEL.predict(df)[0]
    pred_price = float(np.expm1(pred_log))

    return {
        "predicted_price": round(pred_price, 2)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )