# PronIELTS Terraform Infrastructure

This directory contains Terraform configurations to deploy PronIELTS to Microsoft Azure.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Azure Resource Group                          │
│                         (rg-pronielts-dev)                           │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Key Vault   │  │   Storage    │  │    Speech Service        │  │
│  │  (Secrets)   │  │  (Audio)     │  │  (Pronunciation API)     │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘  │
│         │                 │                        │                 │
│         └─────────────────┼────────────────────────┘                 │
│                           │                                          │
│                    ┌──────┴───────┐                                  │
│                    │  App Service │                                  │
│                    │  (FastAPI)   │                                  │
│                    └──────┬───────┘                                  │
│                           │                                          │
│                    ┌──────┴───────┐                                  │
│                    │  PostgreSQL  │                                  │
│                    │  Flexible    │                                  │
│                    └──────────────┘                                  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Static Web App (React Admin)                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Azure CLI** - Install and login:
   ```bash
   az login
   az account set --subscription "<subscription-id>"
   ```

2. **Terraform** >= 1.5.0:
   ```bash
   brew install terraform  # macOS
   ```

3. **Azure Subscription** with permissions to create resources

## Directory Structure

```
infrastructure/terraform/
├── README.md                    # This file
├── modules/                     # Reusable Terraform modules
│   ├── resource_group/          # Azure Resource Group
│   ├── key_vault/               # Azure Key Vault (secrets)
│   ├── sql_database/            # PostgreSQL Flexible Server
│   ├── blob_storage/            # Azure Storage Account
│   ├── speech_service/          # Azure Cognitive Services Speech
│   ├── app_service/             # Azure App Service (FastAPI)
│   └── static_web_app/          # Azure Static Web App (React)
├── environments/
│   ├── dev/                     # Development environment
│   │   ├── main.tf              # Main orchestration
│   │   ├── variables.tf         # Variable definitions
│   │   ├── outputs.tf           # Output values
│   │   ├── providers.tf         # Provider configuration
│   │   ├── backend.tf           # Remote state config
│   │   └── terraform.tfvars     # Dev-specific values
│   └── prod/                    # Production environment (future)
└── shared/
    └── backend-setup/           # Terraform state storage setup
```

## Quick Start

### 1. Setup Remote State Storage (Optional but Recommended)

```bash
cd infrastructure/terraform/shared/backend-setup
terraform init
terraform apply
```

This creates an Azure Storage Account to store Terraform state remotely.

### 2. Deploy Development Environment

```bash
cd infrastructure/terraform/environments/dev

# Initialize Terraform
terraform init

# Preview changes
terraform plan -var-file="terraform.tfvars"

# Apply changes
terraform apply -var-file="terraform.tfvars"
```

### 3. Set PostgreSQL Password (Optional)

You can set the password via environment variable:

```bash
export TF_VAR_postgresql_admin_password="YourSecurePassword123!"
terraform apply -var-file="terraform.tfvars"
```

If not set, a random password will be generated and stored in Key Vault.

## Cost Estimates

### Development Environment (~$28/month)

| Resource | SKU | Monthly Cost |
|----------|-----|--------------|
| PostgreSQL Flexible Server | B_Standard_B1ms | ~$13 |
| App Service | B1 | ~$13 |
| Storage Account | Standard_LRS | ~$2 |
| Speech Service | F0 (Free) | $0 |
| Key Vault | Standard | ~$0.03/secret |
| Static Web App | Free | $0 |

### Production Environment (~$375+/month)

| Resource | SKU | Monthly Cost |
|----------|-----|--------------|
| PostgreSQL Flexible Server | GP_Standard_D2s_v3 + HA | ~$200 |
| App Service | P1v3 | ~$160 |
| Storage Account | Standard_GRS | ~$5 |
| Speech Service | S0 | Pay-per-use |
| Key Vault | Standard | ~$0.03/secret |
| Static Web App | Standard | ~$9 |

## Modules Reference

### resource_group

Creates an Azure Resource Group.

| Variable | Description | Default |
|----------|-------------|---------|
| `name` | Resource group name | Required |
| `location` | Azure region | `brazilsouth` |
| `tags` | Resource tags | `{}` |

### key_vault

Creates Azure Key Vault for secrets management.

