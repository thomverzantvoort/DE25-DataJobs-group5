# prepare_streaming_data.py
# Run this locally to generate a manageable set of streaming JSON files

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import shutil

print("=" * 80)
print("NETFLIX STREAMING DATA PREPARATION (RECENT DATA ONLY)")
print("=" * 80)

# Configuration
INPUT_FILE = "../../Data/raw/watch_history.csv"
OUTPUT_DIR = "../../Data/streaming/"
NUM_FILES = 30  # Create exactly 25 files
EVENTS_PER_FILE = 150  # 150 events per file = 3,750 total events

TOTAL_EVENTS = NUM_FILES * EVENTS_PER_FILE

print(f"\nConfiguration:")
print(f"   Number of files: {NUM_FILES}")
print(f"   Events per file: {EVENTS_PER_FILE}")
print(f"   Total events to process: {TOTAL_EVENTS}")

print(f"\nLoading watch_history from: {INPUT_FILE}")

# Load data
df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} total watch events")
print(f"   Original date range: {df['watch_date'].min()} to {df['watch_date'].max()}")

# Sort by date descending (most recent first) and take top N
df["watch_date_dt"] = pd.to_datetime(df["watch_date"])
df = df.sort_values("watch_date_dt", ascending=False).reset_index(drop=True)

# Take only the most recent events
df = df.head(TOTAL_EVENTS)

print(f"\nSelected {len(df)} most recent events")
print(f"   Selected date range: {df['watch_date'].max()} to {df['watch_date'].min()}")

# Add realistic timestamps
print("\nAdding synthetic timestamps...")


def generate_realistic_hour():
    """Generate hour with peak probability in evening (18:00-23:00)"""
    hours = list(range(24))
    # Define relative probabilities (don't need to sum to 1)
    prob_weights = [
        1, 1, 1, 1, 1, 2,  # 0-5 (early morning, low)
        2, 3, 3, 3, 3, 4,  # 6-11 (morning, low-medium)
        4, 4, 4, 4, 5, 5,  # 12-17 (afternoon, medium)
        8, 9, 10, 10, 8, 6   # 18-23 (evening, peak)
    ]
    # NumPy will automatically normalize these
    prob_weights = np.array(prob_weights)
    probabilities = prob_weights / prob_weights.sum()  # Normalize to sum to 1.0
    
    return np.random.choice(hours, p=probabilities)

np.random.seed(42)
df["hour"] = [generate_realistic_hour() for _ in range(len(df))]
df["minute"] = np.random.randint(0, 60, len(df))
df["second"] = np.random.randint(0, 60, len(df))

# Create full timestamp
df["timestamp"] = (
    df["watch_date_dt"]
    + pd.to_timedelta(df["hour"], unit="h")
    + pd.to_timedelta(df["minute"], unit="m")
    + pd.to_timedelta(df["second"], unit="s")
)

# Sort by timestamp for proper streaming order
df = df.sort_values("timestamp").reset_index(drop=True)

# Clean up temporary columns
df = df.drop(["hour", "minute", "second", "watch_date_dt"], axis=1)
df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

print(f"Added timestamps: {df['timestamp'].min()} to {df['timestamp'].max()}")

# Show sample
print("\n📊 Sample of prepared data:")
print(df[["session_id", "user_id", "movie_id", "timestamp", "action"]].head(5))




# Split into exactly NUM_FILES JSON files
print(f"\nCreating {NUM_FILES} JSON files ({EVENTS_PER_FILE} events per file)...")

for file_num in range(NUM_FILES):
    start_idx = file_num * EVENTS_PER_FILE
    end_idx = start_idx + EVENTS_PER_FILE

    batch = df.iloc[start_idx:end_idx]
    records = batch.to_dict(orient="records")

    file_path = f"{OUTPUT_DIR}/part-{file_num:05d}.json"
    with open(file_path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    if (file_num + 1) % 5 == 0:
        print(f"   Created {file_num + 1}/{NUM_FILES} files...")

print(f"\nCreated {NUM_FILES} JSON files in {OUTPUT_DIR}")

# Summary statistics
total_size_mb = sum(
    os.path.getsize(f"{OUTPUT_DIR}/{f}") for f in os.listdir(OUTPUT_DIR)
) / (1024 * 1024)

print("\n" + "=" * 80)
print("DATA PREPARATION COMPLETE!")
print("=" * 80)
print(f"\nOutput location: {OUTPUT_DIR}")
print(f"Files created: {NUM_FILES}")
print(f"Total events: {len(df)}")
print(f"Events per file: {EVENTS_PER_FILE}")
print(f"Total size: {total_size_mb:.2f} MB")
print(f"\nDate range: {df['timestamp'].min()} to {df['timestamp'].max()}")

print(f"\nNext steps:")
print(f"  1. Upload to GCS:")
print(f"     gsutil -m cp -r {OUTPUT_DIR} gs://data_netflix_2025/streaming/")
print(f"\n  2. Verify upload:")
print(f"     gsutil ls gs://data_netflix_2025/streaming/netflix_stream/")
print(f"\n  3. Run streaming notebook on VM")
print(f"     - With maxFilesPerTrigger=1, processing will take ~4 minutes")
print(f"     - Each trigger processes 1 file with {EVENTS_PER_FILE} events")
print("=" * 80)
