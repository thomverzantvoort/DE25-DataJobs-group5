# Netflix Data Engineering - Lambda Architecture Diagram

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           NETFLIX DATA ENGINEERING PIPELINE                              │
│                              LAMBDA ARCHITECTURE OVERVIEW                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA SOURCES                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────┐
    │                    Netflix 2025 Dataset (Kaggle)                    │
    │                                                                       │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
    │  │  users.csv   │  │  movies.csv  │  │watch_history │             │
    │  │              │  │              │  │    .csv      │             │
    │  │ • user_id    │  │ • movie_id   │  │ • session_id │             │
    │  │ • country    │  │ • title      │  │ • user_id    │             │
    │  │ • plan       │  │ • genre      │  │ • movie_id   │             │
    │  │ • spend      │  │ • rating     │  │ • timestamp  │             │
    │  └──────────────┘  └──────────────┘  │ • duration   │             │
    │                                       │ • progress   │             │
    │  ┌──────────────┐  ┌──────────────┐  └──────────────┘             │
    │  │ reviews.csv  │  │search_logs  │                                │
    │  │              │  │   .csv      │                                │
    │  │ • user_id    │  │ • user_id   │                                │
    │  │ • movie_id   │  │ • query     │                                │
    │  │ • rating     │  │ • timestamp │                                │
    │  └──────────────┘  └──────────────┘                                │
    │                                                                       │
    │  ┌──────────────┐                                                   │
    │  │recommendation│                                                   │
    │  │  _logs.csv   │                                                   │
    │  │              │                                                   │
    │  │ • user_id    │                                                   │
    │  │ • movie_id   │                                                   │
    │  │ • clicked    │                                                   │
    │  └──────────────┘                                                   │
    └─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Google Cloud       │
                    │  Storage (GCS)      │
                    │                     │
                    │  Bucket:            │
                    │  data_netflix_2025 │
                    │                     │
                    │  /raw/              │
                    │    • users.csv      │
                    │    • movies.csv     │
                    │    • watch_history  │
                    │    • reviews.csv    │
                    │    • search_logs    │
                    │    • recommend_logs  │
                    │                     │
                    │  /streaming/        │
                    │    • part-*.json    │
                    │    (30 files)       │
                    └─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐  ┌───────────────────┐
        │   SPEED LAYER     │  │   BATCH LAYER     │
        │   (Streaming)     │  │   (Historical)     │
        └───────────────────┘  └───────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    SPEED LAYER                                          │
│                              Real-Time Processing                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│  Local Machine / Producer                                                            │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  kafka_producer.py                                                            │  │
│  │  • Reads JSON files from Data/streaming/                                      │  │
│  │  • Sends events at 5 events/second                                            │  │
│  │  • 10s delay between batches                                                  │  │
│  │  • Topic: netflix_watch_events                                                 │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ (External IP: 136.113.194.230:9092)
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  Docker Container: Kafka Infrastructure                                             │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Zookeeper (Port 2181)                                                       │  │
│  │  • Manages Kafka cluster metadata                                            │  │
│  │  • Coordinates Kafka brokers                                                │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                              │                                                        │
│                              ▼                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Kafka Broker (kafka1:9093)                                                  │  │
│  │  • Topic: netflix_watch_events (3 partitions)                                │  │
│  │  • Stores streaming events as messages                                       │  │
│  │  • Created by: kafka_admin.py                                                │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ (Internal: kafka1:9093)
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  Docker Container: Spark Cluster                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Jupyter Notebook Container (spark-driver-app)                              │  │
│  │  • Port: 8888 (Jupyter), 4040-4050 (Spark UI)                               │  │
│  │  • Notebook: 03_streaming_pipeline_netflix_kafkatopics.ipynb                │  │
│  │  • Spark Driver: Initiates streaming jobs                                   │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                              │                                                        │
│                              ▼                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Spark Master (spark-master:7077)                                            │  │
│  │  • Port: 8080 (Web UI), 7077 (Cluster)                                       │  │
│  │  • Coordinates streaming jobs                                                 │  │
│  │  • Manages Spark workers                                                      │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                              │                                                        │
│                    ┌─────────┴─────────┐                                             │
│                    ▼                   ▼                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐                                │
│  │  Spark Worker 1      │  │  Spark Worker 2       │                                │
│  │  (spark-worker-1)    │  │  (spark-worker-2)    │                                │
│  │  • Port: 8081        │  │  • Port: 8082        │                                │
│  │  • Executes tasks    │  │  • Executes tasks    │                                │
│  │  • Memory: 2GB        │  │  • Memory: 2GB       │                                │
│  └──────────────────────┘  └──────────────────────┘                                │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Spark Structured Streaming Processing                                       │  │
│  │  ──────────────────────────────────────────────────────────────────────────  │  │
│  │  1. Read from Kafka Topic (netflix_watch_events)                            │  │
│  │  2. Parse JSON messages                                                      │  │
│  │  3. Join with Static Data:                                                   │  │
│  │     • users.csv (from GCS) → country, subscription, monthly_spend           │  │
│  │     • movies.csv (from GCS) → genre, imdb_rating, is_netflix_original       │  │
│  │  4. Detect Churn Signals:                                                    │  │
│  │     • Low engagement (<20% progress)                                        │  │
│  │     • Quality downgrade (SD/HD)                                              │  │
│  │     • Abandoned sessions                                                     │  │
│  │  5. Time-Windowed Aggregation (5-minute windows):                            │  │
│  │     • Group by: country, genre, device_type, quality, content_type         │  │
│  │     • Metrics: sessions, users, watch_time, churn_rates, revenue_impact      │  │
│  │  6. Watermark: 10 minutes (handle late data)                                │  │
│  │  7. Trigger: Every 10 seconds                                                │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Docker Volumes                                                              │  │
│  │  • notebooks: Jupyter notebooks                                              │  │
│  │  • spark-data: Shared data files                                             │  │
│  │  • spark-checkpoint: Streaming checkpoints (fault tolerance)                 │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Google BigQuery    │
                    │                     │
                    │  Dataset:          │
                    │  netflix_streaming  │
                    │                     │
                    │  Table:            │
                    │  engagement_health_│
                    │  realtime          │
                    │                     │
                    │  • 5-min windows   │
                    │  • Real-time metrics│
                    │  • Churn signals   │
                    │  • Alert levels     │
                    └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BATCH LAYER                                          │
