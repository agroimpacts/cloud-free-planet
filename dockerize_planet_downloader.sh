#! /bin/bash
read -p "Enter name of docker image tag: " TAG
echo

# login into AWS ECS registry
make login-aws-registry

# build an image
docker-compose build

# docker string
DOCKERSTRING=554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader
DOCKERLATEST=$DOCKERSTRING:latest
DOCKERTAGGED=$DOCKERSTRING:$TAG
# echo $DOCKERTAGGED
# echo $DOCKERLATEST

# update docker compose
sed -i '' "4s~image:.*~image: $DOCKERTAGGED~" deployment/docker-compose.yml

# tag latest image with any tag you want
# docker tag 554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:latest 554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:$TAG
docker tag $DOCKERLATEST $DOCKERTAGGED
# 
# # push it into AWS ECS registry
# # docker push 554330630998.dkr.ecr.us-east-1.amazonaws.com/planet-downloader:$TAG
docker push $DOCKERTAGGED
# 
# # # introduce changes into deployment/docker-compose.yml file
# # # change the tag of the image
# # sed -i '' '4s/downloader:.*/downloader:'"$TAG"'/' deployment/docker-compose.yml
# 
# # # only needs to be run once per user
make configure-cluster
# # 
# # # run cluster
make cluster-up
# # 
# 
# # wait for cluster to come online. increase sleep if make run-task is 
# # run before cluster is set up
sleep 150s
# 
# # # run ECS task
make run-task
# # 
# # # find logs here (AWS CloudWatch): 
# # # https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEventViewer:group=ecs;stream=planet-downloader/planet-downloader/e677ac0d-2440-4ab3-bc1e-a45280476bae;start=2018-08-27T15:38:08Z
# # # WARN: this is the example URL
# # 
# # # after finishing your work kill the cluster
# # make cluster-down
