import requests

# Test Health Endpoint
health = requests.get("http://127.0.0.1:8000/health")

print("Health Status:")
print(health.status_code)
print(health.json())

print("\n" + "=" * 50 + "\n")

# Test Prediction Endpoint
payload = {
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

prediction = requests.post(
    "http://127.0.0.1:8000/predict",
    json=payload
)

print("Prediction Status:")
print(prediction.status_code)
print(prediction.json())