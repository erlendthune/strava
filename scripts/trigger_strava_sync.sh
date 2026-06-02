#!/bin/sh

set -eu

REPO_OWNER="erlendthune"
REPO_NAME="strava"
WORKFLOW_FILE="strava_sync.yml"
REF_NAME="main"

if [ -z "${STRAVA_GITHUB_TOKEN:-}" ]; then
  echo "STRAVA_GITHUB_TOKEN is not set" >&2
  exit 1
fi

api_url="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/${WORKFLOW_FILE}/dispatches"

http_code=$(
  curl --silent --show-error \
    --output /tmp/strava_workflow_dispatch_response.txt \
    --write-out '%{http_code}' \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${STRAVA_GITHUB_TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$api_url" \
    -d "{\"ref\":\"${REF_NAME}\"}"
)

if [ "$http_code" != "204" ]; then
  echo "Workflow dispatch failed with HTTP $http_code" >&2
  cat /tmp/strava_workflow_dispatch_response.txt >&2
  rm -f /tmp/strava_workflow_dispatch_response.txt
  exit 1
fi

rm -f /tmp/strava_workflow_dispatch_response.txt
echo "Triggered ${WORKFLOW_FILE} on ${REF_NAME} at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"