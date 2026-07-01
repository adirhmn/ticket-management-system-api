terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Automatically fetch the public IP of whoever runs terraform apply
data "http" "my_ip" {
  url = "https://checkip.amazonaws.com"
}

# Fetch the default VPC to explicitly attach the security group
data "aws_vpc" "default" {
  default = true
}

# Fetch the latest official Ubuntu 24.04 LTS AMI (Canonical owner ID 099720109477)
data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd*/ubuntu-noble-24.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"]
}

# Create Security Group container
resource "aws_security_group" "ticket_api_sg" {
  name        = "${var.project_name}-sg"
  description = "Security Group for Support Ticket API (SSH and HTTP/HTTPS)"
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Name = "${var.project_name}-sg"
  }
}

# Ingress SSH rule for Local Developer (IP dynamic lookup)
resource "aws_vpc_security_group_ingress_rule" "ssh_dev" {
  security_group_id = aws_security_group.ticket_api_sg.id
  description       = "SSH Access for Local Developer (Dynamic checkip)"
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
  cidr_ipv4         = "${chomp(data.http.my_ip.response_body)}/32"
}

# Ingress HTTP rule (Public access)
resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.ticket_api_sg.id
  description       = "HTTP Access for Nginx reverse proxy"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

# Ingress HTTPS rule (Public access)
resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.ticket_api_sg.id
  description       = "HTTPS Access for secure web traffic"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

# Egress rule (Outbound unrestricted)
resource "aws_vpc_security_group_egress_rule" "allow_all" {
  security_group_id = aws_security_group.ticket_api_sg.id
  ip_protocol       = "-1" # Represents all protocols
  cidr_ipv4         = "0.0.0.0/0"
}

# IAM Role for EC2 Instance to access CloudWatch logs
resource "aws_iam_role" "ticket_api_role" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Attach standard CloudWatch Agent policy to the IAM Role
resource "aws_iam_role_policy_attachment" "cloudwatch_policy" {
  role       = aws_iam_role.ticket_api_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# Create IAM Instance Profile using the Role
resource "aws_iam_instance_profile" "ticket_api_profile" {
  name = "${var.project_name}-instance-profile"
  role = aws_iam_role.ticket_api_role.name
}

# Launch EC2 Instance and bootstrap dependencies on startup
resource "aws_instance" "ticket_api_instance" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  vpc_security_group_ids      = [aws_security_group.ticket_api_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.ticket_api_profile.name
  associate_public_ip_address = true

  root_block_device {
    volume_size           = 8
    volume_type           = "gp3"
    delete_on_termination = true
  }

  # User Data script runs automatically on the first server bootup
  user_data = <<-EOF
              #!/bin/bash
              # 1. Update system packages
              apt-get update && apt-get upgrade -y
              
              # 2. Install prerequisites, Git and Nginx
              apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release git nginx wget
              
              # 3. Add official Docker GPG key & repository
              mkdir -p /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
              echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
              
              # 4. Install Docker Engine & Docker Compose Plugin
              apt-get update
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
              
              # 5. Configure permissions for the default ubuntu user
              usermod -aG docker ubuntu
              
              # 6. Start and enable core system Nginx and Docker services
              systemctl start docker
              systemctl enable docker
              systemctl start nginx
              systemctl enable nginx
              
              # 7. Install and configure AWS CloudWatch Agent to forward Nginx logs
              wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
              dpkg -i -E ./amazon-cloudwatch-agent.deb
              
              cat <<'CONF' > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
              {
                "agent": {
                  "metrics_collection_interval": 60,
                  "run_as_user": "root"
                },
                "logs": {
                  "logs_collected": {
                    "files": {
                      "collect_list": [
                        {
                          "file_path": "/var/log/nginx/ticket_api_access.log",
                          "log_group_name": "/aws/ec2/${var.project_name}/nginx-access",
                          "log_stream_name": "{instance_id}",
                          "retention_in_days": 7
                        },
                        {
                          "file_path": "/var/log/nginx/ticket_api_error.log",
                          "log_group_name": "/aws/ec2/${var.project_name}/nginx-error",
                          "log_stream_name": "{instance_id}",
                          "retention_in_days": 7
                        }
                      ]
                    }
                  }
                }
              }
              CONF
              
              systemctl enable amazon-cloudwatch-agent
              systemctl start amazon-cloudwatch-agent
              EOF

  tags = {
    Name = "${var.project_name}-instance"
  }
}

