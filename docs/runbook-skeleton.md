# Operational Runbook (Skeleton)

Purpose
-------
Provide a concise, actionable runbook for common incidents affecting the harvesting pipeline (solver failures, login-redirect spikes, storage issues, backlog growth). This is a skeleton to be expanded with environment-specific commands and contacts.

On-call contact
--------------
- Primary on-call (Platform): platform@example.com
- Secondary on-call (Data Eng): data-eng@example.com
- Escalation: Team lead

Key dashboards
--------------
- Harvest overview: jobs started/succeeded/failed
- Solver dashboard: attempts, success rate, latency p95
- Backlog: manual queue size, age p95
- Error breakdown: 4xx/5xx/login-redirect rates

Common incidents & playbooks
---------------------------

1) High rate of login-redirects (sign of captcha/session failure)
- Detection:
  - Alert: login_redirect_rate > 5% over 10 minutes
- Immediate actions:
  - Pause new jobs for affected source (or reduce concurrency to 1)
  - Check most recent trace for that source and compare to canonical trace
  - Check recent solver activity and TTL issues
  - Confirm if site changed (run Pydoll discovery for a representative query)
- Recovery:
  - If a small change in payload or headers is identified, patch payload builder and run canary
  - If broader site change, escalate to discovery team to capture new traces

2) Solver outage / high failure rate
- Detection:
  - Alert: solver_success_rate < 80% or pending_queue_age > TTL/2
- Immediate actions:
  - Switch to manual-in-the-loop for priority jobs (if human resource available)
  - Reduce solver call rate or stop non-critical jobs
  - Check external solver provider status page and API keys
  - Review cost governor thresholds (stop automated solver if cost spike detected)
- Recovery:
  - Switch back to automated solver when health is restored, monitor closely for a spike in backoff

3) Backlog growth in manual queue
- Detection:
  - Alert: pending_queue_size > threshold OR pending_queue_age_p95 > TTL/2
- Immediate actions:
  - Notify human operators; prioritize high-value jobs
  - Temporarily suspend new scheduled jobs for affected sources until backlog reduces

4) Storage write failures or object-store errors
- Detection:
  - Alert: storage write error rate > 1% or object-store returns 5xx
- Immediate actions:
  - Halt writes to object storage; buffer locally in ephemeral store if safe
  - Run storage client health checks; rotate credentials if auth errors
  - Contact storage provider support if outage persists

5) Data integrity alert (parsing errors spike)
- Detection:
  - Alert: parsed_success_rate drops or parsing exceptions spike
- Immediate actions:
  - Re-run parser against raw artifacts for a small sample to confirm if schema drift occurred
  - Compare Pydoll trace payload shape to current payload builder
  - If schema drift, patch parser and re-run backfill for affected windows

Escalation & postmortem
-----------------------
- If incident not resolved within SLA (e.g., 2 hours for critical outage), escalate to team lead.
- After recovery: open an incident report including timeline, root cause, remediation steps, and action items.

Playbook maintenance
--------------------
- Keep this runbook in the repo and review quarterly or after any major incident.
- Add provider-specific contact details, commands and quick-run scripts in a secure location referenced by this runbook.

Document owner: Yachaq Data Platform
File: docs/runbook-skeleton.md
