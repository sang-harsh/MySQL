# Partitioning And Scaling Decisions

[Exercises](23-partitioning-scaling-exercises.md) | [Topic index](../start.md)

## Interview Answer

Scaling choices solve different bottlenecks: indexes improve access paths within a server, partitioning divides one logical table into manageable partitions on a server, replicas distribute reads, and sharding distributes data across servers. Caching can reduce repeated reads but introduces invalidation and staleness. I measure the bottleneck first and choose the least complex option that meets the workload and consistency needs.

## Key Points

- Partitioning can help manage very large tables or prune irrelevant partitions when queries filter on the partition key. It is not a substitute for a good index and does not automatically distribute data across servers.
- MySQL partitioning has restrictions. Every unique key, including the primary key, must include all columns used in the partitioning expression. Foreign-key interactions are restricted for partitioned InnoDB tables; verify current version support before designing around it.
- Sharding splits data across multiple MySQL instances, requiring application/routing decisions and making cross-shard joins/transactions more complex.
- Read replicas can scale suitable read workloads but are eventually consistent under common asynchronous configurations and add operational complexity.
- Caching helps repeated reads when data is reusable; define invalidation, TTL, and acceptable staleness. Cache invalidation bugs can become correctness bugs.
- OLTP systems optimize many small concurrent transactional operations; OLAP/reporting workloads scan and aggregate large datasets. Separate reporting infrastructure may be appropriate as scale grows.
- SQL versus NoSQL is a workload/data-model choice, not a general replacement decision. Relational transactions and constraints remain valuable for many application domains.
- Partitioning may complicate unique constraints, pruning, and query planning; use it only after measuring and validating the access pattern.

## Minimal Example

A large events table queried by month might use RANGE partitioning on a date expression, but this design must meet MySQL's unique-key rules and pruning behavior. A date index or archival strategy may be simpler. Verify EXPLAIN PARTITIONS and operational requirements before adopting partitioning.

## Common Traps

- Partitioning does not mean horizontal sharding across machines.
- More partitions do not guarantee faster queries; pruning depends on the query predicate and partition key.
- A read replica is not a cache or a backup; each solves a different problem.
- Adding a distributed cache without a freshness/invalidation plan can return stale business data.

## Likely Follow-Ups

**When use partitioning?** For measured table-management or pruning benefits with compatible keys and predicates.

**Partitioning versus sharding?** Partitioning divides a table within one MySQL server; sharding distributes data among servers and moves routing/consistency complexity to the system.

**When cache?** For repeatedly requested data where a defined freshness window is acceptable and invalidation can be implemented reliably.

## MySQL Reference

Examples target MySQL 8.4. Partitioning capabilities and restrictions are version-sensitive; see [partitioning overview](https://dev.mysql.com/doc/refman/8.4/en/partitioning-overview.html), [partitioning limitations](https://dev.mysql.com/doc/refman/8.4/en/partitioning-limitations.html), and [EXPLAIN partitions](https://dev.mysql.com/doc/refman/8.4/en/partitioning-info.html).
