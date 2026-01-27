## 2026-01-27 - Missing Foreign Key Indexes in SQLAlchemy/Postgres
**Learning:** `db.ForeignKey` in SQLAlchemy does NOT create a database index automatically in PostgreSQL. This leads to full table scans when filtering by foreign keys.
**Action:** Always verify if FKs are indexed and manually add `db.Index` or `Index` in `__table_args__` for columns used in filters.
