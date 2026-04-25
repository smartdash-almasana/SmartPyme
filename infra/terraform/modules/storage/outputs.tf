output "disk_self_link" {
  description = "Self link of the data disk"
  value       = google_compute_disk.data_disk.self_link
}

output "disk_name" {
  description = "Name of the data disk"
  value       = google_compute_disk.data_disk.name
}
