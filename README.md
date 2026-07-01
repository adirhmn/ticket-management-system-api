# Contact Center Support Tickets API

A production-ready Python FastAPI service built to manage support tickets, complete with authentication, database migrations, containerization, and a robust CI/CD deployment guide.

---

## 📋 Project Deliverables (Quick Links)

To assist the review process, here are the direct links to the key components and deliverables in this repository:

1. **Architecture & CI/CD Diagrams**: Documented with Mermaid diagrams in [ARCHITECTURE.md](ARCHITECTURE.md).
2. **Local Test Results**: Static log of the Pytest suite run is in [test_results.txt](test_results.txt).
3. **AWS Cost-Control Screenshot**: Located in [zero_spend_budget.png](zero_spend_budget.png) (Zero-Spend Budget configuration).
4. **Terraform Infrastructure as Code**: Located in the [terraform/](terraform/) directory.
5. **Live Production API**: [http://15.232.154.184](http://15.232.154.184) (Interactive Swagger Docs: [http://15.232.154.184/docs](http://15.232.154.184/docs)).
6. **Postman Collection for Endpoint Testing**: Import [ticket-management-system-api.postman_collection.json](ticket-management-system-api.postman_collection.json).

---

## 🛠️ Tech Stack
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (Local Dev & Production) & SQLite (Unit Testing only)

- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- **Reverse Proxy**: [Nginx](https://www.nginx.com/)
- **CI/CD**: [GitHub Actions](https://github.com/features/actions)
- **Testing**: [Pytest](https://docs.pytest.org/)

---

## ⚙️ Environment Variables

Copy the `.env.example` file to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable Name  | Type   | Example / Default | Description |
|:---|:---|:---|:---|
| `ENV` | String | `development` / `production` | Set to `production` for live deployments to suppress raw debug logs. |
| `DATABASE_URL` | String | `postgresql://postgres:postgres@db:5432/tickets` | The database connection string. |
| `API_KEY` | String | `test-api-key-12345` | The secret key required in the `X-API-Key` HTTP header. |
| `POSTGRES_USER` | String | `postgres` | PostgreSQL username (used for Docker database container initialization). |
| `POSTGRES_PASSWORD` | String | `postgres` | PostgreSQL password (used for Docker database container initialization). |
| `POSTGRES_DB` | String | `tickets` | PostgreSQL database name (used for Docker database container initialization). |
| `CORS_ORIGINS` | String | `*` | Comma-separated list of allowed origins for CORS. Use `*` to allow all. |

---

## 💻 Local Setup & Development

### Method A: Running with Docker (Recommended)
This method starts the PostgreSQL database and FastAPI backend in Docker containers.

1. Ensure you have Docker and Docker Compose installed.
2. Spin up the development server:
   ```bash
   docker compose up --build
   ```
3. The server will run at `http://localhost:8000`. Hot-reloading is enabled via host volume mapping.
4. Access the interactive API docs at `http://localhost:8000/docs`.

### Method B: Running Locally (Bare Metal)
1. Install Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your local `.env` file to point to your PostgreSQL database (for example, the database container running in Docker):
   ```ini
   ENV=development
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tickets
   API_KEY=test-api-key-12345
   ```

4. Run the Alembic database migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
6. The server will run at `http://localhost:8000`.

---

## 🧪 Running Tests

We use **pytest** to verify API endpoint functionality, authentication, and validation logic.

Execute the test suite locally:
```bash
pytest -v
```

This runs isolated tests using a temporary SQLite database file (`test_temp.db`) which is cleaned up automatically after execution.

---

## 📖 API Documentation

All routes (except `/health`) require the HTTP header `X-API-Key: <your_secret_key>`.

### 📂 Support Tickets Router

#### `POST /tickets`
Creates a new support ticket.
- **Request Body**:
  ```json
  {
    "customer_name": "Jane Doe",
    "customer_email": "jane@example.com",
    "subject": "System crash",
    "description": "The app freezes on launch.",
    "status": "open",       // Optional (Default: "open", Options: open, in_progress, resolved, closed)
    "priority": "medium"    // Optional (Default: "low", Options: low, medium, high, urgent)
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "success": true,
    "message": "Ticket created successfully.",
    "data": {
      "id": "c7a8813a-a1b7-4a0b-8d07-cc6238b1d9bf",
      "customer_name": "Jane Doe",
      "customer_email": "jane@example.com",
      "subject": "System crash",
      "description": "The app freezes on launch.",
      "status": "open",
      "priority": "medium",
      "created_at": "2026-06-30T06:40:00Z",
      "updated_at": "2026-06-30T06:40:00Z"
    }
  }
  ```

#### `GET /tickets`
Lists tickets with search, filtering, and pagination support.
- **Query Parameters**:
  - `page` (Integer, default `1`): Page offset.
  - `page_size` (Integer, default `20`): Page size limit (Max: 100).
  - `status` (String, optional): Filter by exact status.
  - `customer_name` (String, optional): Partial match for customer name.
  - `customer_email` (String, optional): Partial match for email.
  - `subject` (String, optional): Partial match for subject.
  - `search` (String, optional): Broad search matching across name, email, subject, or description.
- **Example Call**:
  ```
  GET /tickets?status=open&page=1&page_size=10
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Tickets retrieved successfully.",
    "data": [
      {
        "id": "c7a8813a-a1b7-4a0b-8d07-cc6238b1d9bf",
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "subject": "System crash",
        "description": "The app freezes on launch.",
        "status": "open",
        "priority": "medium",
        "created_at": "2026-06-30T06:40:00Z",
        "updated_at": "2026-06-30T06:40:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 1,
      "total_pages": 1
    }
  }
  ```

#### `GET /tickets/{ticket_id}`
Retrieves a specific ticket by its UUID.
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Ticket retrieved successfully.",
    "data": {
      "id": "c7a8813a-a1b7-4a0b-8d07-cc6238b1d9bf",
      "customer_name": "Jane Doe",
      "customer_email": "jane@example.com",
      "subject": "System crash",
      "description": "The app freezes on launch.",
      "status": "open",
      "priority": "medium",
      "created_at": "2026-06-30T06:40:00Z",
      "updated_at": "2026-06-30T06:40:00Z"
    }
  }
  ```
- **Response (404 Not Found)**:
  ```json
  {
    "success": false,
    "message": "Ticket with ID 'c7a8813a-a1b7-4a0b-8d07-cc6238b1d9bf' not found.",
    "data": null
  }
  ```

#### `PATCH /tickets/{ticket_id}`
Partially updates a ticket (e.g., status, priority, or description).
- **Request Body**: (all fields optional)
  ```json
  {
    "status": "in_progress",
    "priority": "high"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Ticket updated successfully.",
    "data": {
      "id": "c7a8813a-a1b7-4a0b-8d07-cc6238b1d9bf",
      "customer_name": "Jane Doe",
      "customer_email": "jane@example.com",
      "subject": "System crash",
      "description": "The app freezes on launch.",
      "status": "in_progress",
      "priority": "high",
      "created_at": "2026-06-30T06:40:00Z",
      "updated_at": "2026-06-30T06:45:00Z"
    }
  }
  ```

#### `DELETE /tickets/{ticket_id}`
Deletes a ticket.
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Ticket with ID 'c7a8813a-a1b7-4a0b-8d07-cc6238b1d9bf' has been deleted.",
    "data": {
      "id": "c7a8813a-a1b7-4a0b-8d07-cc6238b1d9bf",
      "customer_name": "Jane Doe",
      "subject": "System crash"
    }
  }
  ```

### 📂 Utility Router

#### `GET /health`
Returns system status. **Does not require authentication**.
- **Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "timestamp": "2026-06-30T13:30:00Z"
  }
  ```
- **Response (503 Service Unavailable)**: (if database is down)
  ```json
  {
    "success": false,
    "message": "Database connection failed.",
    "data": null
  }
  ```

---

## 🚀 AWS EC2 Deployment Guide

Follow these steps to deploy this application to a fresh AWS EC2 Ubuntu instance.

### 1. Provision EC2 Instance (Manual or Terraform)

#### Option A: Automated Setup (Terraform - Recommended)
If you have Terraform installed, you can provision the network, security group, EC2 instance, and automatically bootstrap all dependencies (Docker, Git, Nginx, and the CloudWatch Agent) by running:
```bash
cd terraform
terraform init
terraform apply -var="key_name=YOUR_AWS_SSH_KEY_NAME" -var="alert_email=YOUR_EMAIL_FOR_ALERTS"
```
*Note: Providing `alert_email` is recommended to automatically provision AWS SNS topics and CloudWatch alarms for server uptime and Nginx 500 errors. If left blank, alarms and SNS topics will not be created.*

Once applied, it will output the public IP of your new instance, and you can skip directly to **Step 3 (Clone Repository)** as all dependencies are already pre-installed!

#### Option B: Manual Setup (AWS Web Console)
Go to the **AWS EC2 Console**, ensure your region is set to **Jakarta (`ap-southeast-3`)**, and click **Launch Instance**. Configure the following settings:

- **Name and Tags**: `ticket-management-system-instance`
- **Application and OS Image (AMI)**: Select the **Ubuntu** icon, then choose **Ubuntu Server 24.04 LTS (HVM), SSD Volume Type** (ensure it has the *"Free tier eligible"* badge).
- **Instance Type**: `t3.micro` (Note: `t2.micro` is not available in the Jakarta region; `t3.micro` is the Free Tier eligible instance type in `ap-southeast-3`).
- **Key Pair (login)**: Select your existing SSH key pair, or click *Create new key pair* (download the `.pem` file and keep it secure).
- **Network Settings**:
  - **VPC / Subnet**: Use the default VPC and select a public subnet.
  - **Auto-assign Public IP**: Set to **Enable** (critical to receive a public IP address).
  - **Firewall (Security Groups)**: Select *Create security group* and configure the following inbound rules:
    - `Port 22` (SSH): Whitelist your local machine's public IP address.
      - *Note for CI/CD*: The GitHub Actions pipeline will dynamically whitelist its own runner IP during deploy, and revoke it immediately after completion.
    - `Port 80` (HTTP): Allow `0.0.0.0/0` (public access).
    - `Port 443` (HTTPS): Allow `0.0.0.0/0` (public access for SSL).
    - *Keep Port 5432 (PostgreSQL) closed to the outside world.*
- **Configure Storage**: Keep the default **8 GiB** (or up to 30 GiB) gp3 SSD volume, which is Free Tier eligible.
- **Advanced Details (IAM Instance Profile)**:
  - Scroll down to **IAM instance profile** and select the IAM Role with the `CloudWatchAgentServerPolicy` policy attached. This is required for the CloudWatch Agent to authenticate and stream logs to CloudWatch.

### 2. Set Up the Server (Skip if you used Option A)

SSH into your EC2 instance and run these commands to install Docker, Docker Compose, Nginx, and the CloudWatch Agent:

```bash
# Update OS packages
sudo apt update && sudo apt upgrade -y

# Install prerequisites, Git, Nginx and Wget
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release git nginx wget

# Add official Docker GPG key & repository
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine & Docker Compose Plugin
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Configure permissions for the default ubuntu user
sudo usermod -aG docker ubuntu

# Enable core system services
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl enable nginx
sudo systemctl start nginx
```
*Note: Log out and log back in (or exit SSH and reconnect) for the Docker user group permissions to take effect.*

### 3. Clone Repository and Configure Env
1. Clone your repository onto the EC2 host into `/home/ubuntu/ticket-management-system-api`.
2. Navigate to `/home/ubuntu/ticket-management-system-api`.
3. Create a production `.env` file:

   ```bash
   nano .env
   ```
   Add the variables:
   ```ini
   ENV=production
   DATABASE_URL=postgresql://postgres:secure_production_password@db:5432/tickets
   API_KEY=your_production_secret_key

   # PostgreSQL Database Configuration
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=secure_production_password
   POSTGRES_DB=tickets

   # CORS Configuration
   CORS_ORIGINS=*
   ```

### 4. Configure Nginx Reverse Proxy
1. Create a configuration file for the API:
   ```bash
   sudo nano /etc/nginx/sites-available/ticket-api
   ```
2. Copy-paste the content of `nginx.conf` into this file.
3. Enable the configuration and test Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/ticket-api /etc/nginx/sites-enabled/
   sudo rm /etc/nginx/sites-enabled/default  # Remove default Nginx page
   sudo nginx -t                             # Verify syntax is correct
   sudo systemctl restart nginx
   ```

### 5. Run Initial Deployment
Run the automated deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 🛠️ Server Operations & Maintenance

### How to View Logs
- **FastAPI / App Logs**:
  ```bash
  docker compose -f docker-compose.prod.yml logs -f web
  ```
- **Nginx Access Logs**:
  ```bash
  sudo tail -f /var/log/nginx/ticket_api_access.log
  ```
- **Nginx Error Logs**:
  ```bash
  sudo tail -f /var/log/nginx/ticket_api_error.log
  ```
- **PostgreSQL Database Logs**:
  ```bash
  docker compose -f docker-compose.prod.yml logs -f db
  ```

### How to Restart the Services
- **Restart Backend Containers**:
  ```bash
  docker compose -f docker-compose.prod.yml restart
  ```
- **Restart Nginx Reverse Proxy**:
  ```bash
  sudo systemctl restart nginx
  ```

### How to Clean Up / Destroy Resources
- **Stop Containers and Remove Volumes** (warning: this will wipe database contents!):
  ```bash
  docker compose -f docker-compose.prod.yml down -v
  ```

- **AWS Cleanup**:
  - Terminate the EC2 instance.
  - Delete any associated EBS volumes.
  - Delete Key Pairs if no longer needed.

---

## 📈 Production Monitoring, Alerting, & CloudWatch

> [!NOTE]
> If you deployed using **Option A: Automated Setup (Terraform)**, all monitoring, logging, and alerting infrastructure (CloudWatch log groups, metric filters, SNS alert topics, alarms) and the installation/configuration of the CloudWatch Agent on EC2 are **already fully configured and automated for you**. You can skip this section entirely. The manual instructions below are only necessary if you deployed using Option B.

To support production-grade logging, monitoring, and alerting, the system can be integrated with native AWS monitoring services:

### 1. CloudWatch Logs Integration
For production workloads, application and proxy logs should be forwarded to AWS CloudWatch for persistent retention and queryability.

- **Option A: AWS CloudWatch Agent (Recommended)**
  Follow these steps to manually install, configure, and start the CloudWatch agent on the EC2 host:

  1. **Download and Install the Agent**:
     ```bash
     wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
     sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
     ```
  2. **Create the Configuration File**:
     Create the configuration file to tail and forward the Nginx logs:
     ```bash
     sudo nano /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
     ```
     Copy and paste the configuration:
     ```json
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
                 "log_group_name": "/aws/ec2/ticket-management-system/nginx-access",
                 "log_stream_name": "{instance_id}",
                 "retention_in_days": 7
               },
               {
                 "file_path": "/var/log/nginx/ticket_api_error.log",
                 "log_group_name": "/aws/ec2/ticket-management-system/nginx-error",
                 "log_stream_name": "{instance_id}",
                 "retention_in_days": 7
               }
             ]
           }
         }
       }
     }
     ```
  3. **Enable and Start the Agent Service**:
     ```bash
     sudo systemctl enable amazon-cloudwatch-agent
     sudo systemctl start amazon-cloudwatch-agent
     ```

- **Option B: Docker awslogs Logging Driver**
  Alternatively, route stdout of the web service directly to CloudWatch in `docker-compose.prod.yml`:
  ```yaml
  logging:
    driver: awslogs
    options:
      awslogs-group: "ticket-management-system/app"
      awslogs-region: "ap-southeast-3"
      awslogs-stream: "web-logs"
  ```
  *(Note: The EC2 Instance Profile must have the `CloudWatchAgentServerPolicy` IAM policy attached).*

### 2. Basic Uptime Check
Configure an external uptime check targeting the `/health` check route:
- **AWS Route 53 Health Check**: Create a health check pointing to `http://<EC2_PUBLIC_IP>/health` with a 30-second interval. It will ping the server, verify the HTTP status code is `200`, and confirm database connectivity (since `/health` executes a DB ping).
- **Alternative**: Use free-tier external checkers like [UptimeRobot](https://uptimerobot.com) to monitor endpoint availability.

### 3. Error Alerting
Connect the monitoring indicators to alerts:
- **Uptime Alarm**: Configure an AWS CloudWatch Alarm based on the Route 53 health check status. If the status is `Unhealthy` for 2 consecutive periods, trigger an **SNS (Simple Notification Service)** topic.
- **Log Metric Alarms**: Create a CloudWatch Metric Filter on `ticket-management-system/nginx-error` or `ticket-management-system/app` logs searching for `"error"` or `"HTTP/1.1 500"`. Set an Alarm to trigger if the count exceeds a threshold (e.g., > 5 errors in 1 minute) and send email/Slack notifications via SNS.

---

## 🛡️ Cost Control

To prevent unwanted AWS bills, follow these guidelines:
1. **AWS Budget**: Navigate to **AWS Budgets** in the Billing Console and create a budget template with a **Zero spend budget** setting. This notifies your email when forecasted or actual spend exceeds $0.01.
2. **Avoid NAT Gateways & Load Balancers**: These resources carry an hourly cost even if they are idle. This architecture routes traffic directly to the EC2 instance, which falls under the AWS Free Tier.
3. **Budget Configuration**: A reference screenshot of the configured budget alert is located in the root directory as [zero_spend_budget.png](zero_spend_budget.png) to demonstrate the active zero-spend thresholds.
