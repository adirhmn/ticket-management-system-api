output "instance_public_ip" {
  description = "Public IP address of the newly provisioned EC2 instance"
  value       = aws_instance.ticket_api_instance.public_ip
}

output "instance_public_dns" {
  description = "Public DNS address of the EC2 instance"
  value       = aws_instance.ticket_api_instance.public_dns
}

output "ssh_login_command" {
  description = "Quick SSH helper command to connect to the server"
  value       = "ssh -i <your-key-file.pem> ubuntu@${aws_instance.ticket_api_instance.public_ip}"
}

output "security_group_id" {
  description = "ID of the Security Group to be used in GitHub Actions for ephemeral IP whitelisting"
  value       = aws_security_group.ticket_api_sg.id
}
