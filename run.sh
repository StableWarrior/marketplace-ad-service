#!/bin/bash

set -e

uv run alembic upgrade head
uv run python -m bin.outbox &
uv run python -m bin.api
