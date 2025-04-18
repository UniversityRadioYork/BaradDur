IMAGE="evergiven.ury.york.ac.uk:5000/scheduler"
CONTAINER="scheduler"
PROJECTDIR="/opt/scheduler"
LOGDIR="/mnt/logs/"
PORT=5042
DATE=$(date +%s)

docker build -t $IMAGE:$DATE .
docker push $IMAGE:$DATE
docker service update --image $IMAGE:$DATE scheduler
