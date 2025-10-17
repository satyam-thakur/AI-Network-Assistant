# Security Group - Allow SSH access
resource "aws_security_group" "network_sg" {
  name        = "network-instance-sg"
  description = "Allow SSH access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Change to specific IP for better security
  }

  ingress {
    from_port   = 50080
    to_port     = 50080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "network-instance-sg"
  }
}

# EC2 Instance
resource "aws_instance" "network_instance" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.network_sg.id]

  root_block_device {
    volume_size = var.volume_size
    volume_type = var.volume_type
  }

  tags = {
    Name = var.instance_name
  }
}

# Control instance state (running/stopped)
resource "aws_ec2_instance_state" "instance_state" {
  instance_id = aws_instance.network_instance.id
  state       = var.instance_state
}
