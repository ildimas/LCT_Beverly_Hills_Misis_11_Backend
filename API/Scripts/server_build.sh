#!sh
docker kill db
docker kill backend
docker kill nginx
docker pull washingtonsilverstorage.cr.cloud.ru/washingtonsilver_api:latest
docker pull washingtonsilverstorage.cr.cloud.ru/washingtonsilver_nginx:latest
docker pull washingtonsilverstorage.cr.cloud.ru/washingtonsilver_frontend:latest
docker-compose -f docker-compose-server.yml up --build 
