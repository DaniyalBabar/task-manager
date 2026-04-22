variable "aws_region" {
  description = "The AWS region to deploy infrastructure"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.medium"
}

variable "public_key_path" {
  description = "Path to the local SSH public key"
  default     = "~/.ssh/id_rsa.pub"
}

variable "ami_id" {
  description = "Ubuntu 22.04 AMI ID for the selected region"
  type        = string
  # Note: AMI IDs change frequently and are region-specific. 
  # You can find the latest Ubuntu 22.04 AMI ID in the AWS EC2 Console launch wizard.
  default     = "ami-04b70fa74e45c3917" # Example placeholder for us-east-1
}