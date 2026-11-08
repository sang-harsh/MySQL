# Replication And Recovery

[Exercises](22-replication-recovery-exercises.md) | [Topic index](../start.md)

## Interview Answer

MySQL replication copies changes from a source to one or more replicas, commonly to scale reads or support availability. Replication is asynchronous by default, so a replica can lag and return stale data; it is not a backup. I keep critical read-after-write queries on the primary or use a consistency strategy, and rely on tested backups plus restore procedures for recovery.

## Key Points

- The source records changes in its binary log; replicas retrieve and apply them. Topology and configuration determine whether replication is asynchronous, semisynchronous, or group-based.
- Asynchronous replication can lag because of network, workload, or apply capacity. A successful primary write does not mean every replica has applied it.
- Read/write splitting can direct writes to the primary and some reads to replicas, but the application must identify reads that require fresh data.
- A replica helps availability/read scale but may copy accidental deletes, corruption, or bad application writes. It is not an independent historical backup.
- Backups provide a recovery point; point-in-time recovery combines a backup with subsequent binary logs, when configured and retained.
- Restore tests prove that backups are usable and that recovery time/point objectives are achievable. A backup that has never been restored is unverified.
- GTIDs identify transactions across replication and simplify some topology changes; recognize the purpose without needing to administer failover as an application developer.
- Failover must account for replication position, data consistency, client routing, and preventing two writable primaries.

## Minimal Example

A read-after-write flow can write an order to the primary, then read its confirmation from the same primary to avoid replica lag. Later independent catalog/reporting reads may use a replica if the product accepts its freshness window. This is an application consistency decision, not a guarantee provided by a SELECT statement.

## Common Traps

- “We have a replica” does not mean “we have a backup.” Replicas reproduce source changes, including unwanted ones.
- A replica read immediately after a write may not see that write. Avoid relying on vague “eventual consistency” without defining acceptable delay.
- Replication lag is not always a fixed duration; monitor it and handle degraded replicas.
- Failover without fencing/routing discipline can create split-brain writes or inconsistent reads.

## Likely Follow-Ups

**Why use a replica?** Read scaling, geographic locality, or availability, with lag and operations trade-offs.

**How recover a deleted row?** Restore a backup to a separate environment and replay logs to a point before deletion, then extract/repair the data under a reviewed plan.

**What is GTID?** A global transaction identifier used to track replicated transactions and simplify positioning/topology management.

## MySQL Reference

Examples target MySQL 8.4. See [replication](https://dev.mysql.com/doc/refman/8.4/en/replication.html), [binary log](https://dev.mysql.com/doc/refman/8.4/en/binary-log.html), and [backup and recovery](https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html).
