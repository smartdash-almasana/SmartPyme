variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "name" {
  description = "VM instance name."
  type        = string
}

variable "machine_type" {
  description = "VM machine type."
  type        = string
}

variable "zone" {
  description = "GCP zone."
  type        = string
}

variable "network_self_link" {
  description = "Self link of the VPC network."
  type        = string
}

variable "subnetwork_self_link" {
  description = "Self link of the subnet."
  type        = string
}

variable "service_account_email" {
  description = "Service account email for the VM."
  type        = string
}

variable "attached_disk_self_link" {
  description = "Optional self link of a persistent data disk."
  type        = string
  default     = null
}
