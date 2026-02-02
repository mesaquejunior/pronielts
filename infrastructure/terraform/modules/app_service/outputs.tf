output "app_service_id" {
  description = "The ID of the App Service"
  value       = azurerm_linux_web_app.this.id
}

output "app_service_name" {
  description = "The name of the App Service"
  value       = azurerm_linux_web_app.this.name
}

output "default_hostname" {
  description = "The default hostname of the App Service"
  value       = azurerm_linux_web_app.this.default_hostname
}

output "default_url" {
  description = "The default URL of the App Service"
  value       = "https://${azurerm_linux_web_app.this.default_hostname}"
}

output "outbound_ip_addresses" {
  description = "List of outbound IP addresses for the App Service"
  value       = split(",", azurerm_linux_web_app.this.outbound_ip_addresses)
}

output "possible_outbound_ip_addresses" {
  description = "List of possible outbound IP addresses for the App Service"
  value       = split(",", azurerm_linux_web_app.this.possible_outbound_ip_addresses)
}

output "identity_principal_id" {
  description = "The principal ID of the managed identity"
  value       = azurerm_linux_web_app.this.identity[0].principal_id
}

output "identity_tenant_id" {
  description = "The tenant ID of the managed identity"
  value       = azurerm_linux_web_app.this.identity[0].tenant_id
}

output "service_plan_id" {
  description = "The ID of the App Service Plan"
  value       = azurerm_service_plan.this.id
}
