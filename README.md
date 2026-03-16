# FRRUAS Prototype — CLI Application

Command-line prototype for the **Faculty Resource Reservation and Usage Analytics System (FRRUAS)**.

A database course project (Databases 2025/2026 Winter) at FINKI, under the supervision of Prof. Dr. Vangel V. Ajanovski. This prototype connects to a PostgreSQL database and demonstrates six use cases through an interactive terminal interface.

## Use Cases

| UC | Name | Role |
|----|------|------|
| UC0001 | Browse Available Resources | All |
| UC0002 | Make a Resource Reservation | Teaching Staff |
| UC0003 | Approve or Reject Reservations | Administrator |
| UC0007 | View Resource Usage Analytics | Administrator |
| UC0008 | Log In to the System | All |
| UC0009 | Register a New User | Administrator |

## Prerequisites

- Python 3.10+
- Docker & Docker Compose (for PostgreSQL)

## Setup

### 1. Start the Database

```bash
cd docker
docker compose up -d
```

This starts a PostgreSQL 16 container (`frruas_db`) on port 5432.

### 2. Load Schema and Seed Data

```bash
docker exec -i frruas_db psql -U frruas_user -d frruas_db < database/ddl/schema_creation.sql
docker exec -i frruas_db psql -U frruas_user -d frruas_db < database/dml/data_load.sql
```

### 3. Set Up the Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run

```bash
python main.py
```

## Test Credentials

All seed users share the password `password123`.

| Role | Email |
|------|-------|
| Administrator | ana.petrovska@finki.ukim.mk |
| Administrator | marko.dimitrovski@finki.ukim.mk |
| Teaching Staff | elena.stojanova@finki.ukim.mk |
| Teaching Staff | nikola.trajkovski@finki.ukim.mk |
| Student | stefan.nikolov@students.finki.ukim.mk |
| Student | martina.ilievska@students.finki.ukim.mk |

## Project Structure

| File | Description |
|------|-------------|
| `main.py` | Entry point: login with email/password, role-based main menu |
| `db.py` | Database connection helper and shared UI utilities |
| `uc_browse.py` | UC0001: Browse Available Resources |
| `uc_reserve.py` | UC0002: Make a Resource Reservation |
| `uc_approve.py` | UC0003: Approve or Reject Reservations |
| `uc_analytics.py` | UC0007: View Resource Usage Analytics |
| `uc_users.py` | UC0009: Register a New User |
| `docker/` | Docker Compose configuration for PostgreSQL |
| `database/` | SQL scripts for schema creation and seed data |

## Technology

- **psycopg2** — PostgreSQL adapter
- **bcrypt** — password hashing
