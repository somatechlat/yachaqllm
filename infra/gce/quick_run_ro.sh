#!/usr/bin/env bash
set -euo pipefail

# Quick provision + run Registro Oficial on GCE with persistent logs
# Requirements: gcloud CLI authenticated to your project; AWS creds (if needed) to push to S3.

# Defaults
PROJECT="${PROJECT:-}"
ZONE="${ZONE:-us-central1-a}"
INSTANCE="${INSTANCE:-yachaq-scrape-1}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-standard-4}"
DISK_SIZE="${DISK_SIZE:-50GB}"
IMAGE_FAMILY="${IMAGE_FAMILY:-debian-12}"
IMAGE_PROJECT="${IMAGE_PROJECT:-debian-cloud}"

S3_BUCKET="${S3_BUCKET:-}"
S3_PREFIX="${S3_PREFIX:-raw/ecuador/registro_oficial/2025/10}"
START_ID="${START_ID:-245500}"
END_ID="${END_ID:-245200}"
CONCURRENCY="${CONCURRENCY:-8}"
DELAY="${DELAY:-1}"

# Optional AWS creds (if using key-based auth)
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-}"
AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"

IMAGE_NAME="${IMAGE_NAME:-yachaq/ingest:ro}"
REPO_URL="${REPO_URL:-https://github.com/somatechlat/yachaqllm.git}"
REMOTE_DIR="${REMOTE_DIR:-~/yachaqllm}"
REMOTE_LOG_DIR="/var/log/yachaq"
REMOTE_LOG_FILE="$REMOTE_LOG_DIR/registro_oficial_current.log"
LOCAL_ENV_FILE="$HOME/.yachaq_env"

usage() {
  cat <<EOF
Usage: PROJECT=<id> S3_BUCKET=<bucket> [options] ./infra/gce/quick_run_ro.sh

Environment variables:
  PROJECT                GCP project ID (required)
  ZONE                   GCE zone (default: us-central1-a)
  INSTANCE               Instance name (default: yachaq-scrape-1)
  MACHINE_TYPE           Instance type (default: e2-standard-4)
  DISK_SIZE              Boot disk size (default: 50GB)
  IMAGE_FAMILY           Base OS family (default: debian-12)
  IMAGE_PROJECT          Base OS project (default: debian-cloud)

  S3_BUCKET              Target S3 bucket (required)
  S3_PREFIX              S3 prefix (default: raw/ecuador/registro_oficial/2025/10)
  START_ID               Start ID (default: 245500)
  END_ID                 End ID (default: 245200)
  CONCURRENCY            Scrapy concurrency (default: 8)
  DELAY                  Scrapy download delay in seconds (default: 1)

  AWS_ACCESS_KEY_ID      Optional AWS access key
  AWS_SECRET_ACCESS_KEY  Optional AWS secret
  AWS_DEFAULT_REGION     AWS region (default: us-east-1)

  IMAGE_NAME             Docker image tag to build/run (default: yachaq/ingest:ro)

After completion, tail the log with:
  gcloud compute ssh $INSTANCE -- -t "sudo tail -n +1 -F $REMOTE_LOG_FILE"
EOF
}

if [[ -z "${PROJECT}" || -z "${S3_BUCKET}" ]]; then
  usage
  echo "\nERROR: PROJECT and S3_BUCKET are required." >&2
  exit 1
fi

echo "[1/8] Configuring gcloud project/zone"
gcloud config set project "$PROJECT" >/dev/null
gcloud config set compute/zone "$ZONE" >/dev/null

echo "[2/8] Ensuring instance $INSTANCE exists (zone=$ZONE)"
if ! gcloud compute instances describe "$INSTANCE" --format='value(status)' >/dev/null 2>&1; then
  gcloud compute instances create "$INSTANCE" \
    --machine-type="$MACHINE_TYPE" \
    --boot-disk-size="$DISK_SIZE" \
    --image-family="$IMAGE_FAMILY" --image-project="$IMAGE_PROJECT" \
    --metadata-from-file startup-script=infra/gce/install_docker.sh >/dev/null
else
  echo "Instance exists; skipping create"
fi

if [[ "${STOP_OTHERS:-0}" == "1" ]]; then
  echo "[2.5/8] Stopping any other instances so only $INSTANCE remains running"
  OTHER_INSTANCES=$(gcloud compute instances list --format='value(name)' | grep -v "^$INSTANCE$" || true)
  if [[ -n "$OTHER_INSTANCES" ]]; then
    for inst in $OTHER_INSTANCES; do
      echo " - Stopping $inst"
      gcloud compute instances stop "$inst" --zone "$ZONE" --quiet >/dev/null || true
    done
  else
    echo "No other instances found."
  fi
else
  echo "[2.5/8] Skipping stop of other instances (set STOP_OTHERS=1 to enable)"
fi

echo "[3/8] Waiting for SSH access..."
for i in {1..30}; do
  if gcloud compute ssh "$INSTANCE" --command "echo ok" >/dev/null 2>&1; then
    break
  fi
  sleep 5
done

echo "[4/8] Verifying Docker is available..."
for i in {1..30}; do
  if gcloud compute ssh "$INSTANCE" --command "docker --version" >/dev/null 2>&1; then
    break
  fi
  sleep 5
done

