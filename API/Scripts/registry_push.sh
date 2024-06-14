#!sh
cd ..
docker build --tag washingtonsilverstorage.cr.cloud.ru/washingtonsilver_api . --platform linux/amd64
docker push washingtonsilverstorage.cr.cloud.ru/washingtonsilver_api:latest
cd Nginx/
docker build --tag washingtonsilverstorage.cr.cloud.ru/washingtonsilver_nginx . --platform linux/amd64
docker push washingtonsilverstorage.cr.cloud.ru/washingtonsilver_nginx:latest