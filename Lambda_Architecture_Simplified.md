# Netflix Lambda Architecture - Simplified Diagram for Draw.io/Miro

## Component List for Visual Diagram

### 1. DATA SOURCES
- [Box] Netflix Dataset (Kaggle)
  - users.csv
  - movies.csv
  - watch_history.csv
  - reviews.csv
  - search_logs.csv
  - recommendation_logs.csv

### 2. CLOUD STORAGE
- [Box] Google Cloud Storage (GCS)
  - Bucket: data_netflix_2025
  - /raw/ (CSV files)
  - /streaming/ (JSON files)

### 3. SPEED LAYER COMPONENTS
- [Box] Kafka Producer (Local Machine)
  - kafka_producer.py
  - Reads JSON from /streaming/
  - Sends to Kafka at 5 events/sec

- [Box] Zookeeper
  - Port: 2181
  - Manages Kafka cluster

- [Box] Kafka Broker
  - Topic: netflix_watch_events
  - 3 partitions
  - Port: 9092 (external), 9093 (internal)

- [Box] Spark Driver (Jupyter Container)
  - Port: 8888
  - Notebook: 03_streaming_pipeline_netflix_kafkatopics.ipynb

- [Box] Spark Master
  - Port: 8080 (UI), 7077 (cluster)

- [Box] Spark Workers (2x)
  - Worker 1: Port 8081
  - Worker 2: Port 8082
  - Memory: 2GB each

- [Box] Spark Structured Streaming
  - Reads from Kafka
  - Joins with static data (users, movies from GCS)
  - 5-minute window aggregations
  - 10-second triggers
  - Churn detection

### 4. BATCH LAYER COMPONENTS
- [Box] Spark Driver (Jupyter Container)
  - Notebook: Batch_pipeline_Netflix.ipynb

- [Box] Spark Master
  - Same as Speed Layer

- [Box] Spark Workers (2x)
  - Same as Speed Layer

- [Box] Spark Batch Processing
  - Reads CSVs from GCS
  - Data quality checks
  - Data cleaning
  - Star schema joins
  - Monthly aggregations

### 5. SERVING LAYER
- [Box] Google BigQuery
  - Dataset: netflix_streaming
    - Table: engagement_health_realtime
  - Dataset: netflix_processed
    - Tables: Users, Movies, WatchHistory, Reviews, etc.
    - Tables: monthly_engagement, cohort_retention, content_performance, genre_performance, monthly_active_users

### 6. VISUALIZATION LAYER
- [Box] Looker Studio
  - Dashboard 1: Real-Time Engagement
  - Dashboard 2: Historical Trends

---

## Connection Flow (Arrows)

### SPEED LAYER FLOW:
1. Netflix Dataset → GCS (/raw/ and /streaming/)
2. GCS (/streaming/) → Kafka Producer (Local)
3. Kafka Producer → Kafka Broker (via external IP)
4. Kafka Broker → Spark Structured Streaming (via internal)
5. GCS (/raw/users.csv, movies.csv) → Spark Streaming (for joins)
6. Spark Streaming → BigQuery (netflix_streaming.engagement_health_realtime)
7. BigQuery → Looker Studio Dashboard 1

### BATCH LAYER FLOW:
1. Netflix Dataset → GCS (/raw/)
2. GCS (/raw/) → Spark Batch Processing
3. Spark Batch Processing → BigQuery (netflix_processed.*)
4. BigQuery → Looker Studio Dashboard 2

### INFRASTRUCTURE:
- Spark Driver → Spark Master (cluster connection)
- Spark Master → Spark Workers (task distribution)
- Zookeeper → Kafka Broker (coordination)

---

## Color Coding Suggestions

- **Data Sources**: Light Blue
- **Storage (GCS)**: Light Green
- **Speed Layer**: Orange/Red (hot path)
- **Batch Layer**: Blue (cold path)
- **Serving Layer (BigQuery)**: Yellow
- **Visualization**: Purple
- **Infrastructure (Docker)**: Grey box around Spark components

---

## Layout Suggestions

```
Top Row: Data Sources → GCS
Middle Left: Speed Layer (Kafka → Spark Streaming)
Middle Right: Batch Layer (GCS → Spark Batch)
Bottom: BigQuery → Looker Studio
```

---

## Key Metrics to Include

### Speed Layer:
- Processing: 5-minute windows
- Trigger: Every 10 seconds
- Latency: < 1 minute
- Output: Real-time engagement metrics

### Batch Layer:
- Processing: Monthly aggregations
- Schedule: Daily/hourly
- Latency: Hours
- Output: Historical trends

