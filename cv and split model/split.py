import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import joblib

# ---------------- LOAD DATA ----------------
df = pd.read_csv("dataset.csv")

# ---------------- ENCODING ----------------
le_stop = LabelEncoder()
le_day = LabelEncoder()
le_corridor = LabelEncoder()
le_time = LabelEncoder()

df["stop"] = le_stop.fit_transform(df["stop"])
df["day"] = le_day.fit_transform(df["day"])
df["corridor"] = le_corridor.fit_transform(df["corridor"])
df["time_slot"] = le_time.fit_transform(df["time_slot"])

# ---------------- FEATURES ----------------
X = df[["stop", "day", "time_slot", "total", "corridor"]]
y = df["percentage"]

# ---------------- TRAIN MODEL ----------------
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

print("✅ Model trained")

# ---------------- SAVE MODEL ----------------
joblib.dump({
    "model": model,
    "le_stop": le_stop,
    "le_day": le_day,
    "le_corridor": le_corridor,
    "le_time": le_time
}, "route_model.pkl")

print("✅ Model saved as route_model.pkl")