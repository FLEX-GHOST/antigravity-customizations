---
name: sql-query-optimization-internals
description: Definitive guide for relational database engineering, EXPLAIN ANALYZE interpretation, B-Tree/BRIN/GIN indexing, partitioning, and transaction isolation levels.
language: database
category: programming-languages
quality_score: 100
tier: official
triggers:
  - sql
  - postgresql
  - postgres
  - indexing
  - explain analyze
  - b-tree
  - query optimization
  - database
---
# SQL Query Optimization, PostgreSQL Internals & High-Throughput Indexing

Production engineering principles for high-performance relational databases and SQL execution.

## 1. Execution Plan Mastery (EXPLAIN ANALYZE)
* **Never Trust Naked SQL**: Run `EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)` on any query touching >10,000 rows.
* **Eliminate Sequential Scans**: Replace sequential table scans on filtered queries with targeted B-Tree composite indices covering all `WHERE` and `ORDER BY` predicates.

## 2. Index Design Discipline
* **Leftmost Prefix Rule**: In composite indices `(tenant_id, status, created_at)`, queries must filter by `tenant_id` to leverage the index.
* **Partial Indices for Status Filtering**: Use partial indices on sparse state columns to drastically shrink index size.
  ```sql
  CREATE INDEX idx_orders_unprocessed 
  ON orders (created_at) 
  WHERE status IN ('pending', 'processing');
  ```
* **Covering Indices (`INCLUDE`)**: Include non-key columns in index leaves to achieve Index-Only Scans without reading the heap table.
