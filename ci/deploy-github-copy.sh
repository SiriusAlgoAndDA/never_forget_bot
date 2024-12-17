#!/bin/bash
echo "Environment: $CI_ENVIRONMENT_NAME"

mkdir -p ~/.ssh
echo "$SSH_KEY" | tr -d '\r' > ~/.ssh/deploy_key
sudo chmod 600 ~/.ssh/deploy_key
ssh -i ~/.ssh/deploy_key -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USERNAME@$SSH_HOST "echo Ping && mkdir -p $CODE_FOLDER && exit"
tar -czf $CODE_FOLDER.tar.gz *
scp -i ~/.ssh/deploy_key -P $SSH_PORT -o StrictHostKeyChecking=no $CODE_FOLDER.tar.gz $SSH_USERNAME@$SSH_HOST:~/$CODE_FOLDER
ssh -i ~/.ssh/deploy_key -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USERNAME@$SSH_HOST "
  cd $CODE_FOLDER;
  tar -xzf $CODE_FOLDER.tar.gz
  echo \"$ENV\" > .env;
  make docker-stop postgres || echo \"Postgres not run\";
  make update;
  exit"
