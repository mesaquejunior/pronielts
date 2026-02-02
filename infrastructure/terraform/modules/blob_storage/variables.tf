variable "name" {
  description = "Name of the storage account (must be globally unique, 3-24 characters, lowercase alphanumeric only)"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.name))
    error_message = "Storage account name must be 3-24 characters, lowercase letters and numbers only."
  }
}

variable "location" {
  description = "Azure region for the storage account"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "account_tier" {
  description = "Performance tier (Standard or Premium)"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Standard", "Premium"], var.account_tier)
    error_message = "Account tier must be 'Standard' or 'Premium'."
  }
}

variable "account_replication_type" {
  description = "Replication type (LRS, GRS, ZRS, GZRS, RAGRS, RAGZRS)"
  type        = string
  default     = "LRS"

  validation {
    condition     = contains(["LRS", "GRS", "ZRS", "GZRS", "RAGRS", "RAGZRS"], var.account_replication_type)
    error_message = "Replication type must be one of: LRS, GRS, ZRS, GZRS, RAGRS, RAGZRS."
  }
}

variable "container_name" {
  description = "Name of the blob container for audio recordings"
  type        = string
  default     = "audio-recordings"
}

variable "versioning_enabled" {
  description = "Enable blob versioning"
  type        = bool
  default     = false
}

variable "soft_delete_enabled" {
  description = "Enable soft delete for blobs and containers"
  type        = bool
  default     = true
}

variable "soft_delete_retention_days" {
  description = "Number of days to retain soft-deleted blobs"
  type        = number
  default     = 7

  validation {
    condition     = var.soft_delete_retention_days >= 1 && var.soft_delete_retention_days <= 365
    error_message = "Soft delete retention must be between 1 and 365 days."
  }
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = []
}

variable "enable_lifecycle_policy" {
  description = "Enable lifecycle management policy for audio retention"
  type        = bool
  default     = false
}

variable "audio_retention_days" {
  description = "Number of days to retain audio files before deletion"
  type        = number
  default     = 90
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
