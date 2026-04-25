variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "GCP region."
  type        = string
}

variable "zone" {
  description = "GCP zone."
  type        = string
}

variable "dev_vm_instance_name" {
  description = "Name of the SmartPyme dev VM."
  type        = string
}

variable "ssh_source_cidrs" {
  description = "CIDR ranges allowed to connect by SSH."
  type        = list(string)

  validation {
    condition     = alltrue([for cidr in var.ssh_source_cidrs : cidr != "0.0.0.0/0"])
    error_message = "ssh_source_cidrs must not include 0.0.0.0/0."
  }
}

variable "data_disk_name" {
  description = "Name of the persistent data disk."
  type        = string
}

variable "data_disk_size_gb" {
  description = "Size of the persistent data disk in GB."
  type        = number
}

variable "data_disk_type" {
  description = "Type of the persistent data disk."
  type        = string
}

variable "vm_sa_account_id" {
  description = "Service account ID for the dev VM."
  type        = string
}
