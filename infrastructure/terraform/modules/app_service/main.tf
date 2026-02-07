# App Service Module
# Creates Azure App Service Plan and Linux Web App for FastAPI backend

# App Service Plan
resource "azurerm_service_plan" "this" {
  name                = "${var.name}-plan"
  location            = var.location
  resource_group_name = var.resource_group_name

  os_type  = "Linux"
  sku_name = var.sku_name

  tags = var.tags
}

# Linux Web App
resource "azurerm_linux_web_app" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.this.id

  https_only = true

  # Managed Identity for Key Vault access
  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = var.always_on

    # Python runtime
    application_stack {
      python_version = var.python_version
    }

    # Health check
    health_check_path                 = var.health_check_path
    health_check_eviction_time_in_min = 5

    # CORS configuration
    dynamic "cors" {
      for_each = length(var.cors_allowed_origins) > 0 ? [1] : []
      content {
        allowed_origins     = var.cors_allowed_origins
        support_credentials = false
      }
    }

    # IP restrictions
    dynamic "ip_restriction" {
      for_each = var.ip_restrictions
      content {
        name       = ip_restriction.value.name
        ip_address = ip_restriction.value.ip_address
        priority   = ip_restriction.value.priority
        action     = ip_restriction.value.action
      }
    }
  }

  # Application settings (environment variables)
  app_settings = merge(
    {
      "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
      "SCM_DO_BUILD_DURING_DEPLOYMENT"      = "true"
    },
    var.app_settings
  )

  # Logs configuration
  logs {
    http_logs {
      file_system {
        retention_in_days = 7
        retention_in_mb   = 35
      }
    }
    application_logs {
      file_system_level = "Information"
    }
  }

  tags = var.tags

  lifecycle {
    ignore_changes = [
      # Ignore changes to app_settings that are managed externally
      # (e.g., by deployment pipelines)
    ]
  }
}

# Key Vault access policy for the App Service managed identity
resource "azurerm_key_vault_access_policy" "app_service" {
  count = var.enable_key_vault && !var.key_vault_rbac_enabled ? 1 : 0

  key_vault_id = var.key_vault_id
  tenant_id    = azurerm_linux_web_app.this.identity[0].tenant_id
  object_id    = azurerm_linux_web_app.this.identity[0].principal_id

  secret_permissions = [
    "Get",
    "List",
  ]
}

# RBAC role assignment for Key Vault (when RBAC is enabled)
resource "azurerm_role_assignment" "key_vault_secrets_user" {
  count = var.enable_key_vault && var.key_vault_rbac_enabled ? 1 : 0

  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_web_app.this.identity[0].principal_id
}

# Startup command for FastAPI
resource "azurerm_app_service_custom_hostname_binding" "this" {
  count = var.custom_hostname != null ? 1 : 0

  hostname            = var.custom_hostname
  app_service_name    = azurerm_linux_web_app.this.name
  resource_group_name = var.resource_group_name
}
