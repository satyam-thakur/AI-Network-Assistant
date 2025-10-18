# Terraform - Cloud Infrastructure Provisioning

This directory contains Terraform configuration to provision an AWS EC2 instance for running the AI Network Assistant lab (Containerlab + pyATS + Arista cEOS).

---

## Prerequisites

### 1. Install AWS CLI and Terraform

Use the provided installation script from the project root:

```bash
cd ..
./terraform.sh
```

This installs:
- **AWS CLI v2** - for AWS authentication and management
- **Terraform** - for infrastructure as code provisioning

### 2. Configure AWS Credentials

Set up your AWS access credentials (required before running Terraform):

```bash
aws configure
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-west-2`)
- Output format (e.g., `json`)

### 3. Set Environment Variables (.env)

Create a `.env` file in the project root (not in the terraform directory) with your configuration:

```bash
cat > ../.env << 'EOF'
# AWS Configuration
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Gemini API (for AI Agent)
GEMINI_API_KEY=your_gemini_api_key_here

# pyATS Testbed Path (update after SSH to instance)
PYATS_TESTBED_PATH=./containerlab/testbed_containerlab.yaml
EOF
```

**Note**: The `.env` file is already in `.gitignore` to prevent credential leaks.

To load environment variables:

```bash
source ../.env
```

---

## Configuration Files

- **`provider.tf`** - AWS provider configuration
- **`variables.tf`** - Input variables with defaults
- **`terraform.tfvars`** - Customize instance type, region, AMI, storage, state (running/stopped)
- **`main.tf`** - EC2 instance, security group, and instance state resources
- **`outputs.tf`** - Outputs like instance ID, public IP, SSH command

### Key Variables (edit `terraform.tfvars`)

```hcl
aws_region     = "us-west-2"
instance_type  = "t3a.xlarge"          # Adjust based on lab size
ami_id         = "ami-065778886ef8ec7c8"  # Ubuntu 22.04 LTS
instance_name  = "network-instance"
volume_size    = 25                     # GB
volume_type    = "gp3"
key_name       = "network-automation-key"  # Your SSH key name in AWS
instance_state = "running"              # or "stopped"
```

---

## Terraform Commands

### Initialize Terraform
Downloads provider plugins and initializes the working directory:

```bash
cd terraform
terraform init
```

### Plan (Preview Changes)
Shows what Terraform will create/modify/destroy:

```bash
terraform plan
```

### Apply (Deploy Infrastructure)
Creates the EC2 instance and security group:

```bash
terraform apply -auto-approve
```

After successful apply, you'll see outputs including:
- Instance ID
- Public IP address
- SSH command to connect

### Destroy (Tear Down)
Removes all Terraform-managed resources:

```bash
terraform destroy -auto-approve
```

**Warning**: This will permanently delete the EC2 instance and all data on it.

### Other Useful Commands

```bash
# Format Terraform files
terraform fmt

# Validate configuration syntax
terraform validate

# List managed resources
terraform state list

# Show current state
terraform show

# Refresh state (sync with actual AWS resources)
terraform refresh
```

---

## Managing Instance State

To stop/start the instance without destroying it, edit `terraform.tfvars`:

```hcl
instance_state = "stopped"  # or "running"
```

Then apply changes:

```bash
terraform apply -auto-approve
```

---

## AWS CLI Quick Commands

### Reboot Instance

```bash
aws ec2 reboot-instances --instance-ids <instance-id> --region us-west-2
```

### Describe Instances

```bash
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]' \
  --output table
```

### Get Instance ID

```bash
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].InstanceId' \
  --output text
```

---

## Post-Deployment

After provisioning the EC2 instance, use the SSH command from Terraform outputs to connect:

```bash
ssh -i ~/.ssh/network-automation-key.pem ubuntu@<public-ip>
```

Refer to the main project README for setting up Containerlab and the AI Network Assistant on the instance.

---

## Troubleshooting

### Import Existing Resources

If an EC2 instance exists but is not in Terraform state:

```bash
terraform import aws_instance.network_instance i-0abc1234567890
terraform refresh
terraform plan
```

### Remove Resource from State

```bash
terraform state rm aws_instance.network_instance
terraform refresh
```

### State Sync Issues

```bash
terraform refresh -target=aws_instance.network_instance
terraform plan
```

---

## Security Considerations

- **SSH Key**: Ensure your SSH key pair (`key_name`) exists in AWS before running Terraform
- **Security Group**: Default allows SSH (port 22) and port 50080 from `0.0.0.0/0`. Restrict to your IP for production.
- **Credentials**: Never commit `.env` or `.tfvars` files with real credentials
- **Instance State**: Set `instance_state = "stopped"` when not in use to save costs

---

## Cost Optimization

- Use `instance_state = "stopped"` when not actively using the lab
- Choose appropriate instance type (t3a.xlarge is suitable for multi-node Containerlab)
- Clean up with `terraform destroy` when done with testing

---
