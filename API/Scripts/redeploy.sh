#!/bin/sh
cd ..
cd ..
docker build --tag washingtonsilverstorage.cr.cloud.ru/washingtonsilver_api . --platform linux/amd64
docker push washingtonsilverstorage.cr.cloud.ru/washingtonsilver_api:latest
cd API/Nginx
docker build --tag washingtonsilverstorage.cr.cloud.ru/washingtonsilver_nginx . --platform linux/amd64
docker push washingtonsilverstorage.cr.cloud.ru/washingtonsilver_nginx:latest

# Load environment variables from .env file
export $(grep -v '^#' ../.env | xargs)

# Execute commands using the loaded environment variables
ssh $SSH_USER@$SSH_HOST << EOF
  cd lCT_Deploy
  sh product_build.sh
EOF