docker rmi -f $(docker images | grep conclave-web | awk '{print $3}') &&
echo 'Removed ' &&
docker build -t singhp11/conclave-web:latest . &&
docker push singhp11/conclave-web:latest
