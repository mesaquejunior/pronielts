# Speech Service Module
# Creates Azure Cognitive Services Speech resource for pronunciation assessment

resource "azurerm_cognitive_account" "speech" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name

  kind     = "SpeechServices"
  sku_name = var.sku_name

  # Custom subdomain for REST API access
  custom_subdomain_name = var.custom_subdomain_name

  # Network access
  public_network_access_enabled = var.public_network_access_enabled

  # Managed identity
  dynamic "identity" {
    for_each = var.enable_managed_identity ? [1] : []
    content {
      type = "SystemAssigned"
    }
  }

  tags = var.tags
}
