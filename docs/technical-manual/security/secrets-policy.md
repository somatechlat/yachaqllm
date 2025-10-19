# Secrets Policy

- **AWS Credentials:** Never commit AWS access keys. Use environment variables for local work and rely on IAM roles in AWS deployments.
- **API Keys:** Store third-party credentials in the approved secrets manager (AWS Secrets Manager). Rotate keys every 90 days.
- **RSA and TLS Keys:** Private keys must live in the secure secrets store only. Regenerate keys per service quarterly or immediately after suspected exposure.

## Incident Response: Secret Leak

1. **Rotate Immediately:** Generate a replacement credential (e.g., new RSA keypair or API key) and deploy it to dependent services. Document the rotation in the security logbook.
2. **Purge from Git History:** Use `git filter-repo --path <file>` (or BFG) to remove the leaked material from all branches, then force-push. Coordinate with collaborators so they reset their clones (`git fetch --all`, `git reset --hard origin/main`).
3. **Revoke Compromised Assets:** Invalidate the exposed key via AWS/IAM or the issuing authority. Confirm no lingering trust relationships reference the old key.
4. **Scan and Monitor:** Run `git ls-tree -r HEAD` and secret scanners (GitGuardian CLI, trufflehog) to confirm the repository is clean. Monitor access logs for anomalies following the rotation.
5. **Prevent Recurrence:** Add or update pre-commit hooks and CI secret scans. Ensure contributors follow the secure development checklist before pushing.
