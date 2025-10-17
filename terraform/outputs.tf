# Security Group
output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.network_sg.id
}

# Instance Information
output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.network_instance.id
}

output "instance_public_ip" {
  description = "Public IP address"
  value       = aws_instance.network_instance.public_ip
}

output "instance_private_ip" {
  description = "Private IP address"
  value       = aws_instance.network_instance.private_ip
}

output "instance_state" {
  description = "Instance state"
  value       = aws_ec2_instance_state.instance_state.state
}

output "public_dns" {
  description = "Public DNS name"
  value       = aws_instance.network_instance.public_dns
}

# SSH Connection String
output "ssh_command" {
  description = "SSH connection command"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.network_instance.public_ip}"
}
