
curl -X 'PUT' \
  'http://localhost:8000/client/deactivate' \
  -H 'accept: application/json'

sleep 2

curl -X 'PUT' \
  'http://localhost:8000/service/stop' \
  -H 'accept: application/json'

podman-compose -f podman-compose.yml down