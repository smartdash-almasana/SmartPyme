output "instance_name" {
  description = "Name of the VM instance."
  value       = google_compute_instance.vm.name
}

output "instance_self_link" {
  description = "Self link of the VM instance."
  value       = google_compute_instance.vm.self_link
}

output "network_ip" {
  description = "Internal network IP of the VM instance."
  value       = google_compute_instance.vm.network_interface[0].network_ip
}
