## 2026-01-27 - Missing Foreign Key Indexes in SQLAlchemy/Postgres
**Learning:** `db.ForeignKey` in SQLAlchemy does NOT create a database index automatically in PostgreSQL. This leads to full table scans when filtering by foreign keys.
**Action:** Always verify if FKs are indexed and manually add `db.Index` or `Index` in `__table_args__` for columns used in filters.

## 2025-05-23 - Offloading CPU-bound tasks in Flask
**Learning:** In a synchronous Flask app (threaded workers), CPU-bound tasks like image generation block the GIL, starving other threads. Offloading to `ProcessPoolExecutor` releases the GIL.
**Action:** Use `ProcessPoolExecutor(max_workers=1)` as a context manager for heavy CPU tasks. Avoid module-level global executors to prevent resource exhaustion and fork-safety issues in pre-fork servers.
