# Development Environment Configuration
# Cost estimate: ~$28/month

project     = "pronielts"
environment = "dev"
location    = "brazilsouth"

# PostgreSQL (Burstable tier - budget friendly)
postgresql_admin_login = "pronieltsadmin"
# postgresql_admin_password = "" # Set via TF_VAR_postgresql_admin_password or will be auto-generated
postgresql_sku_name   = "B_Standard_B1ms" # ~$13/month
postgresql_storage_mb = 32768             # 32 GB

# App Service (Basic tier)
app_service_sku_name = "B1" # ~$13/month (supports always_on)

# Speech Service (Free tier - 5 hours/month)
speech_sku_name = "F0"

# Storage (Locally Redundant)
storage_replication_type = "LRS"

# Tags
tags = {
  project     = "pronielts"
  environment = "development"
  managed_by  = "terraform"
  cost_center = "development"
}
