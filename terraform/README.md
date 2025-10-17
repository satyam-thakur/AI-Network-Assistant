### env_export
source .env

### aws cli to reboot instance
aws ec2 reboot-instances --instance-ids i-007a30f4aaa055f6d --region us-west-2

### terraform steps
terraform init
terraform plan
terraform apply -auto-approve
terraform destroy -auto-approve
terraform fmt
terraform validate

### Sync terraform out-of-state
terraform refresh
terraform refresh -target=aws_instance.network-instance
aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId' --output text
terraform import aws_instance.network_instance i-0abc1234567890
terraform refresh
terraform plan

terraform state list
terraform state rm aws_instance.my_vm
terraform refresh
terraform plan
