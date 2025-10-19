#!/usr/bin/env bash
set -euo pipefail

IMAGE=${IMAGE:-yachaq-ingest:ro}
SPIDER=${SPIDER:-registro_oficial}
START_ID=${START_ID:-245800}
END_ID=${END_ID:-245000}
S3_BUCKET=${S3_BUCKET:?set S3_BUCKET}
S3_PREFIX=${S3_PREFIX:?set S3_PREFIX}
SCRAPY_OPTS=${SCRAPY_OPTS:-"-s CONCURRENT_REQUESTS_PER_DOMAIN=12 -s DOWNLOAD_DELAY=1.0"}

echo "Running $IMAGE spider=$SPIDER range $START_ID..$END_ID -> s3://$S3_BUCKET/$S3_PREFIX"

docker run --rm \
  -e SPIDER="$SPIDER" \
  -e START_ID="$START_ID" \
  -e END_ID="$END_ID" \
  -e FILES_STORE=/data/raw/scrapy_downloads \
  -e S3_BUCKET="$S3_BUCKET" \
  -e S3_PREFIX="$S3_PREFIX" \
  -e SCRAPY_OPTS="$SCRAPY_OPTS" \
  -v /mnt/data:/data \
  "$IMAGE"
