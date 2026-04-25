resource "google_service_account" "vm_sa" {
  account_id   = var.vm_sa_account_id
  display_name = "SmartPyme VM Service Account"
  project      = var.project_id
}
