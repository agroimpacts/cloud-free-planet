login-aws-registry: 
	eval `aws ecr get-login --no-include-email --region us-east-1`

configure-cluster:
	ecs-cli configure --cluster planet-downloader-cluster --region us-east-1 --config-name planet-downloader-config

cluster-down:
	ecs-cli down --cluster-config planet-downloader-config

cluster-up:
	ecs-cli up --keypair daunnc \
	           --capability-iam \
			   --size 1 \
			   --instance-type c4.large \
			   --cluster-config planet-downloader-config \
			   --subnets subnet-638f0c39 \
			   --vpc vpc-e48b1a9d \
			   --security-group sg-ac924ee6 \
			   --force

run-task:
	cd deployment; ecs-cli compose up --create-log-groups --cluster-config planet-downloader-config

stop-task:
	cd deployment; ecs-cli compose down
