#!/bin/sh
# Load environment variables from .env file
export $(grep -v '^#' ../.env | xargs)

# Execute commands using the loaded environment variables
ssh $SSH_USER@$SSH_HOST << EOF
  cd lCT_Deploy
  sh product_build.sh
EOF