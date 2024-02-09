SERVICE_NAME ?= newell-source-data
SERVICE_VERSION ?= latest

AWS_ECR_ACCOUNT_ID ?= 275279264324
AWS_ECR_REGION ?= us-east-1
IMAGE_NAME="${AWS_ECR_ACCOUNT_ID}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com/${SERVICE_NAME}:${SERVICE_VERSION}"


.PHONY: source_data/build source_data/push

source_data/tofu:
	cd tofu && tofu init && tofu apply -auto-approve

source_data/push: source_data/build
	aws ecr get-login-password --region $(AWS_ECR_REGION) | docker login --username AWS --password-stdin $(AWS_ECR_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com
	docker push $(IMAGE_NAME)

source_data/build:
	docker build -t $(IMAGE_NAME) .



