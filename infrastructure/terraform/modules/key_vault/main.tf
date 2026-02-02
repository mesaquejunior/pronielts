# Key Vault Module
# Securely stores secrets (DB password, Speech key, Encryption key, etc.)

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id != null ? var.tenant_id : data.azurerm_client_config.current.tenant_id

  sku_name = var.sku_name

  # Security settings
  enabled_for_deployment          = false
  enabled_for_disk_encryption     = false
  enabled_for_template_deployment = false
  enable_rbac_authorization       = var.enable_rbac_authorization
  purge_protection_enabled        = var.purge_protection_enabled
  soft_delete_retention_days      = var.soft_delete_retention_days

  # Network rules (allow Azure services by default)
  network_acls {
    bypass         = "AzureServices"
    default_action = var.network_default_action
  }

  tags = var.tags
}

# Grant access to the current user/service principal deploying Terraform
resource "azurerm_key_vault_access_policy" "deployer" {
  count = var.enable_rbac_authorization ? 0 : 1

  key_vault_id = azurerm_key_vault.this.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Purge",
    "Recover",
  ]
}

# RBAC role assignment for deployer (when RBAC is enabled)
resource "azurerm_role_assignment" "deployer_secrets" {
  count = var.enable_rbac_authorization ? 1 : 0

  scope                = azurerm_key_vault.this.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}
