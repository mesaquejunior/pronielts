output "id" {
  description = "The ID of the Speech service"
  value       = azurerm_cognitive_account.speech.id
}

output "name" {
  description = "The name of the Speech service"
  value       = azurerm_cognitive_account.speech.name
}

output "endpoint" {
  description = "The endpoint of the Speech service"
  value       = azurerm_cognitive_account.speech.endpoint
}

output "primary_access_key" {
  description = "The primary access key for the Speech service"
  value       = azurerm_cognitive_account.speech.primary_access_key
  sensitive   = true
}

output "secondary_access_key" {
  description = "The secondary access key for the Speech service"
  value       = azurerm_cognitive_account.speech.secondary_access_key
  sensitive   = true
}

output "region" {
  description = "The Azure region of the Speech service"
  value       = azurerm_cognitive_account.speech.location
}

output "identity_principal_id" {
  description = "The principal ID of the managed identity (if enabled)"
  value       = try(azurerm_cognitive_account.speech.identity[0].principal_id, null)
}
