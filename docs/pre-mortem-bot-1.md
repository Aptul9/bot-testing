# Pre-Mortem - BOT-1 DoS run

Mandatory before each `--no-dry-run` execution of BOT-1 against `api-coll.museiitaliani.it`. Format from `08_advanced_safety_time_and_pipelines.md` § 2.

This document is a template. Copy it, fill in for the specific run, get user sign-off, then execute.

---

## Run identification

- Date / time window planned: _YYYY-MM-DD HH:MM - HH:MM (Europe/Rome)_
- Operator: _name_
- Approver: _name_
- Region: _e.g. nl-ams_
- Fleet: _2 x g6-standard-1 + 0 browser (BOT-1 only) OR full fleet_
- Concurrency start: _2 (initial RPS, ramp later)_
- Duration target: _N seconds_

## Planned action

Launch BOT-1 DoS against the agreed search endpoints (see [[antibot]] § Endpoint targets - cms-ms cached candidates, confirmed by client). Each VM runs:

```bash
docker run --rm -e WAF_BOTS_ALLOW_DOS=true waf-bots:dev \
  --bot bot-1-dos \
  --duration <N> \
  --concurrency <C> \
  --base-url https://api-coll.museiitaliani.it \
  --no-dry-run \
  --output /tmp/report.json
```

Goal: trigger Fortinet WAF DoS detection, observe `403 / 429 / 503 / connection reset / challenge redirect` from the WAF in measurable time.

## Blast radius

- **Direct target**: cms-ms cached endpoints. Backend is Django/DRF behind the WAF
- **Indirect impact** (worst case): if WAF does not throttle and backend cache misses, traffic propagates to cms-ms origin -> shared DB. Risk of **service degradation for real Ad Arte users on collaudo**
- **Network**: Linode -> public Internet -> Ad Arte WAF -> backend. No PSN involvement on egress
- **Collateral**: Ad Arte support team + SOC may receive false alerts, monitoring noise

## What can go wrong (Pre-Mortem)

| # | Failure | Probability | Impact |
|---|---|---|---|
| 1 | Executor IP already in WAF whitelist (blocker 1 not closed) | Low if SOC verified | Test invalid - no block triggers, hours wasted |
| 2 | WAF threshold higher than achievable from 2 VMs | Medium | Test inconclusive - either escalate or report as "not blocked" |
| 3 | Backend distress (5xx upstream) before WAF reacts | Medium | Real-user impact on collaudo |
| 4 | DoS hits unrelated cached endpoints not under WAF DoS policy | Medium | Test invalid - need confirmed endpoint list (blocker 3) |
| 5 | Linode network egress filtering / asymmetric routing | Low | Connection drops mistaken for WAF block |
| 6 | StackScript on VM failed to build the image | Low if smoke OK | Container missing on VM, BOT command fails fast (low impact) |
| 7 | Token revoked mid-run by Linode (anomaly detection) | Low | Cannot teardown via CLI - manual via web console |
| 8 | Cost overrun if test runs longer than planned | Low | <$5 even at full fleet for hours |

## Stop conditions (during run)

Abort the run **immediately** if any of:
- 5xx responses from the BOT >5% of total requests AND signal != WAF (i.e. backend not WAF responding 5xx)
- ssh from operator box to a VM stops responding
- Linode account flagged for abuse
- User communicates abort
- Any unexpected behavior on monitoring channels (Datadog Synthetics on Ad Arte show alerts)

## Prepared rollback plan

1. SIGINT each container (ssh root@<ip> docker stop $(docker ps -q))
2. If VM unreachable: shut down via Linode CLI `linodes shutdown <id>` (does not stop billing but stops traffic)
3. Confirm Datadog Synthetics on Ad Arte recover (no error events on cms-ms public endpoints) within 5 minutes
4. Pull `/tmp/report.json` from each VM (best-effort, keep evidence even on abort)
5. Notify SOC + client of abort + observed symptoms
6. Document in [[antibot#Log]] with timestamps + signals observed at abort
7. If irreversible impact suspected: invoke `02_core_mindset_and_behavior.md` rule 5 (Error handling with impact) and stop, do not retry

## Pre-flight checklist

Before pressing go:
- [ ] Blocker 1 closed: SOC confirmed executor IPs NOT in whitelist (capture IPs of all fleet VMs)
- [ ] Blocker 3 closed: client confirmed exact endpoint list to target (update `bots/dos.py` `requests` if different from cms-ms cached defaults)
- [ ] Lockbox `[[_secrets/linode]]` populated with rotated token
- [ ] All fleet VMs `running` and bootstrap done (`/var/log/stackscript.done` exists)
- [ ] Smoke from each VM: `ssh root@<ip> "docker run --rm waf-bots:dev --bot bot-1-dos --duration 1"` returns dry-run JSON OK
- [ ] Pre-mortem signed by operator + approver
- [ ] Time window agreed with SOC + client
- [ ] Datadog Synthetics dashboard for Ad Arte open in browser for live monitoring
- [ ] Backup channel to user (Slack/phone) confirmed
- [ ] Teardown command pre-typed, ready to fire (`./scripts/teardown-fleet.sh --yes`)

## Run log (fill during execution)

| Time | Concurrency | RPS observed | Signals (last 60s) | Notes |
|---|---|---|---|---|
| _HH:MM_ | _C_ | _N/s_ | _e.g. blocked_403=12, none=348_ | start |
| ... | | | | |

## Post-run

1. Collect reports: `./scripts/collect-reports.sh`
2. Teardown fleet: `./scripts/teardown-fleet.sh --yes`
3. Request FortiGate logs from SOC for the run window
4. Append summary to [[antibot#Log]]
5. Update [[Board]]: move "Provision antibot fleet" + "Run BOT-1" cards to Done
6. Decision note in `02_Areas/Decisions/` if outcome required policy change
