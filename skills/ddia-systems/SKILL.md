---
name: ddia-systems
description: 'Design and evaluate distributed, data-intensive systems based on Martin Kleppmann’s Designing Data-Intensive Applications (DDIA). Covers storage engine architectures (LSM-trees vs B-Trees), replication topologies, partitioning strategies, transaction isolation levels, distributed consensus (Raft/Paxos), and stream processing.'
license: MIT
metadata:
  author: wondelai
  version: "2.0.0"
---

# Designing Data-Intensive Applications (DDIA) Systems Engineering Guide

A comprehensive architectural standard for building resilient, scalable, and correct distributed data systems. Based on Martin Kleppmann's *Designing Data-Intensive Applications*.

---

## 1. The Three Pillars of Data Systems

- **Reliability**: The system continues to function correctly (at desired performance levels) even in the face of hardware faults, software bugs, and human error.
- **Scalability**: The system's ability to cope with increased load (data volume, traffic volume, or complexity) by adding resources. Always measure with **percentiles** ($P_{50}$, $P_{95}$, $P_{99}$, $P_{99.9}$) rather than deceptive averages.
- **Maintainability**: Operability (easy for ops to keep running), Simplicity (managing accidental complexity via good abstractions), and Evolvability (easy for engineers to adapt to changing requirements).

---

## 2. Storage Engines: LSM-Trees vs B-Trees

All storage engines balance write performance, read latency, and disk amplification:

### Comparison Matrix

| Dimension | Log-Structured (LSM-Tree + SSTables) | Page-Oriented (B-Tree) |
|---|---|---|
| **Underlying Structure** | Memtable (RAM) $\rightarrow$ Immutable SSTables on disk | Fixed-size disk pages (typically 4KB–8KB) |
| **Write Pattern** | Sequential appends to WAL + in-memory sort | In-place random page rewrites |
| **Write Performance** | **High throughput** (sequential disk I/O) | Moderate (random I/O, write amplification) |
| **Read Performance** | Slower (checks memtable, bloom filters, SSTable levels) | **Fast & predictable** (fixed tree depth, $O(\log N)$) |
| **Space Overhead** | Lower fragmentation, periodic compaction | Fragmented pages due to splits |
| **Representative DBs** | RocksDB, LevelDB, Cassandra, InfluxDB | PostgreSQL, MySQL (InnoDB), SQLite |

### OLTP vs OLAP Storage Architectures
- **OLTP (Row-Oriented)**: Stores entire records consecutively on disk. Optimized for random, low-latency lookups by primary key and small transactions.
- **OLAP (Column-Oriented)**: Stores each column separately across disk blocks. Enables massive compression (dictionary encoding, bit-packing) and sub-second analytical scans across millions of rows without loading unused attributes (ClickHouse, Parquet).

---

## 3. Replication Topologies & Consistency Guarantees

Replication provides fault tolerance and scales read traffic across multiple nodes:

### Topologies

1. **Single-Leader Replication**:
   - All writes go to the primary node; followers consume a replication log.
   - Synchronous vs Asynchronous replication trade-off (durability vs write latency).
2. **Multi-Leader Replication**:
   - Multiple datacenters with local leaders.
   - Requires conflict resolution (Last-Write-Wins, CRDTs, or operational transformation).
3. **Leaderless Replication (Dynamo-Style)**:
   - Clients send reads/writes to multiple replicas directly.
   - Quorum condition for strong consistency: $w + r > n$ (where $w$ is write quorum, $r$ is read quorum, $n$ is replica count).

### Replication Anomalies & Guarantees
- **Read-After-Write (Read-Your-Writes) Consistency**: A user must always see updates they submitted themselves (e.g. read user's own profile from the leader).
- **Monotonic Reads**: If a user reads a particular value, they must never subsequently see an older version of that value (prevent time-travel anomalies by pinning a user to a specific follower replica).
- **Consistent Prefix Reads**: If a sequence of writes happens in a certain order, everyone must see them appear in that same order (prevent causality violations).

---

## 4. Partitioning (Sharding) Strategies

Partitioning divides large datasets into smaller subsets to scale beyond single-node limits:

1. **Partitioning by Key Range**:
   - Keys are sorted; partitions handle contiguous ranges.
   - Advantage: Range queries are efficient.
   - Disadvantage: Severe hot-spotting on sequential keys (e.g. timestamps).
2. **Partitioning by Hash of Key**:
   - A cryptographic hash (e.g. MurmurHash3) distributes keys uniformly across partitions.
   - Disadvantage: Range queries must be broadcast to all partitions (scatter/gather).
3. **Consistent Hashing**:
   - Uses a virtual token ring to minimize data movement when nodes join or leave the cluster.

---

## 5. Transactions & Isolation Levels

Transactions provide ACID abstractions to isolate application logic from concurrent race conditions:

### Concurrency Anomalies & Isolation Hierarchy

| Isolation Level | Dirty Reads Prevented? | Non-Repeatable Reads Prevented? | Lost Updates Prevented? | Write Skew Prevented? | Implementation Mechanism |
|---|---|---|---|---|---|
| **Read Uncommitted** | ❌ No | ❌ No | ❌ No | ❌ No | No read locks |
| **Read Committed** | ✅ Yes | ❌ No | ❌ No | ❌ No | Row-level read locks or MVCC |
| **Snapshot Isolation / Repeatable Read** | ✅ Yes | ✅ Yes | ✅ Yes (atomic) | ❌ No | **MVCC** (Multi-Version Concurrency Control) |
| **Serializable** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | 2PL (Two-Phase Locking) or SSI |

### Critical Race Conditions to Prevent
- **Lost Updates**: Two concurrent transactions read, modify, and write the same record, overwriting each other. *Remediation*: Atomic write operations (`UPDATE balance = balance + 10`), explicit pessimistic locks (`SELECT ... FOR UPDATE`), or compare-and-set.
- **Write Skew**: Two transactions read the same data, determine a business rule is satisfied, and write to *different* records, violating an invariant (e.g. two doctors concurrently booking off the same on-call shift). *Remediation*: Serializable isolation or explicit locking of the predicate range.

---

## 6. Distributed Consensus & Fault Tolerance

In distributed systems, networks drop packets, clocks drift, and nodes pause unexpectedly (GC pauses):

- **The Fallacy of Synchronous Clocks**: Never use wall-clock timestamps (`SystemTime::now()`) for strict causal ordering across nodes. Use **Logical Clocks** (Lamport timestamps) or **Vector Clocks** to track causality.
- **Distributed Consensus (Raft / Paxos)**:
  - Solves the problem of reaching agreement among nodes in an asynchronous network with crash faults.
  - Guarantees safety (never return an incorrect result) and liveness (as long as a majority of nodes are reachable).
- **Two-Phase Commit (2PC)**:
  - Atomic commitment across heterogeneous storage systems.
  - **Major Flaw**: A coordinator failure leaves participants blocked indefinitely in the prepared state. Prefer asynchronous event-driven sagas with compensating transactions.

---

## 7. Stream Processing & Batch Systems

- **Log-Based Message Brokers (Kafka / Redpanda)**:
  - Durably append events to disk partitions; multiple consumer groups read independently via committed offsets.
  - Backpressure is built-in: slow consumers fall behind without exhausting broker memory.
- **Idempotency & Exactly-Once Semantics**:
  - True physical "exactly-once" delivery across networks is mathematically impossible.
  - Combine **At-Least-Once Delivery** with **Idempotent Consumers** (deduplication keys, unique constraints in DB) to achieve effective exactly-once processing.
