#!sh
docker kill db
docker-compose -f docker-compose-db.yml up --build -d
cd ../App/
alembic revision --autogenerate -m "auto migrations"
alembic upgrade heads
cd api/
python3 main.py