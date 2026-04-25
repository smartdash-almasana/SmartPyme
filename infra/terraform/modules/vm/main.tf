locals {
  data_device_name = "smartpyme-data"
  startup_script   = <<-EOT
    #!/usr/bin/env bash
    set -euo pipefail

    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 python3-venv python3-pip docker.io
    systemctl enable --now docker

    mkdir -p /data

    DISK_PATH="/dev/disk/by-id/google-${local.data_device_name}"
    if [ -e "$DISK_PATH" ]; then
      if ! blkid "$DISK_PATH" >/dev/null 2>&1; then
        mkfs.ext4 -F "$DISK_PATH"
      fi

      UUID="$(blkid -s UUID -o value "$DISK_PATH")"
      if ! grep -q "UUID=$UUID" /etc/fstab; then
        echo "UUID=$UUID /data ext4 defaults,nofail 0 2" >> /etc/fstab
      fi

      mountpoint -q /data || mount /data
    fi
  EOT
}

resource "google_compute_instance" "vm" {
  name         = var.name
  machine_type = var.machine_type
  zone         = var.zone
  project      = var.project_id
  tags         = ["smartpyme-vm"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      size  = 20
      type  = "pd-balanced"
    }
  }

  network_interface {
    network    = var.network_self_link
    subnetwork = var.subnetwork_self_link

    access_config {}
  }

  service_account {
    email = var.service_account_email
    scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring.write",
    ]
  }

  metadata_startup_script = local.startup_script

  dynamic "attached_disk" {
    for_each = var.attached_disk_self_link == null ? [] : [var.attached_disk_self_link]
    content {
      source      = attached_disk.value
      device_name = local.data_device_name
      mode        = "READ_WRITE"
    }
  }
}
