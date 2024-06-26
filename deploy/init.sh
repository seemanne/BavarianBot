set -e
cat .env
podman build -f ./CONTAINERFILE_BOT -t bavarianbot:latest .
mkdir -p volumes/db
mkdir -p backups/db
nohup podman-compose -f podman-compose.yml up &

echo "giving the container time to start"
sleep 5

curl -X 'GET' \
  'http://localhost:8000/service/init_db' \
  -H 'accept: application/json'

curl -X 'PUT' \
  'http://localhost:8000/service/start' \
  -H 'accept: application/json'

curl -X 'PUT' \
  'http://localhost:8000/client/activate' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost:8000/service/status' \
  -H 'accept: application/json'