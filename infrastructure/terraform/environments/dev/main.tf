# Main Terraform Configuration for Development Environment
# Orchestrates all modules to deploy PronIELTS to Azure

# Get current Azure client configuration
data "azurerm_client_config" "current" {}

# Local values for naming conventions
locals {
  name_prefix = "${var.project}-${var.environment}"
  common_tags = merge(var.tags, {
    terraform   = "true"
    environment = var.environment
  })

  # Storage account name must be lowercase alphanumeric only (3-24 chars)
  storage_account_name = lower(replace("st${var.project}${var.environment}", "-", ""))
}

# Generate random password for PostgreSQL if not provided
resource "random_password" "postgresql" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Generate encryption key for audio files
resource "random_password" "encryption_key" {
  length  = 32
  special = false
}

# Generate secret key for JWT
resource "random_password" "secret_key" {
  length  = 64
  special = false
}

# =============================================================================
# Resource Group
# =============================================================================
module "resource_group" {
  source = "../../modules/resource_group"

  name     = "rg-${local.name_prefix}"
  location = var.location
  tags     = local.common_tags
}

# =============================================================================
# Key Vault (created first for secret storage)
# =============================================================================
module "key_vault" {
  source = "../../modules/key_vault"

  name                       = "kv-${local.name_prefix}"
  location                   = module.resource_group.location
  resource_group_name        = module.resource_group.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  enable_rbac_authorization  = true
  purge_protection_enabled   = false # Dev environment - allow purge
  soft_delete_retention_days = 7

  tags = local.common_tags
}

# =============================================================================
# PostgreSQL Database
# =============================================================================
module "postgresql" {
  source = "../../modules/sql_database"

  name                = "psql-${local.name_prefix}"
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name

  administrator_login    = var.postgresql_admin_login
  administrator_password = coalesce(var.postgresql_admin_password, random_password.postgresql.result)

  sku_name           = var.postgresql_sku_name
  postgresql_version = "15"
  storage_mb         = var.postgresql_storage_mb

  database_name          = "pronielts"
  backup_retention_days  = 7
  high_availability_mode = "Disabled"

  allow_azure_services = true

  tags = local.common_tags
}

# =============================================================================
# Blob Storage
# =============================================================================
module "storage" {
  source = "../../modules/blob_storage"

  name                     = local.storage_account_name
  location                 = module.resource_group.location
  resource_group_name      = module.resource_group.name
  account_tier             = "Standard"
  account_replication_type = var.storage_replication_type
  container_name           = "audio-recordings"

  versioning_enabled         = false
  soft_delete_enabled        = true
  soft_delete_retention_days = 7

  cors_allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://*.azurestaticapps.net"
  ]

  tags = local.common_tags
}

# =============================================================================
# Speech Service
# =============================================================================
module "speech" {
  source = "../../modules/speech_service"

  name                = "speech-${local.name_prefix}"
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  sku_name            = var.speech_sku_name

  tags = local.common_tags
}

# =============================================================================
# App Service (FastAPI Backend)
# =============================================================================
module "app_service" {
  source = "../../modules/app_service"

  name                = "app-${local.name_prefix}"
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name

  sku_name       = var.app_service_sku_name
  python_version = "3.12"
  always_on      = var.app_service_sku_name != "F1" # Not available on Free tier

  health_check_path = "/health"

  key_vault_id           = module.key_vault.id
  key_vault_rbac_enabled = true

  cors_allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://${module.static_web_app.default_hostname}"
  ]

  app_settings = {
    # Application settings
    "MOCK_MODE"                   = "false"
    "BLOB_CONTAINER_NAME"         = "audio-recordings"
    "SPEECH_REGION"               = var.location
    "ALGORITHM"                   = "HS256"
    "ACCESS_TOKEN_EXPIRE_MINUTES" = "60"

    # Key Vault references (secrets loaded at runtime)
    "DATABASE_URL"           = "@Microsoft.KeyVault(SecretUri=${module.key_vault.uri}secrets/database-url/)"
    "BLOB_CONNECTION_STRING" = "@Microsoft.KeyVault(SecretUri=${module.key_vault.uri}secrets/blob-connection-string/)"
    "SPEECH_KEY"             = "@Microsoft.KeyVault(SecretUri=${module.key_vault.uri}secrets/speech-key/)"
    "ENCRYPTION_KEY"         = "@Microsoft.KeyVault(SecretUri=${module.key_vault.uri}secrets/encryption-key/)"
    "SECRET_KEY"             = "@Microsoft.KeyVault(SecretUri=${module.key_vault.uri}secrets/secret-key/)"

    # Startup command for FastAPI
    "STARTUP_COMMAND" = "gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
  }

  tags = local.common_tags
}

# =============================================================================
# Static Web App (React Admin)
# =============================================================================
module "static_web_app" {
  source = "../../modules/static_web_app"

  name                = "swa-${local.name_prefix}"
  location            = "eastus2" # Static Web Apps have limited regions
  resource_group_name = module.resource_group.name

  sku_tier = "Free"
  sku_size = "Free"

  tags = local.common_tags
}

# =============================================================================
# Store Secrets in Key Vault
# =============================================================================

# Database connection string
resource "azurerm_key_vault_secret" "database_url" {
  name         = "database-url"
  value        = "postgresql://${module.postgresql.administrator_login}:${coalesce(var.postgresql_admin_password, random_password.postgresql.result)}@${module.postgresql.server_fqdn}:5432/${module.postgresql.database_name}?sslmode=require"
  key_vault_id = module.key_vault.id

  depends_on = [module.key_vault]
}

# Blob storage connection string
resource "azurerm_key_vault_secret" "blob_connection_string" {
  name         = "blob-connection-string"
  value        = module.storage.primary_connection_string
  key_vault_id = module.key_vault.id

  depends_on = [module.key_vault]
}

# Speech service key
resource "azurerm_key_vault_secret" "speech_key" {
  name         = "speech-key"
  value        = module.speech.primary_access_key
  key_vault_id = module.key_vault.id

  depends_on = [module.key_vault]
}

# Encryption key
resource "azurerm_key_vault_secret" "encryption_key" {
  name         = "encryption-key"
  value        = base64encode(random_password.encryption_key.result)
  key_vault_id = module.key_vault.id

  depends_on = [module.key_vault]
}

# Secret key for JWT
resource "azurerm_key_vault_secret" "secret_key" {
  name         = "secret-key"
  value        = random_password.secret_key.result
  key_vault_id = module.key_vault.id

  depends_on = [module.key_vault]
}

# PostgreSQL admin password (for reference)
resource "azurerm_key_vault_secret" "postgresql_password" {
  name         = "postgresql-admin-password"
  value        = coalesce(var.postgresql_admin_password, random_password.postgresql.result)
  key_vault_id = module.key_vault.id

  depends_on = [module.key_vault]
}
