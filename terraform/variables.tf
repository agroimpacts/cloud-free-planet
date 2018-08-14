variable "region" {
    type        = "string"
    description = "AWS Region"
    default     = "us-east-1"
}

variable "emr_service_role" {
  type        = "string"
  description = "EMR service role"
  default     = "EMR_DefaultRole"
}

variable "emr_instance_profile" {
  type        = "string"
  description = "EMR instance profile"
  default     = "EMR_EC2_DefaultRole"
}

variable "ecs_instance_profile" {
  type        = "string"
  description = "ECS instance profile"
  default     = "ecsInstanceRole"
}

variable "ecs_ami" {
    type        = "string"
    description = "AMI to use for the ECS Instance"
    default     = "ami-9eb4b1e5"
}

variable "s3_log_uri" {
    type        = "string"
    description = "Where EMR logs will be sent"
}

variable "subnet" {
  type = "string"
  description = "AWS subnet identifier"
}

variable "key_name" {
    type        = "string"
    description = "The name of the EC2 secret key (primarily for SSH access)"
}

variable "jupyterhub_port" {
    type        = "string"
    description = "The port on which to connect to JupyterHub"
    default     = "8000"
}

variable "worker_count" {
    type        = "string"
    description = "The number of worker nodes"
    default     = "1"
}

variable "bid_price" {
  type        = "string"
  description = "Bid Price"
  default     = "0.07"
}

variable "s3_rpm_uri" {
  type        = "string"
  description = "S3 path containing RPMs (e.g. s3://bucket/containing/rpms/)"
}

variable "s3_notebook_uri" {
  type        = "string"
  description = "S3 path for notebooks (e.g. s3://bucket/containing/notebooks/)"
}

variable "bs_bucket" {
  type        = "string"
  description = "S3 Bucket containing the bootstrap script (e.g. bucket if the whole path is s3://bucket/containing/bootstrap)"
}

variable "bs_prefix" {
  type        = "string"
  description = "The prefix of the bootstrap script within the s3 bucket (e.g. containing/bootstrap if the whole path is s3://bucket/containing/bootstrap/bootstrap.sh)"
}

variable "geopyspark_jars" {
  type        = "string"
  description = "Comma-separated list of URIs pointing to GeoPySpark jars"
  default     = "s3://geopyspark-dependency-jars/geotrellis-backend-assembly-0.4.2.jar"
}

variable "geopyspark_uri" {
  type        = "string"
  description = "URI from which the GeoPySpark Python code is to be obtained"
  default     = "https://github.com/locationtech-labs/geopyspark/archive/cfe5a5b7ce8ef9b1961bb4144f4efced2ed0c652.zip"
}

variable "rasterframes_sha" {
  type = "string"
  description = "Rasterframes Github SHA"
  default = "92c70f27cb48e167bb204886f5d5360b6c253d15"
}

variable "rasterframes_version" {
  type = "string"
  description = "Version of Rasterframes artifacts"
  default = "0.7.1-SNAPSHOT"
}

variable "user_defined_sg" {
  type        = "string"
  description = "A flag to indicate if the user will supply in `security_group` the security group id to start the cluster in"
  default     = "true"
}

variable "security_group" {
  type        = "string"
  description = "The security group to use for the cluster if user_defined_sg=true"
  default     = "sg-ac924ee6"
}
