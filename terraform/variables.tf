variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3a.xlarge"
}

variable "ami_id" {
  description = "AMI ID"
  type        = string
  default     = "ami-065778886ef8ec7c8"
}

variable "volume_size" {
  description = "Root volume size in GB"
  type        = number
  default     = 25
}

variable "volume_type" {
  description = "Volume type"
  type        = string
  default     = "gp3"
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
  default     = "network-automation-key"
}

variable "instance_state" {
  description = "Instance state (running or stopped)"
  type        = string
  default     = "running"
}

variable "instance_name" {
  description = "Instance name"
  type        = string
  default     = "network-instance"
}
