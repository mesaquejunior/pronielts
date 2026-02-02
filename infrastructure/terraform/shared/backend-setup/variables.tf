variable "resource_group_name" {
  description = "Name of the resource group for Terraform state storage"
  type        = string
  default     = "rg-pronielts-tfstate"
}

variable "storage_account_name" {
  description = "Name of the storage account for Terraform state (must be globally unique, 3-24 chars, lowercase alphanumeric)"
  type        = string
  default     = "stpronieltstfstate"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage account name must be 3-24 characters, lowercase letters and numbers only."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "brazilsouth"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    project    = "pronielts"
    managed_by = "terraform"
    purpose    = "tfstate"
  }
}
