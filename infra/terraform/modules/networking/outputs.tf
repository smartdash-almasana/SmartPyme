output "network_self_link" {
  description = "Self link of the VPC network"
  value       = google_compute_network.vpc.self_link
}

output "subnet_self_link" {
  description = "Self link of the subnet"
  value       = google_compute_subnetwork.subnet.self_link
}

output "network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.vpc.name
}
