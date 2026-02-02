variable "name" {
  description = "Name of the Static Web App"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9][a-zA-Z0-9-]{0,38}[a-zA-Z0-9]$", var.name))
    error_message = "Name must be 2-40 characters, alphanumeric and hyphens."
  }
}

variable "location" {
  description = "Azure region for the Static Web App (limited regions available)"
  type        = string
  default     = "eastus2"

  validation {
    condition = contains([
      "westus2", "centralus", "eastus2", "westeurope", "eastasia", "eastasiastage"
    ], var.location)
    error_message = "Static Web Apps are only available in: westus2, centralus, eastus2, westeurope, eastasia."
  }
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "sku_tier" {
  description = "SKU tier for the Static Web App"
  type        = string
  default     = "Free"

  validation {
    condition     = contains(["Free", "Standard"], var.sku_tier)
    error_message = "SKU tier must be 'Free' or 'Standard'."
  }
}

variable "sku_size" {
  description = "SKU size for the Static Web App"
  type        = string
  default     = "Free"

  validation {
    condition     = contains(["Free", "Standard"], var.sku_size)
    error_message = "SKU size must be 'Free' or 'Standard'."
  }
}

variable "custom_domain" {
  description = "Custom domain for the Static Web App"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
