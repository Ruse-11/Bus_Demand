import pandas as pd
import random
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------

DATASET_FILE = "chennai_bus_demand_200d.csv"
BUS_CAPACITY = 50
LEARNING_RATE = 0.1

START_TIME = datetime.strptime("05:00", "%H:%M")
END_TIME = datetime.strptime("10:00", "%H:%M")

# -----------------------------
# LOAD DATASET
# -----------------------------

df = pd.read_csv(DATASET_FILE)

# -----------------------------
# STOP DEFINITIONS
# -----------------------------

STOPS = {
    "Porur": (13.036249887328198, 80.15330188330523),
    "Valasaravakkam": (13.041018584890555, 80.17295100513537),
    "Iyyappanthangal": (13.037729409724287, 80.13684511959497),
    "Ramapuram": (13.025125453836557, 80.1768439794521)
}


STOP_CORRIDOR_MAP = {
    "Porur": ["Vadapalani", "Thiruvanmiyur","Broadway"],
    "Valasaravakkam": ["Vadapalani", "Broadway"],
    "Iyyappanthangal": ["Vadapalani", "Thiruvanmiyur","Broadway"],
    "Ramapuram": ["Thiruvanmiyur"]
}

CORRIDORS = ["Vadapalani", "Broadway", "Thiruvanmiyur"]

# Waiting time tracker
waiting_time = {c: 0 for c in CORRIDORS}

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def get_time_range(current_time):
    minute_block = "00" if current_time.minute < 30 else "30"
    start_str = current_time.strftime(f"%H:{minute_block}")
    end_time = current_time.replace(minute=int(minute_block)) + timedelta(minutes=30)
    end_str = end_time.strftime("%H:%M")
    return f"{start_str}-{end_str}"


def get_probabilities(stop, day_type, time_range):
    filtered = df[
        (df["Bus_Stop"] == stop) &
        (df["Day_Type"] == day_type) &
        (df["Time_Range"] == time_range)
    ]

    if filtered.empty:
        return {c: 0 for c in CORRIDORS}

    probs = {}
    for c in CORRIDORS:
        col = f"Prob_To_{c}"
        if col in filtered.columns:
            probs[c] = filtered[col].mean()
        else:
            probs[c] = 0

    return probs


# -----------------------------
# SIMULATION LOOP
# -----------------------------

current_time = START_TIME

print("\n🚍 Starting Simulation...\n")

while current_time <= END_TIME:

    print(f"\n⏰ Time: {current_time.strftime('%H:%M')}")

    day_type = "Weekday"
    time_range = get_time_range(current_time)

    # Step 1 — Generate random stop demand
    stop_demand = {
        stop: random.randint(10, 60)
        for stop in STOPS
    }

    print("📍 Stop Demand:", stop_demand)

    # Step 2 — Corridor Demand Aggregation
    corridor_demand = {c: 0 for c in CORRIDORS}

    for stop, demand in stop_demand.items():
        probs = get_probabilities(stop, day_type, time_range)

        for corridor in STOP_CORRIDOR_MAP[stop]:
            predicted = demand * probs.get(corridor, 0)
            corridor_demand[corridor] += predicted

    print("📊 Predicted Corridor Demand:", corridor_demand)

    # Step 3 — Calculate Scores
    scores = {}
    for c in CORRIDORS:
        scores[c] = corridor_demand[c] * 0.7 + waiting_time[c] * 0.3

    print("📈 Corridor Scores:", scores)

    # Step 4 — Select Route to Dispatch
    selected_corridor = max(scores, key=scores.get)

    print(f"🚌 Dispatching Bus to {selected_corridor}")

    # Step 5 — Simulate Actual Boarding
    actual_boarding = {}

    for stop, demand in stop_demand.items():
        if selected_corridor in STOP_CORRIDOR_MAP[stop]:

            probs = get_probabilities(stop, day_type, time_range)
            predicted = demand * probs.get(selected_corridor, 0)

            noise = random.randint(-5, 5)
            actual = max(0, predicted + noise)

            actual_boarding[stop] = actual

            # Reinforcement Update
            if demand > 0:
                error = actual - predicted
                update = LEARNING_RATE * (error / demand)
                new_prob = probs[selected_corridor] + update

                # Clamp between 0 and 1
                new_prob = max(0, min(1, new_prob))

    print("🎟 Actual Boarding:", actual_boarding)

    # Step 6 — Update Waiting Time
    for c in CORRIDORS:
        if c == selected_corridor:
            waiting_time[c] = 0
        else:
            waiting_time[c] += 30

    print("⏳ Waiting Time:", waiting_time)

    # Move to next time slot
    current_time += timedelta(minutes=30)

print("\n✅ Simulation Finished!")