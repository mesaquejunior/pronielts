# Variables for Development Environment

variable "project" {
  description = "Project name"
  type        = string
  default     = "pronielts"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "brazilsouth"
}

# PostgreSQL Configuration
variable "postgresql_admin_login" {
  description = "PostgreSQL administrator login"
  type        = string
  default     = "pronieltsadmin"
}

variable "postgresql_admin_password" {
  description = "PostgreSQL administrator password"
  type        = string
  sensitive   = true
}

variable "postgresql_sku_name" {
  description = "PostgreSQL SKU"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "postgresql_storage_mb" {
  description = "PostgreSQL storage in MB"
  type        = number
  default     = 32768
}

# App Service Configuration
variable "app_service_sku_name" {
  description = "App Service Plan SKU"
  type        = string
  default     = "B1"
}

# Speech Service Configuration
variable "speech_sku_name" {
  description = "Speech Service SKU (F0=Free, S0=Standard)"
  type        = string
  default     = "F0"
}

# Storage Configuration
variable "storage_replication_type" {
  description = "Storage account replication type"
  type        = string
  default     = "LRS"
}

# Tags
variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    project     = "pronielts"
    environment = "development"
    managed_by  = "terraform"
  }
}
