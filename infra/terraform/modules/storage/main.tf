resource "google_compute_disk" "data_disk" {
  name    = var.name
  type    = var.type
  zone    = var.zone
  size    = var.size_gb
  project = var.project_id
}
