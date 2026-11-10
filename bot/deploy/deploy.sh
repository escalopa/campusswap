#!/usr/bin/env bash
# Deploy the CampusSwap bot to Cloud Run and point Telegram at it.
# One-time setup (project, Firestore, service account, secrets) is described in docs/bot/deploy.md.
set -euo pipefail

PROJECT="${PROJECT:-campusswap-infra}"
REGION="${REGION:-europe-west1}"
SERVICE="campusswap-bot"
SA="campusswap-bot@${PROJECT}.iam.gserviceaccount.com"
cd "$(dirname "$0")/.."   # bot/

gcloud run deploy "$SERVICE" \
  --project "$PROJECT" --region "$REGION" --source . \
  --service-account "$SA" \
  --set-secrets CAMPUSSWAP_TOKEN=telegram-token:latest,CAMPUSSWAP_WEBHOOK_SECRET=webhook-secret:latest \
  --min-instances 0 --max-instances 1 --memory 512Mi --cpu 1 --timeout 60 \
  --allow-unauthenticated --quiet

URL="$(gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" --format='value(status.url)')"
echo "Service URL: $URL"

# Register the webhook. Secrets are read from Secret Manager and passed via env, never printed.
CAMPUSSWAP_WEBHOOK_SECRET="$(gcloud secrets versions access latest --secret webhook-secret --project "$PROJECT")" \
  "${PYTHON:-.venv/bin/python}" -m campusswap_bot --config config.toml --set-webhook "$URL/telegram"
