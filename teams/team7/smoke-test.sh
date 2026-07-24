#!/usr/bin/env bash
# End-to-end verification for the Team 7 gateway and backend.
set -euo pipefail

team_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
env_file="$team_dir/.env"

if [[ ! -f "$env_file" ]]; then
    echo "Missing $env_file. Copy .env.example to .env before running this check." >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Docker Desktop is not running." >&2
    exit 1
fi

if ! docker network inspect polylife_net >/dev/null 2>&1; then
    echo "Shared network polylife_net is missing. Start PolyLife Core first." >&2
    exit 1
fi

if [[ -z "${TEAM7_TOKEN:-}" ]]; then
    echo "Set TEAM7_TOKEN to a valid Core access token before running this check." >&2
    exit 1
fi

set -a
source "$env_file"
set +a

docker compose --project-directory "$team_dir" up --build --detach
docker compose --project-directory "$team_dir" exec --no-TTY backend pytest -q

curl --fail --silent --show-error "http://localhost:${TEAM_PORT}/" >/dev/null
curl --fail --silent --show-error \
    --header "Authorization: Bearer ${TEAM7_TOKEN}" \
    "http://localhost:${TEAM_PORT}/api/reserve/coaches" >/dev/null

echo "Team 7 smoke test passed."
