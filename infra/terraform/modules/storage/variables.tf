variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "zone" {
  description = "GCP zone"
  type        = string
}

variable "name" {
  description = "Name of the data disk"
  type        = string
}

variable "size_gb" {
  description = "Size of the data disk in GB"
  type        = number
}

variable "type" {
  description = "Type of the data disk"
  type        = string
  default     = "pd-balanced"
}