│                            Historical Processing                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│  Google Cloud Storage (GCS)                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Bucket: netflix_data_25                                                     │  │
│  │  Path: gs://netflix_data_25/raw/                                             │  │
│  │    • users.csv                                                                │  │
│  │    • movies.csv                                                               │  │
│  │    • watch_history.csv                                                        │  │
│  │    • reviews.csv                                                              │  │
│  │    • search_logs.csv                                                          │  │
│  │    • recommendation_logs.csv                                                  │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  Docker Container: Spark Cluster                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Jupyter Notebook Container (spark-driver-app)                              │  │
│  │  • Notebook: Batch_pipeline_Netflix.ipynb                                   │  │
│  │  • Spark Driver: Initiates batch jobs                                        │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                              │                                                        │
│                              ▼                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Spark Master (spark-master:7077)                                            │  │
│  │  • Coordinates batch jobs                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                              │                                                        │
│                    ┌─────────┴─────────┐                                             │
│                    ▼                   ▼                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐                                │
│  │  Spark Worker 1      │  │  Spark Worker 2       │                                │
│  │  • Executes batch     │  │  • Executes batch     │                                │
│  │    processing tasks   │  │    processing tasks   │                                │
│  └──────────────────────┘  └──────────────────────┘                                │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Spark Batch Processing                                                      │  │
│  │  ──────────────────────────────────────────────────────────────────────────  │  │
│  │  1. Load Raw CSVs from GCS                                                   │  │
│  │  2. Data Quality Checks:                                                     │  │
│  │     • Missing values                                                         │  │
│  │     • Duplicates                                                              │  │
│  │     • Schema validation                                                      │  │
│  │  3. Data Cleaning:                                                           │  │
│  │     • Remove nulls in critical columns                                       │  │
│  │     • Remove duplicates                                                      │  │
│  │     • Handle data types                                                      │  │
│  │  4. Star Schema Joins:                                                       │  │
│  │     • Fact: watch_history                                                    │  │
│  │     • Dimensions: users, movies, reviews                                    │  │
│  │  5. Data Transformation:                                                    │  │
│  │     • Parse timestamps                                                       │  │
│  │     • Extract year/month                                                     │  │
│  │  6. Monthly Aggregations:                                                    │  │
│  │     • monthly_engagement: watch time per country/plan/month                  │  │
│  │     • cohort_retention: user retention by cohort                             │  │
│  │     • content_performance: ratings per genre/month                           │  │
│  │     • genre_performance: overall genre stats                                  │  │
│  │     • monthly_active_users: MAU over time                                    │  │
│  │  7. Write Cleaned Tables:                                                    │  │
│  │     • Users, Movies, WatchHistory, Reviews, etc.                             │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  Temporary GCS Bucket                                                        │  │
│  │  • netflix-group5-temp                                                        │  │
│  │  • Used for BigQuery intermediate storage                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Google BigQuery    │
                    │                     │
                    │  Dataset:          │
                    │  netflix_processed  │
                    │                     │
                    │  Cleaned Tables:   │
                    │  • Users           │
                    │  • Movies          │
                    │  • WatchHistory    │
                    │  • Reviews         │
                    │  • SearchLogs      │
                    │  • Recommendation  │
                    │    Logs            │
                    │                     │
                    │  Aggregated Tables:│
                    │  • monthly_        │
                    │    engagement      │
                    │  • cohort_         │
                    │    retention       │
                    │  • content_        │
                    │    performance     │
                    │  • genre_          │
                    │    performance     │
                    │  • monthly_active_ │
                    │    users           │
                    └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    SERVING LAYER                                        │
