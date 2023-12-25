#!/bin/bash -e

git pull
pip install -r requirements.txt
python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput

npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

commit=`git rev-parse HEAD`

curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header "accept: application/json" \
     --header "content-type: application/json" \
     --header "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
     -d '{
  "environment": "production",
  "revision": "'$commit'",
  "rollbar_username": "User",
  "local_username": "User",
  "comment": "Deploy",
  "status": "Succeeded"
}'

echo -e "\033[32mSucceeded"
