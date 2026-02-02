# Static Web App Module
# Creates Azure Static Web App for hosting React admin dashboard

resource "azurerm_static_site" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name

  sku_tier = var.sku_tier
  sku_size = var.sku_size

  tags = var.tags
}

# Custom domain (if provided)
resource "azurerm_static_site_custom_domain" "this" {
  count = var.custom_domain != null ? 1 : 0

  static_site_id  = azurerm_static_site.this.id
  domain_name     = var.custom_domain
  validation_type = "cname-delegation"
}
