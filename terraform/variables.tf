variable "aws_region" {
  description = "The AWS region to deploy infrastructure"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.medium"
}
