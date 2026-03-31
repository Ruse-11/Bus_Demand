# dataset.py

import pandas as pd
import numpy as np
import random

# ---------------- CONFIG ----------------

STOP_CORRIDORS = {
    "Porur": ["Vadapalani", "Thiruvanmiyur","Broadway"],
    "Valasaravakkam": ["Vadapalani", "Broadway"],
    "Iyyappanthangal": ["Vadapalani", "Thiruvanmiyur","Broadway"],
    "Ramapuram": ["Thiruvanmiyur"]
}

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ---------------- TIME SLOTS ----------------

def generate_time_slots():
    slots = []
    for h in range(6, 22):
        slots.append(f"{h:02d}:00-{h:02d}:30")
        slots.append(f"{h:02d}:30-{h+1:02d}:00")
    return slots

TIME_SLOTS = generate_time_slots()

# ---------------- DATA GENERATION ----------------

def generate_dataset(n=3000):
    rows = []

    for _ in range(n):
        stop = random.choice(list(STOP_CORRIDORS.keys()))
        corridors = STOP_CORRIDORS[stop]

        day = random.choice(DAYS)
        time_slot = random.choice(TIME_SLOTS)

        total = random.randint(20, 120)

        # extract hour
        hour = int(time_slot[:2])

        # time-based patterns
        if hour < 10:
            base = [0.6, 0.25, 0.15]
        elif hour < 16:
            base = [0.3, 0.4, 0.3]
        else:
            base = [0.25, 0.5, 0.25]

        base = np.array(base[:len(corridors)])

        # add randomness
        weights = base + np.random.normal(0, 0.05, len(corridors))
        weights = np.clip(weights, 0.05, 1)
        weights = weights / weights.sum()

        splits = weights * total

        for i, corridor in enumerate(corridors):
            rows.append([
                stop,
                day,
                time_slot,
                total,
                corridor,
                splits[i] / total   # percentage
            ])

    df = pd.DataFrame(rows, columns=[
        "stop", "day", "time_slot", "total",
        "corridor", "percentage"
    ])

    return df


# ---------------- MAIN ----------------

if __name__ == "__main__":
    df = generate_dataset(5000)
    df.to_csv("dataset.csv", index=False)
    print("✅ Dataset saved as dataset.csv")