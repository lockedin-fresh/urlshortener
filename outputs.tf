output "public_ip" {
  value = aws_eip.app_eip.public_ip
}

output "instance_id" {
  value = aws_instance.app_server.id
}
