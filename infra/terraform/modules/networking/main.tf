resource "google_compute_network" "vpc" {
  name                    = "smartpyme-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "subnet" {
  name          = "smartpyme-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
  project       = var.project_id
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "smartpyme-allow-ssh"
  network = google_compute_network.vpc.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = var.ssh_source_cidrs
  target_tags   = ["smartpyme-vm"]
}
