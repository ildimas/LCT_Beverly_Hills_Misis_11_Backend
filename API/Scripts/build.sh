cd ..
cd ..
docker build --tag washingtonsilverstorage.cr.cloud.ru/washingtonsilver_api . --platform linux/amd64
docker push washingtonsilverstorage.cr.cloud.ru/washingtonsilver_api:latest
cd API/Nginx
docker build --tag washingtonsilverstorage.cr.cloud.ru/washingtonsilver_nginx . --platform linux/amd64
docker push washingtonsilverstorage.cr.cloud.ru/washingtonsilver_nginx:latest
cd ..
cd Database/
docker build --tag washingtonsilverstorage.cr.cloud.ru/washingtonsilver_database . --platform linux/amd64
docker push washingtonsilverstorage.cr.cloud.ru/washingtonsilver_database:latest