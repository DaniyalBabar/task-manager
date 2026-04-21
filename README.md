# TaskFlow — Task Manager

A 3-service microservices app deployed on AWS EC2 using Docker, Terraform, Ansible, Kubernetes (microk8s), and ArgoCD.

## Architecture

```
Frontend (Nginx)  →  Backend (FastAPI)  →  Database (PostgreSQL)
     :80                  :8000                   :5432
```

---

## Prerequisites

- AWS account with programmatic access (`aws configure`)
- Terraform v1.5+
- Ansible 2.14+
- Docker Hub account
- SSH key pair (`~/.ssh/id_rsa` + `~/.ssh/id_rsa.pub`)

---

## Deployment Steps

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/task-manager.git
cd task-manager
```

### 2. Set GitHub Secrets
In your GitHub repo → Settings → Secrets → Actions, add:
- `DOCKERHUB_USERNAME` — your Docker Hub username
- `DOCKERHUB_TOKEN` — your Docker Hub access token

### 3. Update placeholders
Replace all `YOUR_DOCKERHUB_USERNAME` in `k8s/manifests.yaml` with your actual Docker Hub username.
Replace `YOUR_GITHUB_USERNAME` in `argocd/app.yaml` with your GitHub username.

### 4. Provision AWS infrastructure with Terraform
```bash
cd terraform
terraform init
terraform plan
terraform apply
# Note the ec2_public_ip from the output
```

### 5. Configure the server with Ansible
```bash
cd ../ansible
# Edit inventory.ini — replace YOUR_EC2_IP with the IP from step 4
nano inventory.ini

ansible-playbook -i inventory.ini playbook.yml
```
This installs microk8s, enables addons, and installs ArgoCD.
The ArgoCD admin password will be printed at the end.

### 6. Push code to trigger CI
```bash
git add .
git commit -m "initial commit"
git push origin main
```
GitHub Actions will build Docker images, push to Docker Hub, and update `k8s/manifests.yaml` with the new image tags.

### 7. Configure ArgoCD
```bash
# SSH into the EC2 instance
ssh ubuntu@YOUR_EC2_IP

# Apply the ArgoCD app manifest
microk8s kubectl apply -f /path/to/argocd/app.yaml
```
ArgoCD will automatically sync the cluster with `k8s/manifests.yaml`.

### 8. Access the app
- **App**: `http://YOUR_EC2_IP:30080`
- **ArgoCD UI**: `https://YOUR_EC2_IP:30443` (user: `admin`, password from Ansible output)

---

## File Structure

```
task-manager/
├── services/
│   ├── frontend/         # Nginx + HTML/JS app
│   │   ├── src/index.html
│   │   ├── nginx.conf
│   │   └── Dockerfile
│   └── backend/          # Python FastAPI REST API
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── terraform/            # AWS infra (VPC, EC2, SG)
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── ansible/              # Server config + microk8s + ArgoCD
│   ├── inventory.ini
│   └── playbook.yml
├── k8s/                  # Kubernetes manifests
│   └── manifests.yaml
├── .github/workflows/    # GitHub Actions CI
│   └── ci.yml
├── argocd/               # ArgoCD app config
│   └── app.yaml
└── README.md
```
