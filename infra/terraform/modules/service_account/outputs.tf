output "email" {
  description = "Email of the service account"
  value       = google_service_account.vm_sa.email
}

output "id" {
  description = "ID of the service account"
  value       = google_service_account.vm_sa.id
}
