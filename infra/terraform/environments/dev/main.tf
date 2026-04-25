terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

module "networking" {
  source = "../../modules/networking"

  project_id       = var.project_id
  region           = var.region
  zone             = var.zone
  ssh_source_cidrs = var.ssh_source_cidrs
}

module "service_account" {
  source = "../../modules/service_account"

  project_id       = var.project_id
  vm_sa_account_id = var.vm_sa_account_id
}

module "data_disk" {
  source = "../../modules/storage"

  project_id = var.project_id
  zone       = var.zone
  name       = var.data_disk_name
  size_gb    = var.data_disk_size_gb
  type       = var.data_disk_type
}

module "dev_vm" {
  source = "../../modules/vm"

  project_id              = var.project_id
  name                    = var.dev_vm_instance_name
  machine_type            = "e2-medium"
  zone                    = var.zone
  network_self_link       = module.networking.network_self_link
  subnetwork_self_link    = module.networking.subnet_self_link
  service_account_email   = module.service_account.email
  attached_disk_self_link = module.data_disk.disk_self_link
}
