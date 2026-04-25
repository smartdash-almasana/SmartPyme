terraform {
  backend "local" {
    path = "terraform.tfstate"
  }

  # Backend remoto futuro:
  # backend "gcs" {
  #   bucket = "smartpyme-terraform-state"
  #   prefix = "environments/dev"
  # }
}
