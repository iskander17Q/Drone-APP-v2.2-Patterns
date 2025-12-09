# Pipeline Architecture Overview

## Scope
**Domain flow:** Imagery uploads → automated analysis → Heatmap/Report generation → report distribution. All services avoid flight/mission terminology and only focus on imagery artifacts.

## Shared Concepts
- **Imagery**: Uploaded source imagery batches stored in MinIO. Metadata tracked in Postgres.
- **AnalysisRun**: Processing jobs triggered per Imagery batch. Includes status, Celery/Rabbit routing keys, progress metrics.
- **Heatmap**: Geo-referenced raster generated from vegetation index/thermal analysis stored in MinIO.
- **Report**: Aggregated outputs (PDF/JSON) referencing Heatmaps and summary statistics.

## Monolithic Stack (`monolith/`)
- **Flask API**
  - Endpoints: `/imagery`, `/analysis-runs`, `/reports`.
  - Uses SQLAlchemy for Postgres models: Imagery, AnalysisRun, Heatmap, Report.
  - Handles uploads directly to MinIO via presigned URLs.
- **Celery Workers**
  - Task queue via Redis.
  - Tasks: `ingest_imagery`, `run_analysis`, `generate_report`.
  - Access shared `image_processing` utilities.
- **Postgres**
  - Single schema `imagery_pipeline`.
- **MinIO**
  - Buckets: `imagery-uploads`, `analysis-heatmaps`, `reports`.
- **Docker Compose**
  - Services: `web`, `worker`, `beat`, `redis`, `postgres`, `minio`, `createbuckets`.
- **Workflow**
  1. Flask receives Imagery upload request, stores metadata, returns upload URL.
  2. Upload completion triggers Celery `run_analysis`.
  3. Worker downloads from MinIO, runs analysis, stores Heatmap and analysis metrics.
  4. `generate_report` task aggregates data and stores Report PDFs/JSON in MinIO, updates Postgres.

## Microservices Stack (`microservices/`)
- **Services**
  - `ingestion`: FastAPI service handling Imagery uploads, storing metadata, and publishing jobs to RabbitMQ (`imagery.uploaded`).
  - `processing`: FastAPI service running AnalysisRun orchestration. Consumes RabbitMQ messages, performs analysis, persists Heatmaps, and emits `analysis.completed`.
  - `report`: FastAPI service generating Report assets upon `analysis.completed`.
  - `api-gateway`: FastAPI/ASGI app exposing unified REST interface `/imagery`, `/analysis-runs`, `/reports`, proxying to internal services.
- **Infrastructure**
  - Message broker: RabbitMQ with exchanges `imagery` and `analysis`.
  - Database: Shared Postgres schema with service-specific role accounts.
  - Object storage: MinIO buckets same as monolith.
  - Shared `libs/` package for models and schemas (pydantic + SQLAlchemy models).
- **Docker Compose**
  - Services: `gateway`, `ingestion`, `processing`, `report`, `rabbitmq`, `postgres`, `minio`, `createbuckets`.
- **Workflow**
  1. Gateway obtains upload URL from `ingestion` service and records Imagery row.
  2. `ingestion` emits message when upload finalizes.
  3. `processing` consumes message, runs analysis tasks, writes Heatmap artifacts to MinIO, updates AnalysisRun + Heatmap tables, then publishes completion event.
  4. `report` service listens for completion, composes Report in MinIO and updates Postgres.

## Next Steps
1. Scaffold `monolith/` project with Flask app, Celery config, Docker artifacts.
2. Scaffold `microservices/` project with shared libs, FastAPI services, messaging setup.
3. Provide setup instructions and developer docs.
