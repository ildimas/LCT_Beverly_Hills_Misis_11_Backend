#!sh
docker kill db
docker kill backend
docker kill nginx
docker-compose -f docker-compose.yml up --build 
cd ..
alembic revision --autogenerate -m "test running migrations"
alembic upgrade heads