#!sh
docker kill db
docker-compose -f docker-compose.yml up --build 
cd ..
alembic revision --autogenerate -m "test running migrations"
alembic upgrade heads