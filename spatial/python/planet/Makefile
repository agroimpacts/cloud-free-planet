CONFIG_NAME := planet-downloader-config-${USER}
CLUSTER_NAME := planet-downloader-cluster-${USER}
INSTANCE_TYPE := c4.large
INSTANCE_ROLE := PlanetDownloaderECSRole
SIZE := 1
KEYPAIR := daunnc
SUBNETS := subnet-638f0c39
VPC := vpc-e48b1a9d
SECURITY_GROUP := sg-ac924ee6

login-aws-registry: 
	eval `aws ecr get-login --no-include-email --region us-east-1`

configure-cluster:
	ecs-cli configure --cluster ${CLUSTER_NAME} --region us-east-1 --config-name ${CONFIG_NAME}

cluster-down:
	ecs-cli down --cluster-config ${CONFIG_NAME}

cluster-up:
	ecs-cli up --keypair ${KEYPAIR} \
			   --instance-role ${INSTANCE_ROLE} \
			   --size ${SIZE} \
			   --instance-type ${INSTANCE_TYPE} \
			   --cluster-config ${CONFIG_NAME} \
			   --subnets ${SUBNETS} \
			   --vpc ${VPC} \
			   --security-group ${SECURITY_GROUP} \
			   --force

run-task:
	cd deployment; ecs-cli compose up --create-log-groups --cluster-config ${CONFIG_NAME}

stop-task:
	cd deployment; ecs-cli compose down

run-local:
	docker-compose run planet-downloader
	# or you can use docker directly
	# docker run \
	#   -v ${PWD}/catalog:/opt/planet/catalog \
	#   -v ${PWD}/cfg:/opt/planet/cfg daunnc/planet-downloader:latest python planet_download_tiff.py
