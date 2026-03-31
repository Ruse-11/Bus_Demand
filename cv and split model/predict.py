import pandas as pd
import joblib

# ---------------- LOAD MODEL ----------------
data = joblib.load("route_model.pkl")

model = data["model"]
le_stop = data["le_stop"]
le_day = data["le_day"]
le_corridor = data["le_corridor"]
le_time = data["le_time"]

# ---------------- STOP → CORRIDOR MAP ----------------
STOP_CORRIDORS = {
    "Porur": ["Vadapalani", "Thiruvanmiyur", "Broadway"],
    "Valasaravakkam": ["Vadapalani", "Broadway"],
    "Iyyappanthangal": ["Vadapalani", "Thiruvanmiyur", "Broadway"],
    "Ramapuram": ["Thiruvanmiyur"]
}

# ---------------- SAFE TRANSFORM FUNCTION ----------------
def safe_transform(encoder, value, name):
    if value not in encoder.classes_:
        raise ValueError(f"❌ Unknown {name}: {value}")
    return encoder.transform([value])[0]

# ---------------- PREDICT FUNCTION ----------------

def predict_split(stop, day, time_slot, total):

    if stop not in STOP_CORRIDORS:
        raise ValueError("❌ Invalid stop")

    # Encode common fields
    stop_enc = safe_transform(le_stop, stop, "stop")
    day_enc = safe_transform(le_day, day, "day")
    time_enc = safe_transform(le_time, time_slot, "time_slot")

    corridors = STOP_CORRIDORS[stop]
    results = {}

    for corridor in corridors:

        if corridor not in le_corridor.classes_:
            continue

        corridor_enc = safe_transform(le_corridor, corridor, "corridor")

        X = pd.DataFrame([[
            stop_enc,
            day_enc,
            time_enc,
            total,
            corridor_enc
        ]], columns=["stop", "day", "time_slot", "total", "corridor"])

        pred = model.predict(X)[0]
        results[corridor] = max(pred, 0)

    total_pred = sum(results.values())

    # Handle zero case
    if total_pred == 0:
        equal = round(100 / len(results), 2)
        return {k: equal for k in results}

    # Normalize to 100%
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

    print("\n🚌 Route Split:")
    for k, v in result.items():
        print(f"{k}: {v}%")