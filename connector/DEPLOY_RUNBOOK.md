# TGL connector operations

Current app: `tgl-summitx`, Fly.io, region dfw, one process on one 512 MB shared machine. Source in the public tom-nwachuku/tgl repository. The deployment credential is the existing GitHub Actions FLY_API_TOKEN secret; never copy it into logs, packets or the browser.

## Release

1. Save the current image/release ID and machine count. Sessions are ephemeral; **a deploy or rollback discards active planning sessions**. Never describe rollback as having no data impact.
2. Run the bundle-drift check and regression suite on the exact commit. Check public documentation against API.md.
3. Build only `connector/` using its Dockerfile. Non-root user; one Uvicorn process; access logs off. Private preparation, evidence and credentials stay outside the image context.
4. Dispatch the deploy workflow for the reviewed branch, or merge an approved PR to main. The workflow verifies before deploying. Use no HA standby machine: session data is process-local and must not randomly route across machines. Do not scale horizontally without a shared, authenticated state design.
5. Read the deployment result, then perform SDK initialize/list/all-tool/doc/delete verification at the public URL. A green deployment alone is insufficient. Re-test through Muse's actual custom integration.

## Custom domain

In Cloudflare, create only the scoped `tgl.summitxdigital.com` record(s) supplied by the Fly app's current certificate/DNS instructions, with proxy disabled. Do not guess app IPs from edge DNS. Preserve main-site, developer-site and mail records. Request/verify Fly's TLS certificate for this exact domain. Confirm HTTPS, `/`, `/privacy`, `/terms`, initialize and the full MCP journey. Then set `TGL_PUBLIC_BASE_URL=https://tgl.summitxdigital.com` and update public copy and the unsubmitted review form. The Fly domain remains a valid fallback.

Host/Origin validation must allow the deployed public names. Fly health checks use `/`; verify their actual status. Never globally disable DNS-rebinding protection to fix a hostname mismatch.

## Rollback and incidents

Redeploy the previously recorded image/commit through the existing workflow. Verify its actual public tools and document behavior. Both forward deploy and rollback discard live sessions. A rollback to the original build also restores its known read/write-link and deletion limitations, so consider disabling access until a fixed forward release instead.

Session content must not enter logs or support issues. Ask users to delete their session with tgl_plan_delete; privacy support is private email. Investigate security incidents using non-content metadata, limit exposure, preserve necessary evidence privately and notify the responsible owner. The published Muse Connector Terms require notice to Meta within 48 hours for a User Data incident; Tom must review and accept those obligations before store submission. Do not invent a Meta incident API or claim monitoring/SLA coverage that is not configured.

## Submission boundary

Deployment, custom integration, directory approval and featured placement are different states. Leave all final form attestations and Terms acceptance for Tom. Never call a prepared draft submitted, approved, or listed.
