output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = "1.2.3.4" # This will get overridden by main.tf 
}
