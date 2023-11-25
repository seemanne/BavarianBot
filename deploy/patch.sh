set -e

current_date_time=$(date "+%Y_%m_%d_%H_%M")

git rev-parse --short HEAD >> ./current_patch

curl -X 'GET' \
  'http://localhost:8000/poast?channel=446853953905229844&message=Brb%2C%20getting%20an%20upgrade' \
  -H 'accept: application/json'

curl -X 'PUT' \
  'http://localhost:8000/client/deactivate' \
  -H 'accept: application/json'

sleep 2

curl -X 'PUT' \
  'http://localhost:8000/service/stop' \
  -H 'accept: application/json'

podman-compose -f podman-compose.yml down
cp volumes/db/chalkotheke.db backups/db/chalkotheke_$current_date_time.db
podman build -f ./CONTAINERFILE -t bavarianbot:latest .
nohup podman-compose -f podman-compose.yml up &

echo "giving the coontainer time to start"
sleep 5

curl -X 'PUT' \
  'http://localhost:8000/service/start' \
  -H 'accept: application/json'

curl -X 'PUT' \
  'http://localhost:8000/client/activate' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost:8000/service/status' \
  -H 'accept: application/json'