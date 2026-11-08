# Replication And Recovery: Exercises

[Notes](22-replication-recovery.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 operational/diagnostic tasks, and 2 interview questions. Keep this at application-level awareness. No replica configuration or destructive restore is performed here.

## 1. Read Immediately After A Write

An API creates an order on the primary and immediately fetches it from a possibly lagging replica. What can happen and what is safer?

**Expected result:** The replica may not have applied the write; read from primary or use a consistency mechanism.

<details><summary>Show answer</summary>

The read can return no order or stale state because asynchronous replication may lag. Route read-after-write to the primary or use a proven replication-position/session consistency strategy.
</details>

## 2. Choose A Replica Read

A product catalog can tolerate a short freshness delay. What is a reasonable read-routing approach and caveat?

**Expected result:** Read from a healthy replica while monitoring lag and preserving a primary fallback or policy.

<details><summary>Show answer</summary>

Route suitable catalog reads to a healthy replica and define an acceptable staleness window. Monitor lag and route critical freshness reads to the primary; a replica does not guarantee current data.
</details>

## 3. Recover An Accidental Delete

A row was deleted at 10:15. The team has a 02:00 backup and binary logs through 10:30. Give a high-level safe recovery path.

**Expected result:** Restore backup separately, replay logs to just before the delete, then extract/repair under review.

<details><summary>Show answer</summary>

Restore the backup to an isolated server, replay binary logs to a point just before 10:15, validate the row, then plan a reviewed extraction/repair. Do not overwrite production blindly.
</details>

## 4. Distinguish Replica From Backup

Why can a replica not replace a historical backup?

**Expected result:** It copies accidental deletes/corruption and does not inherently preserve prior states.

<details><summary>Show answer</summary>

Replication copies source changes, including erroneous updates or deletes. A backup and retained logs provide historical recovery points; a replica mainly supports availability/read scaling.
</details>

## 5. Design A Read-After-Write Flow

A user updates their profile and must immediately see the new value. Where should the immediate read go?

**Expected result:** Read from the primary or use a validated consistency token/position approach.

<details><summary>Show answer</summary>

Read from the primary for the immediate confirmation, or use a tested consistency mechanism that waits until the selected replica has applied the relevant transaction. Do not assume replica lag is zero.
</details>

## 6. Plan A Failover

A primary becomes unavailable. Name important checks before promoting a replica and routing writes.

**Expected result:** Check applied position/lag, prevent dual writers, promote deliberately, and update routing/monitoring.

<details><summary>Show answer</summary>

Evaluate which transactions the candidate replica applied, prevent the old primary from accepting writes, promote one writer, update clients/routing, and verify data/health. Failover needs a documented recovery and fencing process.
</details>

## 7. Explain Binary Logs In Recovery

What do binary logs contribute to point-in-time recovery after restoring a backup?

**Expected result:** They allow replaying changes after the backup to a selected time/transaction boundary.

<details><summary>Show answer</summary>

When retained and correctly configured, binary logs record changes after a backup and can be replayed to a point before an error. Verify retention, backup coordinates, and restore procedure.
</details>

## 8. Check Backup Readiness

A team has nightly backup files but has never restored one. What is unverified?

**Expected result:** Integrity/usability, restore time, and achievable recovery objectives.

<details><summary>Show answer</summary>

A successful backup job does not prove a usable restore. Perform periodic isolated restore tests and measure recovery time and recovery point against the business objectives.
</details>

## 9. Debug A Stale Read

A replica shows an old order status though the primary update succeeded. Give a likely cause and application behavior.

**Expected result:** Replication lag; retry/read from primary according to consistency needs, not blindly overwrite.

<details><summary>Show answer</summary>

The replica may not yet have applied the transaction. For a freshness-critical path, read from primary or wait using a supported consistency signal; avoid interpreting the stale read as failed write and repeating a non-idempotent action.
</details>

## 10. Identify GTID Purpose

At a high level, what does a GTID identify?

**Expected result:** A transaction across replication, helping replication position/topology management.

<details><summary>Show answer</summary>

A GTID uniquely identifies a committed transaction in a replication topology and helps replicas track which transactions were applied. Detailed configuration is an operational topic.
</details>

## 11. Interview: Replication Versus Backup

Explain why a replica is not a backup.

**Expected result:** Replicas reproduce current changes; backups retain recoverable historical states.

<details><summary>Show answer</summary>

A replica applies the source's changes and can reproduce mistakes or corruption. A backup plus retained logs provides a historical recovery point; restore tests verify that it works.
</details>

## 12. Interview: Replication Lag

Define replication lag and one user-facing impact.

**Expected result:** Replica apply delay and stale/missing read-after-write results.

<details><summary>Show answer</summary>

Replication lag is the delay between a source transaction and its application on a replica. A read routed to that replica can miss a just-written row or show an older value, so the application needs a freshness policy.
</details>
