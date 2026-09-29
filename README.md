# KQL Ops Library

Ready-to-run queries for the questions an Azure operations engineer asks every day: *is it down, why is it slow, who changed it, is it backed up, what's exposed, what's wasting money.*

Every query carries a header saying what it answers, where to run it, which tables it needs, and when to reach for it. CI rejects any query without one.

Two engines, one language:

- **Log Analytics** queries run against data your agents and diagnostic settings collect (heartbeats, performance counters, event logs, activity logs, backup jobs). Use them in the Logs blade, alert rules and workbooks.
- **Resource Graph** queries run against the live configuration of every resource in every subscription you can read. No agents, no ingestion cost, results in seconds. Use them in Resource Graph Explorer.

## How I use it during an alert

| Alert | Start with | Then |
|---|---|---|
| **Node Down** | `heartbeat-missing` | `vm-stopped-or-deleted` (was it a person?) → `unexpected-shutdowns` (was it a crash?) |
| **High CPU** | `high-cpu-sustained` (real or a blip?) | `low-memory` (paging looks like CPU) → `cpu-anomalies-14d` (unusual for *this* VM?) |
| **Hardware Status** | `disk-and-ntfs-errors` | `disk-latency` → `low-disk-space` |
| **Backup failed** | `failed-backup-jobs` (error code) | `backup-duration-trend` (overrunning the window?) |
| **"Something changed"** | `nsg-rule-changes` | `role-assignment-changes` → `failed-arm-operations` |
| **Agent unreachable** | `heartbeat-gaps-24h` (flapping?) | `agent-version-inventory` → `vms-without-monitoring-agent` |

## Index

