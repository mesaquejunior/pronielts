variable "name" {
  description = "Name of the App Service (must be globally unique)"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9][a-zA-Z0-9-]{0,58}[a-zA-Z0-9]$", var.name))
    error_message = "App Service name must be 2-60 characters, alphanumeric and hyphens."
  }
}

variable "location" {
  description = "Azure region for the App Service"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "sku_name" {
  description = "SKU for the App Service Plan"
  type        = string
  default     = "B1"

  validation {
    condition = contains([
      "F1", "D1", "B1", "B2", "B3",
      "S1", "S2", "S3",
      "P1v2", "P2v2", "P3v2",
      "P1v3", "P2v3", "P3v3",
      "P0v3", "P1mv3", "P2mv3", "P3mv3", "P4mv3", "P5mv3"
    ], var.sku_name)
    error_message = "Invalid SKU name. Common options: F1 (Free), B1-B3 (Basic), S1-S3 (Standard), P1v3-P3v3 (Premium)."
  }
}

variable "python_version" {
  description = "Python version for the App Service"
  type        = string
  default     = "3.12"

  validation {
    condition     = contains(["3.9", "3.10", "3.11", "3.12"], var.python_version)
    error_message = "Python version must be 3.9, 3.10, 3.11, or 3.12."
  }
}

variable "always_on" {
  description = "Keep the app always running (not available on Free tier)"
  type        = bool
  default     = false
}

variable "health_check_path" {
  description = "Path for health check endpoint"
  type        = string
  default     = "/health"
}

variable "app_settings" {
  description = "Application settings (environment variables)"
  type        = map(string)
  default     = {}
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = []
}

variable "ip_restrictions" {
  description = "IP restrictions for the App Service"
  type = list(object({
    name       = string
    ip_address = string
    priority   = number
    action     = string
  }))
  default = []
}

variable "key_vault_id" {
  description = "ID of the Key Vault for managed identity access"
  type        = string
  default     = null
}

variable "key_vault_rbac_enabled" {
  description = "Whether Key Vault uses RBAC authorization"
  type        = bool
  default     = true
}

variable "custom_hostname" {
  description = "Custom hostname for the App Service"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
