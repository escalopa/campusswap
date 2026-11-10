# Deploy to Google Cloud

The bot runs on **Cloud Run** in webhook mode with **Firestore** as its database, in the GCP project `campusswap-infra` (region `europe-west1`). There are two environments with separate bots, services, databases and secrets:

| | Test | Prod |
|---|---|---|
| Telegram bot | [@campusswap_test_bot](https://t.me/campusswap_test_bot) | [@campusswap_bot](https://t.me/campusswap_bot) |
| Cloud Run service | `campusswap-bot-test` | `campusswap-bot` |
| Firestore database | `staging` | `(default)` |
| Secret Manager | `telegram-token-test`, `webhook-secret-test` | `telegram-token`, `webhook-secret` |
| GitHub secret | `TELEGRAM_BOT_TOKEN_TEST` | `TELEGRAM_BOT_TOKEN_PROD` |
| Deployed | automatically on every push to `main` that changes `bot/` | by hand: Actions → **Deploy bot** → Run workflow → `prod` |

A third Firestore database, `test`, is used only by the automated tests.

```mermaid
flowchart LR
    S[Students in Telegram] <--> TG[Telegram servers]
    TG -- "POST /telegram<br>secret header" --> CR[Cloud Run<br>campusswap-bot / -test]
    CR --> FS[(Firestore<br>(default) / staging)]
    SM[Secret Manager] --> CR
    GH[GitHub Actions] -- "keyless (Workload Identity)" --> CR
```

## How it differs from running locally

| | Local | Cloud Run |
|---|---|---|
| Updates | Long polling | Webhook (`POST /telegram`) |
| Storage | SQLite file | Firestore (`[storage].backend = "firestore"`) |
| Conversation state | Memory | Firestore (`FirestorePersistence`), so a half-finished post survives a restart |
| Secrets | `config.toml` / `config.test.toml` | Secret Manager → `CAMPUSSWAP_TOKEN`, `CAMPUSSWAP_WEBHOOK_SECRET` |
| Entry point | `python -m campusswap_bot` | `python -m campusswap_bot.server` (Dockerfile) |

Each service runs with `--max-instances 1`, so one instance owns the in-memory conversation state, and processes each update inside the HTTP request, so CPU is billed only while a message is handled and the service scales to zero between messages. The webhook secret travels only in Telegram's `X-Telegram-Bot-Api-Secret-Token` header, never in the URL or logs. The URL is public (Telegram must reach it), but requests without the secret are refused.

## What is already set up

- Project `campusswap-infra`, billing linked, APIs enabled (Run, Firestore, Secret Manager, Artifact Registry, Cloud Build, IAM Credentials, STS)
- Firestore databases `(default)`, `staging`, `test`
- Service accounts `campusswap-bot` (runtime, `roles/datastore.user`) and `github-deployer`
- Secrets `telegram-token`, `webhook-secret`, `telegram-token-test`, `webhook-secret-test`
- Workload Identity pool `github` with provider `campusswap-repo`, accepting only `escalopa/campusswap` on `main`
- GitHub secrets `TELEGRAM_BOT_TOKEN_TEST` and `TELEGRAM_BOT_TOKEN_PROD`

## One-time: grant permissions (project owner)

The remaining IAM grants are in one script. Run it once:

```bash
cd bot
./deploy/setup-iam.sh
```

It lets the runtime account read the test secrets, lets GitHub Actions deploy without any JSON key, gives Cloud Build what it needs, and finally sets the GitHub variable `DEPLOY_ENABLED=true`, which switches on the deploy job.

## Deploy

From GitHub: push to `main` (test), or **Actions → Deploy bot → Run workflow** and pick `test` or `prod`. The workflow runs the tests first.

From your laptop (`bot/` folder, virtual environment set up):

```bash
./deploy/deploy.sh test
./deploy/deploy.sh prod
```

Both build the image with Cloud Build, deploy the service and register the webhook with Telegram.

!!! warning "Webhook vs local polling"
    While a bot's webhook is set, polling with that bot's token cannot receive updates. Develop locally with the **test** bot and stop its webhook first:
    `python -m campusswap_bot --config config.test.toml --delete-webhook`, then `python -m campusswap_bot --config config.test.toml`. Run `./deploy/deploy.sh test` to switch it back.

## Rotate a bot token

1. In @BotFather: `/revoke` → choose the bot → copy the new token.
2. Update Secret Manager and GitHub (values from stdin, never on the command line):
   ```bash
   pbpaste | gcloud secrets versions add telegram-token-test --project campusswap-infra --data-file=-
   pbpaste | gh secret set TELEGRAM_BOT_TOKEN_TEST --repo escalopa/campusswap
   ```
3. Redeploy that environment. The workflow warns if the GitHub secret and Secret Manager ever differ.

## Operate

```bash
gcloud run services logs read campusswap-bot-test --project campusswap-infra --region europe-west1 --limit 50
```

Data lives in the Firestore console under `campusswap-infra` → Firestore → `staging` (test) or `(default)` (prod).

## Tests against Firestore

```bash
CAMPUSSWAP_FIRESTORE_TEST_PROJECT=campusswap-infra CAMPUSSWAP_FIRESTORE_TEST_DATABASE=test pytest
```

Every database and flow test then runs twice (SQLite and Firestore), plus a test that restarts the app in the middle of posting an item and checks the post can still be finished. Each test writes under its own collection prefix and cleans up.
