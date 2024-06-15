#!sh
docker kill db
docker kill backend
docker kill nginx
docker pull washingtonsilverstorage.cr.cloud.ru/washingtonsilver_nginx@sha256:afd0ba1cd4504ed5695aaded04faa4d33c70fb3decd90db41a7555d4bab2c059
docker-compose -f docker-compose.yml up --build 
cd ..
alembic revision --autogenerate -m "test running migrations"
alembic upgrade heads