| Variable | Description | Default |
|----------|-------------|---------|
| `name` | Key Vault name (globally unique) | Required |
| `sku_name` | SKU (`standard` or `premium`) | `standard` |
| `enable_rbac_authorization` | Use RBAC vs access policies | `true` |
| `purge_protection_enabled` | Enable purge protection | `false` |

### sql_database

Creates Azure Database for PostgreSQL Flexible Server.

| Variable | Description | Default |
|----------|-------------|---------|
| `name` | Server name (globally unique) | Required |
| `administrator_login` | Admin username | Required |
| `administrator_password` | Admin password | Required |
| `sku_name` | Compute SKU | `B_Standard_B1ms` |
| `postgresql_version` | PostgreSQL version | `15` |
| `storage_mb` | Storage in MB | `32768` |

### blob_storage

Creates Azure Storage Account with blob container.

| Variable | Description | Default |
|----------|-------------|---------|
| `name` | Storage account name (globally unique) | Required |
| `account_tier` | Performance tier | `Standard` |
| `account_replication_type` | Redundancy type | `LRS` |
| `container_name` | Blob container name | `audio-recordings` |

### speech_service

Creates Azure Cognitive Services Speech resource.

| Variable | Description | Default |
|----------|-------------|---------|
| `name` | Service name | Required |
| `sku_name` | SKU (`F0` free or `S0` standard) | `F0` |

### app_service

Creates Azure App Service Plan and Linux Web App.

| Variable | Description | Default |
|----------|-------------|---------|
| `name` | App name (globally unique) | Required |
| `sku_name` | Plan SKU (`F1`, `B1`, `P1v3`, etc.) | `B1` |
| `python_version` | Python version | `3.12` |
| `health_check_path` | Health endpoint | `/health` |
| `app_settings` | Environment variables | `{}` |

### static_web_app

Creates Azure Static Web App for React frontend.

| Variable | Description | Default |
|----------|-------------|---------|
| `name` | App name | Required |
| `location` | Region (limited) | `eastus2` |
| `sku_tier` | SKU tier | `Free` |

## Post-Deployment Steps

### 1. Run Database Migrations

```bash
# SSH into App Service
az webapp ssh --resource-group rg-pronielts-dev --name app-pronielts-dev

# Run migrations
cd /home/site/wwwroot
alembic upgrade head
```

### 2. Deploy Backend Code

```bash
# Create deployment package
cd backend
zip -r ../backend.zip . -x "*.pyc" -x "__pycache__/*" -x ".env" -x "env/*"

# Deploy to App Service
az webapp deployment source config-zip \
  --resource-group rg-pronielts-dev \
  --name app-pronielts-dev \
  --src ../backend.zip
```

### 3. Deploy React Admin

Use GitHub Actions with the Static Web Apps API key, or:

```bash
cd web
npm run build

# Deploy using SWA CLI
npx @azure/static-web-apps-cli deploy ./dist \
  --deployment-token <api_key_from_terraform_output>
```

## Troubleshooting

### Common Issues

1. **Key Vault Access Denied**
   - Ensure the App Service managed identity has Key Vault Secrets User role
   - Check RBAC assignments: `az role assignment list --scope <key_vault_id>`

2. **PostgreSQL Connection Failed**
   - Verify firewall rules allow Azure services
   - Check SSL mode in connection string (`sslmode=require`)

3. **Speech Service Quota Exceeded**
   - F0 tier has 5 hours/month limit
   - Upgrade to S0 for production

### Useful Commands

```bash
# View Terraform state
terraform show

# List outputs
terraform output

# Destroy all resources (CAUTION!)
terraform destroy -var-file="terraform.tfvars"

# Import existing resource
terraform import azurerm_resource_group.example /subscriptions/.../resourceGroups/example
```

## Security Best Practices

1. **Secrets**: All sensitive values stored in Key Vault
2. **Managed Identity**: App Service uses system-assigned identity
3. **Network**: PostgreSQL firewall restricts access
4. **SSL/TLS**: Enforced on all connections
5. **RBAC**: Role-based access control for Key Vault

## Contributing

1. Format code: `terraform fmt -recursive`
2. Validate: `terraform validate`
3. Plan changes before applying
4. Use meaningful variable names and descriptions
