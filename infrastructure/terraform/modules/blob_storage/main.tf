# Blob Storage Module
# Creates Azure Storage Account and container for audio recordings

resource "azurerm_storage_account" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name

  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  account_kind             = "StorageV2"

  # Security settings
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = true

  # Blob properties
  blob_properties {
    versioning_enabled = var.versioning_enabled

    dynamic "delete_retention_policy" {
      for_each = var.soft_delete_enabled ? [1] : []
      content {
        days = var.soft_delete_retention_days
      }
    }

    dynamic "container_delete_retention_policy" {
      for_each = var.soft_delete_enabled ? [1] : []
      content {
        days = var.soft_delete_retention_days
      }
    }

    # CORS rules for web access
    dynamic "cors_rule" {
      for_each = length(var.cors_allowed_origins) > 0 ? [1] : []
      content {
        allowed_origins    = var.cors_allowed_origins
        allowed_methods    = ["GET", "PUT", "POST", "DELETE", "HEAD", "OPTIONS"]
        allowed_headers    = ["*"]
        exposed_headers    = ["*"]
        max_age_in_seconds = 3600
      }
    }
  }

  tags = var.tags
}

# Create the audio recordings container
resource "azurerm_storage_container" "audio" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.this.name
  container_access_type = "private"
}

# Lifecycle management policy for audio files
resource "azurerm_storage_management_policy" "this" {
  count = var.enable_lifecycle_policy ? 1 : 0

  storage_account_id = azurerm_storage_account.this.id

  rule {
    name    = "delete-old-audio"
    enabled = true

    filters {
      prefix_match = ["${var.container_name}/"]
      blob_types   = ["blockBlob"]
    }

    actions {
      base_blob {
        delete_after_days_since_modification_greater_than = var.audio_retention_days
      }
    }
  }
}
