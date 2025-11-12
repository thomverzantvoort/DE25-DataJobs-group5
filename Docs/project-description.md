## Netflix User Intelligence – Data Engineering Project

Overview This project is developed for the JADS Data Engineering course (Assignment 2). The goal is to design and implement a Big Data Architecture and two Spark data processing pipelines that generate both real-time and historical insights into user behavior on a streaming platform. The project is based on the Netflix 2025 User Behavior Dataset from Kaggle, which contains user activity, subscription, and content data.

## Dataset Description 
The project uses the following datasets from the Netflix 2025 User Behavior collection on Kaggle:

users.csv contains user account and demographic attributes such as user identifier, country, device type, and plan.
movies.csv contains catalog metadata such as show or movie identifier, title, genre, release year, and duration.
watch_history.csv contains granular viewing events per user with timestamps, play duration, completion percentage, and event type such as play, pause, or stop
reviews.csv contains user generated ratings or textual reviews per movie.
search_logs.csv contains user search events with timestamp, query text, and optional clicked item.
recommendation_logs.csv contains recommendation delivery or click events showing which items were recommended and whether a user interacted.

The dataset follows a star schema where watch_history.csv acts as the fact table and all other files act as dimension tables. This structure enables joining and aggregating data efficiently during processing.

## Project Description
**Goals**
● Design and implement data architectures and data processing pipelines using Apache
Spark and GCP services.

**Skills Required**
● Ability to create, configure, and use a data architecture in the GCP
● Ability to create, deploy, and execute batch and stream data processing jobs with Apache Spark

**Assignment Constraints**
● The data architecture (of a data infrastructure) must be based on recognized data
architectures such as Microsoft Big Data Architecture (one used in the labs), Lambda,
Kappa, and Data Warehouse.
● The data architecture must be implemented with the most appropriate tools, such as
Spark, BigQuery, Google Cloud Storage, and Kafka.
● Two separate data pipelines should be implemented. The pipelines can be batch
processing and/or data stream processing pipelines. Each pipeline will be a Spark
program/job.
○ 2 batch or
○ 2 stream or
○ 1 batch and 1 stream
● The students cannot use the datasets used in the labs.
● The students need to develop their own Spark programs. The students cannot use the
complete Spark programs from the articles or GitHub as-is. For example, the students
cannot simply copy and use a Spark program implemented for a specific use case.
● The data pipelines should implement a sufficient number of data processing steps (see
the examples given later for the level of complexity expected). Machine learning is not
the focus of this assignment. While the students can use machine learning in their
pipelines, simply training models and making predictions is insufficient. For example,
there should be reasonably complex data preprocessing where data pipelines are
used. The students are encouraged to focus on batch and stream data processing use
cases.
○ An assignment report from the previous batch can be found in Canvas (Modules
>> Assignments). You can check it to get an idea about the assignment.
