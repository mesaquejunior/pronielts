# Terraform Provider Configuration for Development Environment

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }

  # Authentication via environment variables:
  # ARM_SUBSCRIPTION_ID - Azure subscription ID
  # ARM_TENANT_ID       - Azure AD tenant ID
  # ARM_CLIENT_ID       - Service Principal app ID (for CI/CD)
  # ARM_CLIENT_SECRET   - Service Principal password (for CI/CD)
  # OR use Azure CLI authentication: `az login`
}

provider "azuread" {
  # Uses same authentication as azurerm
}

provider "random" {
  # No configuration needed
}