│                              Unified Data Warehouse                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │      Google BigQuery                │
                    │                                     │
                    │  ┌───────────────────────────────┐  │
                    │  │  netflix_streaming            │  │
                    │  │  (Speed Layer Output)         │  │
                    │  │                               │  │
                    │  │  • engagement_health_realtime  │  │
                    │  │    - 5-min windows            │  │
                    │  │    - Real-time metrics        │  │
                    │  │    - Churn signals            │  │
                    │  └───────────────────────────────┘  │
                    │                                     │
                    │  ┌───────────────────────────────┐  │
                    │  │  netflix_processed              │  │
                    │  │  (Batch Layer Output)           │  │
                    │  │                               │  │
                    │  │  Cleaned Tables:                │  │
                    │  │  • Users, Movies, WatchHistory  │  │
                    │  │                                 │  │
                    │  │  Aggregated Tables:             │  │
                    │  │  • monthly_engagement           │  │
                    │  │  • cohort_retention             │  │
                    │  │  • content_performance           │  │
                    │  │  • genre_performance             │  │
                    │  │  • monthly_active_users           │  │
                    │  └───────────────────────────────┘  │
                    └─────────────────────────────────────┘
                              │
                              │ (BigQuery Connector)
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              VISUALIZATION LAYER                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │      Looker Studio                  │
                    │      (Google Data Studio)            │
                    │                                     │
                    │  ┌───────────────────────────────┐  │
                    │  │  Dashboard 1:                  │  │
                    │  │  Real-Time Engagement          │  │
                    │  │                               │  │
                    │  │  Data Source:                  │  │
                    │  │  engagement_health_realtime    │  │
                    │  │                               │  │
                    │  │  Metrics:                     │  │
                    │  │  • Active users per 5-min     │  │
                    │  │  • Churn risk by segment       │  │
                    │  │  • Alert levels (HIGH/MED/LOW) │  │
                    │  │  • Engagement rates            │  │
                    │  │  • Revenue impact               │  │
                    │  │  • Top genres/countries         │  │
                    │  └───────────────────────────────┘  │
                    │                                     │
                    │  ┌───────────────────────────────┐  │
                    │  │  Dashboard 2:                  │  │
                    │  │  Historical Trends             │  │
                    │  │                               │  │
                    │  │  Data Sources:                 │  │
                    │  │  • monthly_engagement          │  │
                    │  │  • cohort_retention            │  │
                    │  │  • content_performance         │  │
                    │  │  • genre_performance           │  │
                    │  │  • monthly_active_users        │  │
                    │  │                               │  │
                    │  │  Metrics:                     │  │
                    │  │  • MAU per plan and country    │  │
                    │  │  • Retention curves            │  │
                    │  │  • Churn analysis              │  │
                    │  │  • Genre performance over time   │  │
                    │  │  • Watch duration trends        │  │
                    │  │  • Content ratings by genre     │  │
                    │  └───────────────────────────────┘  │
                    └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW SUMMARY                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

SPEED LAYER (Real-Time):
  Raw Data → Kafka Producer → Kafka Topic → Spark Streaming → BigQuery (realtime) → Dashboard 1
  Processing Time: 5-minute windows, 10-second triggers
  Latency: Near real-time (< 1 minute)

BATCH LAYER (Historical):
  Raw Data (GCS) → Spark Batch → BigQuery (processed) → Dashboard 2
  Processing Time: Monthly aggregations
  Latency: Daily/hourly batch runs

SERVING LAYER:
  Both layers converge in BigQuery
  Unified query interface for dashboards
  Historical accuracy + Real-time insights

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              KEY TECHNOLOGIES                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘

• Container Orchestration: Docker Compose
• Stream Processing: Apache Kafka + Zookeeper
• Data Processing: Apache Spark (Structured Streaming + Batch)
• Cloud Storage: Google Cloud Storage (GCS)
• Data Warehouse: Google BigQuery
• Visualization: Looker Studio (Google Data Studio)
• Development: Jupyter Notebooks
• Language: Python (PySpark)

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ARCHITECTURE BENEFITS                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

✓ Lambda Architecture: Combines real-time (speed) and batch (accuracy) processing
✓ Fault Tolerance: Spark checkpoints, Kafka message persistence
✓ Scalability: Distributed Spark cluster, Kafka partitions
✓ Flexibility: Separate pipelines for different use cases
✓ Unified Serving: BigQuery as single source of truth
✓ Real-time Monitoring: Operational dashboards with low latency
✓ Historical Analysis: Accurate batch processing for trends

