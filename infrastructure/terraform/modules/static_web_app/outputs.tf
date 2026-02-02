output "id" {
  description = "The ID of the Static Web App"
  value       = azurerm_static_site.this.id
}

output "name" {
  description = "The name of the Static Web App"
  value       = azurerm_static_site.this.name
}

output "default_hostname" {
  description = "The default hostname of the Static Web App"
  value       = azurerm_static_site.this.default_host_name
}

output "default_url" {
  description = "The default URL of the Static Web App"
  value       = "https://${azurerm_static_site.this.default_host_name}"
}

output "api_key" {
  description = "API key for deployment (use in GitHub Actions)"
  value       = azurerm_static_site.this.api_key
  sensitive   = true
}
