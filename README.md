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

### 1. Set GitHub Secrets & Permissions
In your GitHub repo → Settings:
1. **Secrets:** (Secrets and variables → Actions) Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` (Ensure the token has "Read & Write" permissions).
2. **Permissions:** (Actions → General → Workflow permissions) Ensure **Read and write permissions** is checked so the CI pipeline can push updated manifests back to the repo.

### 2. Provision AWS infrastructure
We use Terraform to physically build the VPC and spin up the EC2 server (`t3.small` is recommended over `t2.micro` to maintain enough RAM for Kubernetes).
```bash
# Strongly recommended to prevent GitHub's 100MB file limit from blocking your push
echo "terraform/.terraform/\n*.tfstate\n*.tfstate.backup" >> .gitignore

cd terraform
terraform init
terraform apply -auto-approve
# Note the printed ec2_public_ip output
```

### 3. Configure the server with Ansible
Update `ansible/inventory.ini` with your new EC2 IP address.
Because Ansible does not natively run on Windows PowerShell, you can use an isolated Docker container to securely execute the configuration playbook:
```powershell
cd ../ansible
docker run --rm -v "${pwd}:/ansible" -v "$env:USERPROFILE\.ssh\id_rsa:/tmp/id_rsa:ro" -e ANSIBLE_HOST_KEY_CHECKING=False -w /ansible willhallonline/ansible:latest sh -c "mkdir -p ~/.ssh && cp /tmp/id_rsa ~/.ssh/id_rsa && chmod 600 ~/.ssh/id_rsa && ansible-playbook -i inventory.ini playbook.yml"
```
*(MicroK8s and ArgoCD will be installed. Copy the generated ArgoCD Admin Password at the end!)*

### 4. Push code to trigger CI
```bash
cd ..
git add .
git commit -m "Infrastructure setup and manifest configurations"
git push origin main
```
*GitHub Actions will automatically build the newest Docker containers, push them up to Docker Hub, and physically update `k8s/manifests.yaml` in this repository with the finalized image tags!*

### 5. Finalize Deployment (ArgoCD)
With your EC2 server configured and code pushed, tell ArgoCD to watch your GitHub repository and automatically deploy it to the Kubernetes Pods:
```powershell
# Send your local app.yaml configuration directly into the EC2 Kubernetes cluster
cat argocd/app.yaml | ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no ubuntu@<YOUR_EC2_IP> "microk8s kubectl apply -f -"
```

### 6. Access the App
- **Live App**: `http://<YOUR_EC2_IP>:30080`
- **ArgoCD UI**: `https://<YOUR_EC2_IP>:30443` (Username: `admin`, Password is from Step 3)

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
