#!/usr/bin/env python3
"""
Kafka Admin - Create Netflix Streaming Topic
Run this ONCE to set up the Kafka topic before starting producer/consumer
"""

from kafka.admin import KafkaAdminClient, NewTopic

# Configuration - UPDATE THIS!
KAFKA_BOOTSTRAP_SERVERS = "34.44.222.225:9092"  # Your VM's external IP
TOPIC_NAME = "netflix_watch_events"
NUM_PARTITIONS = 3  # More partitions = more parallel processing
REPLICATION_FACTOR = 1  # Single broker = replication 1


def delete_topic(admin, topic_name):
    """Delete existing topic (useful for cleanup)"""
    try:
        admin.delete_topics(topics=[topic_name])
        print(f"✓ Deleted topic: {topic_name}")
    except Exception as e:
        print(f"⊘ Could not delete topic {topic_name}: {e}")


def create_topic(admin, topic_name, num_partitions, replication_factor):
    """Create Kafka topic for Netflix streaming"""
    topic = NewTopic(
        name=topic_name,
        num_partitions=num_partitions,
        replication_factor=replication_factor,
    )

    try:
        admin.create_topics(new_topics=[topic], validate_only=False)
        print(f"✓ Created topic: {topic_name}")
        print(f"  Partitions: {num_partitions}")
        print(f"  Replication: {replication_factor}")
    except Exception as e:
        print(f"⚠️  Topic creation failed: {e}")
        print(f"   (Topic may already exist)")


if __name__ == "__main__":
    print("=" * 80)
    print("NETFLIX STREAMING KAFKA TOPIC SETUP")
    print("=" * 80)

    # Create admin client
    admin_client = KafkaAdminClient(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, client_id="NetflixAdmin"
    )

    print(f"\nConnected to Kafka: {KAFKA_BOOTSTRAP_SERVERS}")

    # Optional: Delete existing topic (uncomment to reset)
    delete_topic(admin_client, TOPIC_NAME)

    # Create topic
    create_topic(admin_client, TOPIC_NAME, NUM_PARTITIONS, REPLICATION_FACTOR)

    print("\n" + "=" * 80)
    print("SETUP COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Run producer.py on your laptop to stream data")
    print("  2. Run 03_streaming_pipeline_netflix_kafka.ipynb in Jupyter")
    print("=" * 80)
