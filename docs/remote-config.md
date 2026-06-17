<!-- SPDX-License-Identifier: FSL-1.1-MIT -->

# Remote-config flag reconciliation

Runtime feature flags ("remote config") live as `Feature` rows in this service and
are edited through Django admin. Each consuming repo also ships a checked-in
**declaration file** listing the flags it expects. The admin **"Reconcile flags"**
view fetches those declarations from GitHub at a Git ref, diffs them against the
database, and lets an operator selectively apply the differences.

This is a _configuration-as-code → reconcile_ workflow on the **existing**
`Feature`/`Service`/`Chain` models — it adds no new config tables. (One small
operational table, `RemoteConfigReconcileRef`, just remembers the last ref used
per service so the form can pre-fill it.)

## Canonical service keys (Phase 0)

Declarations are diffed **per service**. The canonical `Service.key` values and
the repo → service → path mapping (configured in `REMOTE_CONFIG_SOURCES`):

| Service key  | Repo                                | Declaration path                        |
| ------------ | ----------------------------------- | --------------------------------------- |
| `WALLET_WEB` | `safe-global/safe-wallet-monorepo`  | `apps/web/config/remote-config.json`    |
| `MOBILE`     | `safe-global/safe-wallet-monorepo`  | `apps/mobile/config/remote-config.json` |
| `CGW`        | `safe-global/safe-client-gateway`   | `remote-config.json`                    |

A `Service` row must exist for each key. An ADD/ATTACH will auto-create a missing
`Service` (named after its key); you can also create them up front in
**Admin → Services**.

## Settings

| Setting                         | Default                             | Purpose                                            |
| ------------------------------- | ----------------------------------- | -------------------------------------------------- |
| `REMOTE_CONFIG_GITHUB_TOKEN`    | _(unset)_                           | Optional; raises the raw-API rate limit. Public repos work without it. |
| `REMOTE_CONFIG_TIMEOUT_SECONDS` | `5`                                 | Per-fetch HTTP timeout.                            |
| `REMOTE_CONFIG_RAW_BASE_URL`    | `https://raw.githubusercontent.com` | Base URL for raw fetches (overridable for testing).|
| `REMOTE_CONFIG_SOURCES`         | web/mobile/cgw (see above)          | The repo/path/service mapping.                     |

## Release runbook: reconcile flags

1. Merge the release's declaration changes (or push the release branch).
2. Go to **Admin → Features → "Reconcile flags"**.
3. Enter the Git ref per service (branch, tag, or SHA). The form pre-fills each
   service's last-used ref.
4. **Compute diff.** Each source shows a git-diff-style table of
   `ADD` / `ATTACH` / `UPDATE` / `DETACH` / `DELETE`.
5. Review the checkboxes (smart defaults, decision #6):
   - **Pre-checked:** ADD, ATTACH, and authoritative `description`/`scope` updates.
   - **Un-checked:** `chains` divergences and DETACH/DELETE — these are deliberate.
6. **Apply selected changes.** Mutations run in one transaction and are written to
   the admin History (`LogEntry`). The refs you used are remembered for next time.

### Diff semantics

- **ADD** — declared key has no `Feature` row → create it (declared `scope`/`description`),
  attach the service, and seed `chains` from `defaultChains` (PER_CHAIN only).
- **ATTACH** — a `Feature` with that key exists but lacks this service → attach the service.
- **UPDATE** — attached, but `description`/`scope` (code-authoritative) or `chains`
  (informational — release-time default, never force-applied) differ.
- **DETACH** — in the DB for this service but no longer declared → detach the service.
- **DELETE** — detaching would leave the `Feature` with **zero** services → offer a row delete.
  A flag shared with another service is never deleted, only detached.

`defaultChains` is a **release-time seed, not desired state.** After launch, ops may
enable/disable a flag per chain; the tool surfaces a `chains` divergence as informational
drift and never overwrites it unless you explicitly tick it.

## Drift detection

The **"Check drift vs default branch"** link runs the same diff read-only against each
repo's **trunk** (its `default_ref`: `dev` for the wallet monorepo, `main` for CGW) — no
apply controls. Use it any time to spot code-vs-DB drift (a flag declared on the trunk but
missing in the DB, or enabled in the DB but no longer declared).

A "not found" for a source usually means the declaration file isn't on that branch yet —
e.g. it is still on an unmerged feature branch. The check is only meaningful once the
declarations are merged to each repo's trunk.

## A note on caching (prefer a SHA/tag for releases)

Declarations are fetched from `raw.githubusercontent.com/<repo>/<ref>/<path>`. GitHub's
**raw CDN caches each branch URL for ~5 minutes**, so immediately after a push a *branch*
ref can briefly serve the previous commit's content (you may see one service update while
another still shows the old value as the per-URL caches expire at different times). The
Config Service itself adds no caching.

- For a **release reconcile**, enter an exact **commit SHA or tag** as the ref. SHA/tag URLs
  are immutable, so they are always fresh and pin the reconcile to a known release.
- For **drift checks** against a branch (e.g. `main`), a stale read self-corrects within the
  CDN TTL — just re-compute after a few minutes.

## Seeding the initial declaration from the DB

To make the first reconcile clean, export current production state into the checked-in
declaration file:

```bash
python src/manage.py export_remote_config --service WALLET_WEB > remote-config.json
```

Run per service, review, and commit into the relevant repo.

## Adding a new flag (in a consuming repo)

1. Add the key to the repo's flag source (the `FEATURES` enum for web/mobile, or an
   `isFeatureEnabled(...)` call for CGW).
2. Add a matching entry to that repo's `remote-config.json` (`key`, `description`,
   `scope`, and `defaultChains` for the chains it should launch on).
3. The repo's sync test fails if code references an undeclared flag (or vice-versa).
4. On release, reconcile via the admin view above to create/seed the `Feature` row.
