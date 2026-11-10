#!/usr/bin/env bash
# One-time IAM setup for campusswap-infra. Run once, by the project owner:
#   ./deploy/setup-iam.sh
# Already created (no need to repeat): project, Firestore databases (default)/staging/test,
# service accounts campusswap-bot + github-deployer, secrets, Workload Identity pool "github"
# with provider "campusswap-repo" (only escalopa/campusswap, main branch).
set -euo pipefail
P=campusswap-infra
PN="$(gcloud projects describe $P --format='value(projectNumber)')"
RUNTIME="campusswap-bot@$P.iam.gserviceaccount.com"
DEPLOYER="github-deployer@$P.iam.gserviceaccount.com"
BUILD="$PN-compute@developer.gserviceaccount.com"
q() { "$@" --format="value(etag)" >/dev/null && echo "ok: ${*: -1}"; }

# Runtime service account: read its own secrets (prod ones were granted already).
for s in telegram-token-test webhook-secret-test; do
  q gcloud secrets add-iam-policy-binding "$s" --project $P --member "serviceAccount:$RUNTIME" --role roles/secretmanager.secretAccessor
done

# GitHub Actions deployer: build from source, deploy Cloud Run, read secrets to register the webhook.
for role in roles/run.sourceDeveloper roles/run.admin roles/cloudbuild.builds.editor roles/artifactregistry.admin \
            roles/storage.admin roles/serviceusage.serviceUsageConsumer roles/logging.viewer roles/secretmanager.secretAccessor; do
  q gcloud projects add-iam-policy-binding $P --member "serviceAccount:$DEPLOYER" --role "$role" --condition=None
done
q gcloud iam service-accounts add-iam-policy-binding "$RUNTIME" --project $P --member "serviceAccount:$DEPLOYER" --role roles/iam.serviceAccountUser
q gcloud iam service-accounts add-iam-policy-binding "$BUILD" --project $P --member "serviceAccount:$DEPLOYER" --role roles/iam.serviceAccountUser

# Let GitHub Actions in escalopa/campusswap act as the deployer (keyless, no JSON keys).
q gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER" --project $P --role roles/iam.workloadIdentityUser \
  --member "principalSet://iam.googleapis.com/projects/$PN/locations/global/workloadIdentityPools/github/attribute.repository/escalopa/campusswap"

# Cloud Build's default service account needs to push images and write logs.
for role in roles/artifactregistry.writer roles/logging.logWriter roles/storage.objectViewer; do
  q gcloud projects add-iam-policy-binding $P --member "serviceAccount:$BUILD" --role "$role" --condition=None
done
gh variable set DEPLOY_ENABLED --repo escalopa/campusswap --body true && echo "ok: GitHub deploys enabled"
echo "IAM setup done."
