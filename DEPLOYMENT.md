# TaskFlow Deployment Guide

This guide provides detailed, step-by-step instructions for deploying the TaskFlow microservices application on AWS EC2 using Terraform, Ansible, MicroK8s, and ArgoCD.

## Prerequisites

Before you begin, ensure you have the following installed and configured on your local machine:
- **AWS CLI**: Installed and configured (`aws configure`) with appropriate permissions.
- **Terraform**: v1.5+ for infrastructure provisioning.
- **Ansible**: v2.14+ for server configuration.
- **Docker**: For running Ansible playbook via container (especially useful on Windows).
- **Git**: For version control.
- **SSH Key Pair**: Available at `~/.ssh/id_rsa` and `~/.ssh/id_rsa.pub`.
- **Docker Hub Account**: For pushing container images.
- **GitHub Repository**: With Actions enabled.

---

## Step 1: Configure GitHub Repository Secrets & Permissions

Your GitHub Actions pipeline requires permission to push images to Docker Hub and update your repository manifests.

1. Navigate to your GitHub repository.
2. Go to **Settings** > **Secrets and variables** > **Actions**.
3. Add the following repository secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username.
   - `DOCKERHUB_TOKEN`: A Docker Hub Personal Access Token (Ensure it has "Read & Write" permissions).
4. Go to **Settings** > **Actions** > **General**.
5. Scroll down to **Workflow permissions**.
6. Select **Read and write permissions** and click **Save**. This allows the CI pipeline to push updated manifest files back to your repository.

---

## Step 2: Provision AWS Infrastructure with Terraform

We use Terraform to automatically create a VPC, security groups, and an EC2 instance (`t3.small` recommended for running Kubernetes).

1. Open your terminal and navigate to the Terraform directory:
   ```bash
   cd terraform
   ```
2. Prevent Terraform state files from being tracked by Git (recommended to avoid hitting GitHub file size limits):
   ```bash
   echo -e "terraform/.terraform/\n*.tfstate\n*.tfstate.backup" >> ../.gitignore
   ```
3. Initialize the Terraform environment:
   ```bash
   terraform init
   ```
4. Apply the Terraform configuration to provision resources:
   ```bash
   terraform apply -auto-approve
   ```
5. Note down the public IP address of the newly created EC2 instance from the output (`ec2_public_ip`).

---

## Step 3: Configure the EC2 Server with Ansible

Ansible will connect to your new EC2 instance, install necessary dependencies, and set up MicroK8s and ArgoCD.

1. Navigate to the Ansible directory:
   ```bash
   cd ../ansible
   ```
2. Update the `inventory.ini` file. Replace the placeholder with your actual EC2 public IP:
   ```ini
   [webservers]
   <YOUR_EC2_IP> ansible_user=ubuntu
   ```
3. Execute the Ansible playbook. If you are on Windows (PowerShell), use the following Docker command to run Ansible:
   ```powershell
   docker run --rm -v "${pwd}:/ansible" -v "$env:USERPROFILE\.ssh\id_rsa:/tmp/id_rsa:ro" -e ANSIBLE_HOST_KEY_CHECKING=False -w /ansible willhallonline/ansible:latest sh -c "mkdir -p ~/.ssh && cp /tmp/id_rsa ~/.ssh/id_rsa && chmod 600 ~/.ssh/id_rsa && ansible-playbook -i inventory.ini playbook.yml"
   ```
   *Note: If you are on Linux/macOS, you can run directly:*
   ```bash
   ansible-playbook -i inventory.ini playbook.yml
   ```
4. **Crucial:** At the end of the playbook execution, it will print the **ArgoCD Admin Password**. Copy and save this password; you will need it later!

---

## Step 4: Trigger the CI/CD Pipeline

With the infrastructure running, push your codebase to GitHub to trigger the CI workflow.

1. Navigate back to the root of your project:
   ```bash
   cd ..
   ```
2. Stage, commit, and push your changes:
   ```bash
   git add .
   git commit -m "Configure infrastructure and deployment manifests"
   git push origin main
   ```
3. Go to the **Actions** tab in your GitHub repository and watch the pipeline execute. It will build the Docker images, push them to Docker Hub, and automatically update the `k8s/manifests.yaml` file with the new image tags.

---

## Step 5: Finalize ArgoCD Deployment

Now that your Kubernetes cluster is running and your images are built, configure ArgoCD to synchronize your application.

1. Execute the following command from your local terminal to apply the ArgoCD application configuration to your remote cluster. Replace `<YOUR_EC2_IP>` with your EC2 public IP:
   ```powershell
   cat argocd/app.yaml | ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no ubuntu@<YOUR_EC2_IP> "microk8s kubectl apply -f -"
   ```
2. ArgoCD will now continuously monitor your GitHub repository and automatically apply changes to the Kubernetes pods.

---

## Step 6: Access Your Application

- **Live Application:** Access the frontend at `http://<YOUR_EC2_IP>:30080`
- **ArgoCD Dashboard:** Access the UI at `https://<YOUR_EC2_IP>:30443`
  - **Username:** `admin`
  - **Password:** (The password generated at the end of Step 3)
