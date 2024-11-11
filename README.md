---

# Django Celery Task Scheduling API

## Overview

This project provides a robust API built with Django for scheduling and managing asynchronous tasks using **Celery**. It allows users to schedule, monitor, cancel, and retry data processing tasks. The system uses **Celery** for asynchronous task management and **Redis** as the message broker.

## Key Features

- **Task Scheduling**: Schedule data processing tasks to be executed asynchronously.
- **Real-Time Task Status Updates**: Track task progress via WebSocket.
- **Cancel Tasks**: Cancel scheduled tasks before they are executed.
- **Retry Failed Tasks**: Automatically or manually retry failed tasks with exponential backoff.
- **Comprehensive API Endpoints**: Manage task lifecycle using simple REST API calls.

## Prerequisites

To run this project, you will need the following:

- **Python 3.8+**
- **Django 3.2+**
- **Celery 5.2+**
- **Redis Server** (as the message broker for Celery)

## Installation Steps

Follow the steps below to set up and run the project locally.

### 1. Clone the repository

First, clone the project repository:

```bash
git clone https://github.com/rohandass58/Celery_Project.git
cd Celery_Project
```

### 2. Set up a Virtual Environment

Create and activate a virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install the Dependencies

Install all required Python packages listed in the `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

Run migrations to set up the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

### 6. Start the Celery Worker

In a separate terminal, start the Celery worker to process background tasks:

```bash
celery -A Celery_Project worker -l info
```

### 7. Run the WebSocket Server

Use Daphne to run the WebSocket server for real-time task status updates:

```bash
daphne -p 8001 Celery_Project.asgi:application
```

---

## API Usage

### Task Creation

To create a new task, send a `POST` request to the `/api/tasks/` endpoint with the following JSON body:

```json
{
  "name": "Data Processing Task",
  "description": "Process some data in the background.",
  "scheduled_time": "2024-11-20T10:00:00Z"
}
```

### Monitor Task Status via WebSocket

You can monitor the real-time status of a task by connecting to the WebSocket endpoint:

```
ws://localhost:8001/ws/tasks/<task_id>/
```

### Cancel or Retry a Task

To cancel a scheduled task or retry a failed task, send a `POST` request to the corresponding endpoint:

- **Cancel Task**: `POST /api/tasks/<task_id>/cancel/`
- **Retry Task**: `POST /api/tasks/<task_id>/retry/`

### API Endpoints

- **Create Task**: `POST /api/tasks/`
- **Cancel Task**: `POST /api/tasks/<task_id>/cancel/`
- **Retry Task**: `POST /api/tasks/<task_id>/retry/`
- **Get Task Status**: `GET /api/tasks/<task_id>/status/`

---

## WebSocket Usage

### Task Status Updates

When the task status is updated (e.g., `COMPLETED`, `FAILED`), a message will be sent over the WebSocket connection in the following format:

```json
{
  "status": "COMPLETED",
  "result": {"message": "Data processed successfully"}
}
```

---

## Celery Configuration

Celery is optimized for performance using the following configuration parameters:

- **worker_prefetch_multiplier**: `1` — Prevents workers from pulling too many tasks at once.
- **worker_max_tasks_per_child**: `1000` — Automatically restarts workers after they process 1000 tasks to avoid memory leaks.
- **task_time_limit**: Specifies the hard time limit for tasks.
- **task_soft_time_limit**: Specifies the soft time limit for tasks, allowing for graceful termination.
- **worker_concurrency**: `4` — Number of worker processes to run concurrently.

---

## Conclusion

This Django Celery Task Scheduling API offers a comprehensive solution for managing background tasks. You can schedule, monitor, and manage tasks efficiently, using both REST APIs and real-time WebSocket updates. The system is designed to be scalable, efficient, and easy to integrate into any Django-based application.
