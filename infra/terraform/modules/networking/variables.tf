variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "zone" {
  description = "GCP zone"
  type        = string
}

variable "ssh_source_cidrs" {
  description = "CIDR ranges allowed for SSH access"
  type        = list(string)
}
