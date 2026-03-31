import pandas as pd
import numpy as np

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

model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

print("✅ Model trained")

# ---------------- SAVE MODEL ----------------

joblib.dump(model, "model.pkl")
joblib.dump(le_stop, "le_stop.pkl")
joblib.dump(le_day, "le_day.pkl")
joblib.dump(le_corridor, "le_corridor.pkl")
joblib.dump(le_time, "le_time.pkl")

print("✅ Model and encoders saved")


# ---------------- PREDICT FUNCTION ----------------

STOP_CORRIDORS = {
    "Porur": ["Vadapalani", "Thiruvanmiyur","Broadway"],
    "Valasaravakkam": ["Vadapalani", "Broadway"],
    "Iyyappanthangal": ["Vadapalani", "Thiruvanmiyur","Broadway"],
    "Ramapuram": ["Thiruvanmiyur"]
}

def predict_split(stop, day, time_slot, total):

    model = joblib.load("model.pkl")
    le_stop = joblib.load("le_stop.pkl")
    le_day = joblib.load("le_day.pkl")
    le_corridor = joblib.load("le_corridor.pkl")
    le_time = joblib.load("le_time.pkl")

    corridors = STOP_CORRIDORS[stop]
    results = {}

    for corridor in corridors:
        X = pd.DataFrame([[
            le_stop.transform([stop])[0],
            le_day.transform([day])[0],
            le_time.transform([time_slot])[0],
            total,
            le_corridor.transform([corridor])[0]
        ]], columns=["stop","day","time_slot","total","corridor"])

        pred = model.predict(X)[0]
        results[corridor] = max(pred, 0)

    # normalize
    total_pred = sum(results.values())

    for k in results:
        results[k] = round((results[k] / total_pred) * 100, 2)

    return results


# ---------------- TEST ----------------

if __name__ == "__main__":
    result = predict_split(
        stop="Porur",
        day="Mon",
        time_slot="08:30-09:00",
        total=80
    )

    print("\nRoute Split:")
    print(result)