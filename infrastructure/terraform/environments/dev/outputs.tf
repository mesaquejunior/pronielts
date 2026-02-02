# Outputs for Development Environment

# =============================================================================
# Resource Group
# =============================================================================
output "resource_group_name" {
  description = "Name of the resource group"
  value       = module.resource_group.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = module.resource_group.location
}

# =============================================================================
# App Service (Backend API)
# =============================================================================
output "app_service_url" {
  description = "URL of the FastAPI backend"
  value       = module.app_service.default_url
}

output "app_service_name" {
  description = "Name of the App Service"
  value       = module.app_service.app_service_name
}

output "app_service_outbound_ips" {
  description = "Outbound IP addresses of the App Service (for firewall rules)"
  value       = module.app_service.outbound_ip_addresses
}

# =============================================================================
# Static Web App (React Admin)
# =============================================================================
output "static_web_app_url" {
  description = "URL of the React admin dashboard"
  value       = module.static_web_app.default_url
}

output "static_web_app_name" {
  description = "Name of the Static Web App"
  value       = module.static_web_app.name
}

output "static_web_app_api_key" {
  description = "API key for Static Web App deployment (use in GitHub Actions)"
  value       = module.static_web_app.api_key
  sensitive   = true
}

# =============================================================================
# PostgreSQL Database
# =============================================================================
output "postgresql_server_fqdn" {
  description = "FQDN of the PostgreSQL server"
  value       = module.postgresql.server_fqdn
}

output "postgresql_database_name" {
  description = "Name of the database"
  value       = module.postgresql.database_name
}

output "postgresql_admin_login" {
  description = "Administrator login for PostgreSQL"
  value       = module.postgresql.administrator_login
}

# =============================================================================
# Blob Storage
# =============================================================================
output "storage_account_name" {
  description = "Name of the storage account"
  value       = module.storage.storage_account_name
}

output "blob_container_name" {
  description = "Name of the audio recordings container"
  value       = module.storage.container_name
}

output "blob_endpoint" {
  description = "Primary blob endpoint URL"
  value       = module.storage.primary_blob_endpoint
}

# =============================================================================
# Speech Service
# =============================================================================
output "speech_service_name" {
  description = "Name of the Speech service"
  value       = module.speech.name
}

output "speech_region" {
  description = "Region of the Speech service"
  value       = module.speech.region
}

output "speech_endpoint" {
  description = "Endpoint of the Speech service"
  value       = module.speech.endpoint
}

# =============================================================================
# Key Vault
# =============================================================================
output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = module.key_vault.name
}

output "key_vault_uri" {
  description = "URI of the Key Vault"
  value       = module.key_vault.uri
}

# =============================================================================
# Deployment Commands
# =============================================================================
output "deployment_commands" {
  description = "Commands to deploy the application"
  value       = <<-EOT

    # Deploy Backend to App Service:
    az webapp deployment source config-zip \
      --resource-group ${module.resource_group.name} \
      --name ${module.app_service.app_service_name} \
      --src backend.zip

    # Run Database Migrations:
    az webapp ssh --resource-group ${module.resource_group.name} --name ${module.app_service.app_service_name}
    # Then run: alembic upgrade head

    # Deploy React Admin to Static Web App:
    # Use the AZURE_STATIC_WEB_APPS_API_KEY secret in GitHub Actions
    # Or use Azure Static Web Apps CLI:
    # swa deploy ./web/dist --deployment-token <api_key>

  EOT
}
