#!/bin/bash

set -e

echo "Installing AWS CLI, Terraform..."

# Update and install dependencies
sudo apt-get update -y
sudo apt-get install -y curl wget unzip gnupg software-properties-common


# Install Containerlab
echo "Installing Containerlab..."
curl -sL https://containerlab.dev/setup | sudo -E bash -s "all"

# # Install Docker
# echo "Installing Docker..."
# curl -fsSL https://get.docker.com | sudo sh

# # Configure Docker permissions
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl restart docker.services
wait
# Restart Docker
# sudo systemctl restart docker.service

echo ""
echo "Installation complete!"
echo "Note: Log out and back in for Docker group changes to take effect."
