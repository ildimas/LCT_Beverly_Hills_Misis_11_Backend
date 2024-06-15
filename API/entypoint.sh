#!/bin/bash
set -e

cd API/App/

alembic revision --autogenerate -m "Auto-generated migration"

alembic upgrade head

cd api/

exec python main.py