if [[ "${SYNC_CODE:-0}" == "1" ]]; then
  echo "[5/8] Syncing ingestion code to VM (code only, no bulky downloads)"
  gcloud compute ssh "$INSTANCE" --command "mkdir -p $REMOTE_DIR/rag/ingest" >/dev/null
  gcloud compute ssh "$INSTANCE" --command "rm -rf $REMOTE_DIR/rag/ingest/ingest_spiders" >/dev/null || true
  gcloud compute ssh "$INSTANCE" --command "rm -rf $REMOTE_DIR/rag/ingest/downloads" >/dev/null || true
  gcloud compute ssh "$INSTANCE" --command "rm -rf $REMOTE_DIR/rag/ingest/data" >/dev/null || true
  gcloud compute scp --recurse rag/ingest/ingest_spiders "$INSTANCE":"$REMOTE_DIR/rag/ingest" >/dev/null
  gcloud compute scp rag/ingest/requirements.txt "$INSTANCE":"$REMOTE_DIR/rag/ingest" >/dev/null
  gcloud compute scp rag/ingest/entrypoint.sh "$INSTANCE":"$REMOTE_DIR/rag/ingest" >/dev/null
  gcloud compute scp rag/ingest/Dockerfile "$INSTANCE":"$REMOTE_DIR/rag/ingest" >/dev/null
else
  echo "[5/8] Skipping code sync (set SYNC_CODE=1 to push local changes)"
fi

echo "[5.5/8] Ensuring AWS credentials available on VM (for S3 uploads)"
# Prefer copying local ~/.aws to the VM so the container can mount read-only creds
if [[ -d "$HOME/.aws" ]]; then
  echo " - Copying local ~/.aws to VM"
  gcloud compute scp --recurse "$HOME/.aws" "$INSTANCE":"~/.aws" >/dev/null || true
else
  echo " - No local ~/.aws directory found; relying on AWS_* env vars if provided"
fi

echo "[5.6/8] Copying local .env to VM (if present)"
if [[ -f "${LOCAL_ENV_FILE}" ]]; then
  echo " - Copying ${LOCAL_ENV_FILE} to VM as ~/.yachaq_env"
  gcloud compute scp "${LOCAL_ENV_FILE}" "$INSTANCE":"~/.yachaq_env" >/dev/null || true
  # Also copy to the repo remote dir so docker can use it as an --env-file
  gcloud compute scp "${LOCAL_ENV_FILE}" "$INSTANCE":"$REMOTE_DIR/.env" >/dev/null || true
else
  echo " - No local .env (${LOCAL_ENV_FILE}) found; skipping"
fi

FORCE_REBUILD="${FORCE_REBUILD:-0}"
echo "[6/8] Ensuring Docker image $IMAGE_NAME exists (FORCE_REBUILD=$FORCE_REBUILD)"
if gcloud compute ssh "$INSTANCE" --command "docker image inspect $IMAGE_NAME >/dev/null 2>&1"; then
  if [[ "$FORCE_REBUILD" == "1" ]]; then
    echo " - Image exists but FORCE_REBUILD=1; rebuilding..."
    gcloud compute ssh "$INSTANCE" --command "cd $REMOTE_DIR && docker build -t $IMAGE_NAME -f rag/ingest/Dockerfile ." >/dev/null
  else
    echo " - Image already present; skipping rebuild."
  fi
else
  echo " - Image not found; building now..."
  gcloud compute ssh "$INSTANCE" --command "cd $REMOTE_DIR && docker build -t $IMAGE_NAME -f rag/ingest/Dockerfile ." >/dev/null
fi

echo "[7/8] Starting Registro Oficial container with S3 upload and log file"
AWS_ENV=""
[[ -n "$AWS_ACCESS_KEY_ID" ]] && AWS_ENV+=" -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
[[ -n "$AWS_SECRET_ACCESS_KEY" ]] && AWS_ENV+=" -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"
[[ -n "$AWS_DEFAULT_REGION" ]] && AWS_ENV+=" -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION"

RUN_CMD=$(cat <<RCMD
set -euo pipefail
sudo mkdir -p $REMOTE_LOG_DIR
docker rm -f ro-job >/dev/null 2>&1 || true
docker run -d --name ro-job --restart unless-stopped \
  -e S3_BUCKET="$S3_BUCKET" \
  -e S3_PREFIX="$S3_PREFIX" \
  -e FILES_STORE=/data/raw/scrapy_downloads \
  $AWS_ENV \
  -v $REMOTE_DIR/rag/ingest_spiders:/app/ingest_spiders_project \
  -v "$HOME/.aws:/root/.aws:ro" \
  -v $REMOTE_LOG_DIR:/logs \
  $IMAGE_NAME \
  sh -lc 'cd ingest_spiders && scrapy crawl registro_oficial \
    -a start_id=$START_ID -a end_id=$END_ID \
    -s LOG_LEVEL=INFO -s CONCURRENT_REQUESTS=$CONCURRENCY -s DOWNLOAD_DELAY=$DELAY \
    -s LOG_FILE=/logs/registro_oficial_current.log'
RCMD
)

gcloud compute ssh "$INSTANCE" --command "$RUN_CMD" >/dev/null

echo "[8/8] Done. To follow the live log, run:"
echo "gcloud compute ssh $INSTANCE -- -t \"sudo tail -n +1 -F $REMOTE_LOG_FILE\""
