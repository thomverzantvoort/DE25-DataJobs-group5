#!/usr/bin/env python3
"""
Netflix Streaming Kafka Producer
Reads JSON batch files and streams them to Kafka topic
Run this on your LOCAL MACHINE (not in Jupyter)
"""

import json
import glob
import time
from pathlib import Path
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configuration - UPDATE THESE!
KAFKA_BOOTSTRAP_SERVERS = "34.44.222.225:9092"  # Your VM's external IP
KAFKA_TOPIC = "netflix_watch_events"
JSON_DATA_DIR = "../../Data/streaming"
EVENTS_PER_SECOND = 5  # Simulate realistic streaming rate
BATCH_DELAY_SECONDS = 10  # Delay between batches (simulates time gaps)


class NetflixStreamProducer:
    """Kafka producer for Netflix watch events"""

    def __init__(self, bootstrap_servers, topic):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",  # Wait for all replicas to acknowledge
            retries=3,
            max_in_flight_requests_per_connection=1,  # Ensure ordering
        )
        self.total_sent = 0
        self.total_errors = 0

    def send_event(self, event_data):
        """Send single event to Kafka"""
        try:
            future = self.producer.send(self.topic, value=event_data)
            # Block until message is sent (synchronous for demo purposes)
            record_metadata = future.get(timeout=10)
            self.total_sent += 1
            return True
        except KafkaError as e:
            print(f"❌ Error sending event: {e}")
            self.total_errors += 1
            return False

    def send_batch(self, batch_file):
        """Send all events from a JSON batch file"""
        batch_name = Path(batch_file).name
        events = []

        # Read JSON file (one event per line)
        with open(batch_file, "r") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line.strip()))

        print(f"\n📦 Processing batch: {batch_name}")
        print(f"   Events to send: {len(events)}")

        # Send events with rate limiting
        batch_start = time.time()
        for i, event in enumerate(events, 1):
            success = self.send_event(event)

            if success and i % 10 == 0:
                print(f"   Sent {i}/{len(events)} events...", end="\r")

            # Rate limiting: sleep to achieve target events/second
            if EVENTS_PER_SECOND > 0:
                time.sleep(1.0 / EVENTS_PER_SECOND)

        batch_duration = time.time() - batch_start
        print(f"   ✓ Batch complete: {len(events)} events in {batch_duration:.1f}s")

        return len(events)

    def close(self):
        """Flush and close producer"""
        self.producer.flush()
        self.producer.close()


def main():
    print("=" * 80)
    print("NETFLIX STREAMING KAFKA PRODUCER")
    print("=" * 80)
    print(f"Kafka Broker: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Source: {JSON_DATA_DIR}")
    print(f"Rate: {EVENTS_PER_SECOND} events/second")
    print("=" * 80)

    # Get all JSON batch files
    json_files = sorted(glob.glob(f"{JSON_DATA_DIR}/part-*.json"))

    if not json_files:
        print(f"\n❌ No JSON files found in {JSON_DATA_DIR}")
        print("   Make sure the path is correct!")
        return

    print(f"\nFound {len(json_files)} batch files to stream")

    # Create producer
    producer = NetflixStreamProducer(KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC)

    try:
        start_time = time.time()

        # Stream each batch file
        for batch_num, json_file in enumerate(json_files, 1):
            print(f"\n{'─' * 80}")
            print(f"BATCH {batch_num}/{len(json_files)}")

            # Send batch
            events_sent = producer.send_batch(json_file)

            # Wait between batches (simulates temporal gaps)
            if batch_num < len(json_files):
                print(f"\n   ⏳ Waiting {BATCH_DELAY_SECONDS}s before next batch...")
                time.sleep(BATCH_DELAY_SECONDS)

        total_time = time.time() - start_time

        # Summary
        print("\n" + "=" * 80)
        print("STREAMING COMPLETE")
        print("=" * 80)
        print(f"✓ Total batches: {len(json_files)}")
        print(f"✓ Total events sent: {producer.total_sent:,}")
        print(f"✓ Total errors: {producer.total_errors}")
        print(f"✓ Total time: {total_time:.1f}s")
        print(f"✓ Average rate: {producer.total_sent / total_time:.1f} events/second")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
    finally:
        print("\nClosing producer...")
        producer.close()
        print("✓ Producer closed")


if __name__ == "__main__":
    main()
