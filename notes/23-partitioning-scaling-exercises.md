# Partitioning And Scaling Decisions: Exercises

[Notes](23-partitioning-scaling.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 design/diagnostic tasks, and 2 interview questions. Keep partitioning and scaling answers at application-developer level. Verify MySQL 8.4 limitations before applying partition DDL.

## 1. Improve A Date-Filtered Event Table

A large event table is queried by date and has no supporting index. What should be evaluated before partitioning?

**Expected result:** Measure query plan and consider an index/range filter first; partition only for measured pruning/management needs.

<details><summary>Show answer</summary>

Inspect query predicates, data volume, and EXPLAIN. A date index or archival policy may solve the problem with less complexity. Partitioning is useful only if the workload can prune partitions or management benefits justify its restrictions.
</details>

## 2. Scale Read-Heavy Catalog Queries

The primary is CPU-bound on independent catalog reads; brief staleness is acceptable. Suggest an option and caveat.

**Expected result:** A read replica can distribute eligible reads but may lag and requires monitoring/routing.

<details><summary>Show answer</summary>

Route suitable reads to a replica, monitor lag, and keep read-after-write/freshness-critical requests on the primary or behind a consistency mechanism. A replica adds operational complexity and is not a backup.
</details>

## 3. Scale Writes Beyond One Server

A single primary cannot meet write throughput even after query/index improvements. What does sharding add and cost?

**Expected result:** Data is distributed across servers; routing and cross-shard operations become more complex.

<details><summary>Show answer</summary>

Sharding distributes records across multiple servers and can add write capacity, but requires shard-key/routing design, rebalancing, and more complex cross-shard queries and transactions. Measure and exhaust simpler optimizations first.
</details>

## 4. Cache A Frequently Read Profile

A profile can be stale for up to 30 seconds. What must a cache design define?

**Expected result:** TTL/freshness, invalidation on writes, fallback, and failure behavior.

<details><summary>Show answer</summary>

Define a TTL/freshness target, update or invalidate on writes, handle cache misses/errors, and decide how stale values are served. Monitor hit rate and correctness; caching adds a second copy of state.
</details>

## 5. Separate Reporting From OLTP

A monthly report scans hundreds of millions of transactional rows and slows checkout. Suggest a direction.

**Expected result:** Separate or pre-aggregate analytical work; protect OLTP latency and freshness needs.

<details><summary>Show answer</summary>

Consider a reporting replica/warehouse or maintained summaries so large scans do not compete with checkout. Define refresh lag and reconciliation; do not assume a replica removes all resource contention.
</details>

## 6. Choose SQL Or NoSQL

A team proposes replacing every relational table with a document database for “scale.” What should guide the decision?

**Expected result:** Access patterns, relationships/constraints, transaction needs, scale evidence, and operational capability.

<details><summary>Show answer</summary>

Choose based on data model, query patterns, consistency/transaction requirements, scale bottleneck, and team operations. NoSQL is not a universal performance upgrade; relational constraints and transactions may better fit core order/payment data.
</details>

## 7. Identify Partition Pruning

A table is partitioned by month, and a query filters on a fixed month range. What can EXPLAIN PARTITIONS help inspect?

**Expected result:** Which partitions the optimizer expects to scan.

<details><summary>Show answer</summary>

```sql
EXPLAIN PARTITIONS SELECT event_id FROM events
WHERE event_date>='2026-03-01' AND event_date<'2026-04-01';
```
Check whether irrelevant partitions are pruned. Partitioning benefit depends on query predicate and version/definition.
</details>

## 8. Check Partition Key Constraints

A table is partitioned by `created_at`, but its primary key is only `event_id`. What MySQL rule must be reviewed?

**Expected result:** Every unique key must include all columns used by the partitioning expression.

<details><summary>Show answer</summary>

MySQL requires unique keys, including the primary key, to include all columns used by the partitioning expression. The schema may need a composite primary key or a different design; verify current engine/version restrictions.
</details>

## 9. Debug “Partitioning Is Sharding”

Why is this statement incorrect?

**Expected result:** Partitioning is within one logical MySQL server/table; sharding distributes data among servers.

<details><summary>Show answer</summary>

Partitioning divides a table into partitions managed by one MySQL server. Sharding distributes data across multiple server instances and requires routing and cross-shard coordination.
</details>

## 10. Identify A Cache Consistency Risk

An application updates the database but leaves a cached profile unchanged. What user-visible bug can occur and one mitigation?

**Expected result:** Stale profile; invalidate/update cache or use bounded TTL/versioning.

<details><summary>Show answer</summary>

Users may see old values until expiration. Invalidate or update the cache after a committed write and define a TTL fallback; use an outbox/event if reliable cross-system invalidation is required.
</details>

## 11. Interview: Scaling Options

Compare an index, partitioning, a read replica, and sharding in one sentence each.

**Expected result:** Distinguish local access path, one-server table management, read scale, and multi-server data distribution.

<details><summary>Show answer</summary>

An index speeds suitable access paths within a table. Partitioning divides one table on a server for pruning/management. A replica serves reads from a copied dataset with possible lag. Sharding distributes data across servers and adds routing/transaction complexity.
</details>

## 12. Interview: Cache Trade-Off

Why can a cache improve latency while making correctness harder?

**Expected result:** It avoids repeated reads but creates stale duplicated state requiring invalidation/freshness policy.

<details><summary>Show answer</summary>

A cache can serve repeated data quickly, but it duplicates state and may lag behind database updates. Define freshness, invalidation, expiration, and failure behavior so stale data does not violate business rules.
</details>
