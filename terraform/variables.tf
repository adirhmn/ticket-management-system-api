variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-southeast-3" # Jakarta Region
}

variable "project_name" {
  description = "Prefix for resource names"
  type        = string
  default     = "ticket-management-system"
}

variable "instance_type" {
  description = "EC2 instance size (Free Tier eligible)"
  type        = string
  default     = "t3.micro"
}


variable "key_name" {
  description = "Name of the pre-existing AWS SSH Key Pair to associate with the EC2 instance"
  type        = string
}

variable "alert_email" {
  description = "Email address to receive production alarms (e.g. alerts@company.com). Leave blank to disable alarms and SNS topics."
  type        = string
  default     = ""
}

