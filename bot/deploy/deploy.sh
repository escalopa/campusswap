#!/usr/bin/env bash
# Deploy the CampusSwap bot to Cloud Run and point Telegram at it.
#   ./deploy/deploy.sh test    → campusswap-bot-test (@campusswap_test_bot, Firestore "staging")
#   ./deploy/deploy.sh prod    → campusswap-bot      (@campusswap_bot,      Firestore "(default)")
# GitHub Actions runs the same steps (.github/workflows/deploy.yml). One-time setup: docs/bot/deploy.md.
set -euo pipefail

ENV="${1:-test}"
PROJECT="${PROJECT:-campusswap-infra}"
REGION="${REGION:-europe-west1}"
case "$ENV" in
  prod) SERVICE=campusswap-bot;      DB="(default)"; TOKEN_SECRET=telegram-token;      HOOK_SECRET=webhook-secret ;;
  test) SERVICE=campusswap-bot-test; DB=staging;     TOKEN_SECRET=telegram-token-test; HOOK_SECRET=webhook-secret-test ;;
  *) echo "usage: $0 test|prod" >&2; exit 2 ;;
esac
SA="campusswap-bot@${PROJECT}.iam.gserviceaccount.com"
cd "$(dirname "$0")/.."   # bot/

gcloud run deploy "$SERVICE" \
  --project "$PROJECT" --region "$REGION" --source . \
  --service-account "$SA" \
  --set-env-vars "CAMPUSSWAP_FIRESTORE_DATABASE=$DB" \
  --set-secrets "CAMPUSSWAP_TOKEN=${TOKEN_SECRET}:latest,CAMPUSSWAP_WEBHOOK_SECRET=${HOOK_SECRET}:latest" \
  --min-instances 0 --max-instances 1 --memory 512Mi --cpu 1 --timeout 60 \
  --allow-unauthenticated --quiet

URL="$(gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" --format='value(status.url)')"
echo "Service URL: $URL"

# Register the webhook. Secrets go through env vars and are never printed.
CAMPUSSWAP_TOKEN="$(gcloud secrets versions access latest --secret "$TOKEN_SECRET" --project "$PROJECT")" \
CAMPUSSWAP_WEBHOOK_SECRET="$(gcloud secrets versions access latest --secret "$HOOK_SECRET" --project "$PROJECT")" \
  "${PYTHON:-.venv/bin/python}" -m campusswap_bot --config deploy/config.cloud.toml --set-webhook "$URL/telegram"