<!-- index:start -->
| Area | Query | Run in | When to use |
|---|---|---|---|
| backup | [Backup jobs getting slower](log-analytics/backup/backup-duration-trend.kql) | Log Analytics | Backups that keep growing will eventually overrun their window. Catch it early. |
| backup | [Failed Azure Backup jobs](log-analytics/backup/failed-backup-jobs.kql) | Log Analytics | Morning check of last night's backups, with the error code needed for a support case. |
| change-audit | [Failed Azure operations by caller](log-analytics/change-audit/failed-arm-operations.kql) | Log Analytics | Pipeline or automation failing silently; or someone repeatedly hitting a policy deny. |
| change-audit | [Who changed NSG rules](log-analytics/change-audit/nsg-rule-changes.kql) | Log Analytics | Traffic suddenly blocked or opened. First question: did someone change a rule? |
| change-audit | [RBAC role assignments added or removed](log-analytics/change-audit/role-assignment-changes.kql) | Log Analytics | Access reviews, or checking who granted someone Owner. |
| change-audit | [VMs stopped, deallocated or deleted](log-analytics/change-audit/vm-stopped-or-deleted.kql) | Log Analytics | Node Down alert with no crash in the event log. Someone may have stopped it. |
| linux | [Processes killed by the OOM killer](log-analytics/linux/oom-killer.kql) | Log Analytics | A Linux service keeps restarting with no application error. The kernel killed it for memory. |
| linux | [Failed SSH logins](log-analytics/linux/ssh-failed-logins.kql) | Log Analytics | Detect SSH brute force, or confirm a user's key/password problem. |
| linux | [Syslog errors by host and process](log-analytics/linux/syslog-errors.kql) | Log Analytics | Linux equivalent of scanning the System event log. Find the noisy process first. |
| performance | [CPU anomalies against each VM's own baseline](log-analytics/performance/cpu-anomalies-14d.kql) | Log Analytics | Finds machines behaving unusually for themselves, where a flat 90% threshold would never fire (a VM that normally sits at 5% now at 60%). |
| performance | [Slow disks (Windows)](log-analytics/performance/disk-latency.kql) | Log Analytics | Application is slow but CPU and memory look fine. Often it is storage throttling. |
| performance | [Sustained high CPU](log-analytics/performance/high-cpu-sustained.kql) | Log Analytics | Triage for a High CPU alert: confirms whether the spike is sustained or a one-off. |
| performance | [Volumes under 10% free](log-analytics/performance/low-disk-space.kql) | Log Analytics | Daily check. A full disk stops databases, logging and backups. |
| performance | [Low memory (Windows and Linux)](log-analytics/performance/low-memory.kql) | Log Analytics | Memory pressure causes slowness that looks like a CPU or app problem. Check this alongside High CPU alerts. |
| performance | [Top 10 busiest machines right now](log-analytics/performance/top-cpu-now.kql) | Log Analytics | Quick look during an incident when many alerts fire at once. |
| vm-health | [Monitoring agent versions](log-analytics/vm-health/agent-version-inventory.kql) | Log Analytics | Before an agent upgrade, or when one machine behaves differently from the rest. |
| vm-health | [Availability % per VM from heartbeats](log-analytics/vm-health/availability-7d.kql) | Log Analytics | Monthly SLA reporting, or proving a VM was actually up during an incident window. |
| vm-health | [Heartbeat gaps (flapping machines)](log-analytics/vm-health/heartbeat-gaps-24h.kql) | Log Analytics | A VM that is up now but dropped out several times today. Catches flaky network or agent restarts that a point-in-time check misses. |
| vm-health | [VMs that stopped sending heartbeats](log-analytics/vm-health/heartbeat-missing.kql) | Log Analytics | First query for a Node Down alert. Tells you which machines went silent and when. |
| windows-events | [Disk and file-system errors](log-analytics/windows-events/disk-and-ntfs-errors.kql) | Log Analytics | Pairs with Hardware Status alerts. Early warning before a disk fails outright. |
| windows-events | [Brute-force logon attempts](log-analytics/windows-events/failed-logons.kql) | Log Analytics | Spike in failed logons against one machine, or one IP trying many accounts. |
| windows-events | [Windows services that crashed](log-analytics/windows-events/service-crashes.kql) | Log Analytics | App down but the VM is up. Shows which service died and how often. |
| windows-events | [Unexpected shutdowns and reboots](log-analytics/windows-events/unexpected-shutdowns.kql) | Log Analytics | After a Node Down alert clears: was it a crash, a power event, or a planned restart? |
| cost | [Deallocated VMs still paying for disks](resource-graph/cost/deallocated-vms.kql) | Resource Graph | A deallocated VM stops compute billing but its disks keep costing money. Candidates to snapshot and delete. |
| cost | [Public IPs not attached to anything](resource-graph/cost/orphaned-public-ips.kql) | Resource Graph | Standard SKU public IPs bill even when unused. |
| cost | [Unattached managed disks](resource-graph/cost/unattached-disks.kql) | Resource Graph | Monthly cost cleanup. Unattached disks bill in full. |
| dr | [Site Recovery replication health](resource-graph/dr/asr-replication-health.kql) | Resource Graph | Before a DR drill, or when ASR sync alerts fire. Shows RPO and when DR was last proven. |
| dr | [VMs with no Azure Backup](resource-graph/dr/vms-without-backup.kql) | Resource Graph | Backup coverage check across every subscription at once. |
| inventory | [VM power state across subscriptions](resource-graph/inventory/vm-power-state.kql) | Resource Graph | How many VMs are running vs deallocated, across every subscription, in seconds. |
| inventory | [VM count by size and OS](resource-graph/inventory/vm-size-and-os.kql) | Resource Graph | Capacity planning, reservation purchases, or checking for sizes about to be retired. |
| inventory | [VMs with no Azure Monitor Agent](resource-graph/inventory/vms-without-monitoring-agent.kql) | Resource Graph | A VM without an agent never alerts. Find monitoring blind spots before an outage does. |
| security | [NSG rules exposing SSH/RDP to the internet](resource-graph/security/nsg-open-management-ports.kql) | Resource Graph | Security review. Any hit here is a finding. |
| security | [Public IPs and what they are attached to](resource-graph/security/public-ip-inventory.kql) | Resource Graph | Know your internet-facing surface. Anything unexpected here is a question for its owner. |
| security | [Storage accounts allowing public blob access](resource-graph/security/storage-public-blob-access.kql) | Resource Graph | Common data-leak cause. Should normally return nothing. |
<!-- index:end -->

## Header format

```kql
// Title: Sustained high CPU
// Source: Log Analytics            <- or Resource Graph
// Tables: Perf
// When to use: Triage for a High CPU alert
// Tune: 90% over 15-minute bins    <- optional: the thresholds you'll want to change
```

## Contributing a query

1. Put it in the right folder under `log-analytics/` or `resource-graph/`.
2. Add the header.
3. Run `python3 tools/check_queries.py` and `python3 tools/build_index.py`.

## Notes on data sources

- **Perf** queries assume performance counters are collected by a data collection rule. If you use VM insights instead, the same metrics live in `InsightsMetrics`.
- **Backup** queries need the Recovery Services vault diagnostic setting sending `CoreAzureBackup` and `AddonAzureBackupJobs` in resource-specific mode.
- **SecurityEvent** needs Defender for Cloud or Microsoft Sentinel collecting Windows security events.
- Thresholds are starting points. Every estate has its own normal; tune them against a week of your own data before alerting on them.
