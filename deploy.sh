IMAGE="evergiven.ury.york.ac.uk:5000/baraddur"
CONTAINER="baraddur"
PROJECTDIR="/opt/baraddur"
LOGDIR="/mnt/logs/"
PORT=6339
DATE=$(date +%s)

docker build -t $IMAGE:$DATE .
docker push $IMAGE:$DATE
docker service update --image $IMAGE:$DATE baraddur
