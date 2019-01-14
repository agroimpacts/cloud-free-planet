variable "test_key_name" {
    type        = "string"
    description = "The name of the EC2 secret key (primarily for SSH access)"
}

variable "test_key_path" {
    type        = "string"
    description = "The path to the EC2 secret key (primarily for SSH access)"
}


variable "instance_type" {
    type        = "string"
    description = "instance type for all worker nodes"
    default     = "m4.xlarge"
}

variable "bid_price" {
  type        = "string"
  description = "Bid Price, change depending on instance type"
  default     = "0.086"
}
