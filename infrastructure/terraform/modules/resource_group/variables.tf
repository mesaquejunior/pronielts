variable "name" {
  description = "Name of the resource group"
  type        = string

  validation {
    condition     = can(regex("^rg-[a-z0-9-]+$", var.name))
    error_message = "Resource group name must start with 'rg-' and contain only lowercase letters, numbers, and hyphens."
  }
}

variable "location" {
  description = "Azure region where resources will be created"
  type        = string
  default     = "brazilsouth"

  validation {
    condition     = contains(["brazilsouth", "eastus", "eastus2", "westus2", "westeurope", "northeurope"], var.location)
    error_message = "Location must be one of the allowed Azure regions."
  }
}

variable "tags" {
  description = "Tags to apply to the resource group"
  type        = map(string)
  default     = {}
}
