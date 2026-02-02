# Resource Group Module
# Creates the Azure Resource Group that contains all other resources

resource "azurerm_resource_group" "this" {
  name     = var.name
  location = var.location

  tags = var.tags

  lifecycle {
    prevent_destroy = false
  }
}
