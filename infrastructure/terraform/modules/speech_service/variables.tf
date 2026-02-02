variable "name" {
  description = "Name of the Speech service resource"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}[a-zA-Z0-9]$", var.name)) || can(regex("^[a-zA-Z0-9]$", var.name))
    error_message = "Name must be 2-64 characters, alphanumeric and hyphens, start and end with alphanumeric."
  }
}

variable "location" {
  description = "Azure region for the Speech service"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "sku_name" {
  description = "SKU for the Speech service (F0 = Free, S0 = Standard)"
  type        = string
  default     = "F0"

  validation {
    condition     = contains(["F0", "S0"], var.sku_name)
    error_message = "SKU must be 'F0' (free tier, 5 hrs/month) or 'S0' (standard, pay-per-use)."
  }
}

variable "custom_subdomain_name" {
  description = "Custom subdomain name for the Speech service (required for some features)"
  type        = string
  default     = null
}

variable "public_network_access_enabled" {
  description = "Enable public network access"
  type        = bool
  default     = true
}

variable "enable_managed_identity" {
  description = "Enable system-assigned managed identity"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
