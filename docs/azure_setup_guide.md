# Azure Setup Guide for PronIELTS

This guide walks you through setting up all Azure resources needed for the PronIELTS platform.

## Prerequisites

- Azure account (free tier available)
- Azure CLI installed (`brew install azure-cli` on macOS)
- Terraform 1.6+ installed
- GitHub account (for CI/CD)
- Credit card (required for Azure verification, won't be charged on free tier)

---

## Step 1: Create Azure Account

### 1.1 Sign Up

1. Go to [https://portal.azure.com](https://portal.azure.com)
2. Click "Start Free" or "Sign In"
3. Sign up with:
   - Microsoft account (Outlook, Hotmail)
   - Work/school account
   - Create new Microsoft account

4. Provide:
   - Phone number (verification)
   - Credit card (verification only)
   - Identity verification

5. Select "Pay-As-You-Go" subscription
   - Free credits: $200 for 30 days
   - Free services for 12 months
   - Always-free services

### 1.2 Verify Setup

```bash
# Login to Azure CLI
az login

# List subscriptions
az account list --output table

# Set default subscription
az account set --subscription "<your-subscription-id>"

# Verify
az account show
```

---

## Step 2: Create Resource Group

Resource groups organize all related Azure resources.

```bash
# Create resource group for development
az group create \
  --name rg-pronielts-dev \
  --location brazilsouth

# Verify
az group show --name rg-pronielts-dev
```

**Resource Group Naming Convention**:
- `rg-pronielts-dev`: Development environment
- `rg-pronielts-staging`: Staging environment (future)
- `rg-pronielts-prod`: Production environment (future)

---

## Step 3: Create Azure SQL Database

### 3.1 Create SQL Server

```bash
# Create SQL Server
az sql server create \
  --name sql-pronielts-dev \
  --resource-group rg-pronielts-dev \
  --location brazilsouth \
  --admin-user sqladmin \
  --admin-password '<StrongPassword123!>'

# Enable Azure services access
az sql server firewall-rule create \
  --resource-group rg-pronielts-dev \
  --server sql-pronielts-dev \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow your IP for development
az sql server firewall-rule create \
  --resource-group rg-pronielts-dev \
  --server sql-pronielts-dev \
  --name AllowMyIP \
  --start-ip-address <your-ip> \
  --end-ip-address <your-ip>
```

### 3.2 Create Database

```bash
# Create database (Basic tier - free eligible)
az sql db create \
  --resource-group rg-pronielts-dev \
  --server sql-pronielts-dev \
  --name sqldb-pronielts-dev \
  --service-objective Basic \
  --max-size 2GB

# Get connection string
az sql db show-connection-string \
  --client ado.net \
  --name sqldb-pronielts-dev \
  --server sql-pronielts-dev
```

**Connection String Format**:
```
Server=tcp:sql-pronielts-dev.database.windows.net,1433;Database=sqldb-pronielts-dev;User ID=sqladmin;Password=<your_password>;Encrypt=true;Connection Timeout=30;
```

**Cost**: Basic tier is ~$5/month after free credits (32GB storage, 5 DTUs)

---

## Step 4: Create Blob Storage

### 4.1 Create Storage Account

```bash
# Create storage account
az storage account create \
  --name stpronieltsdev \
  --resource-group rg-pronielts-dev \
  --location brazilsouth \
  --sku Standard_LRS \
  --kind StorageV2

# Get connection string
az storage account show-connection-string \
  --name stpronieltsdev \
  --resource-group rg-pronielts-dev \
  --output tsv
```

### 4.2 Create Blob Container

```bash
# Get account key
ACCOUNT_KEY=$(az storage account keys list \
  --resource-group rg-pronielts-dev \
  --account-name stpronieltsdev \
  --query '[0].value' \
  --output tsv)

# Create container
az storage container create \
  --name audio-recordings \
  --account-name stpronieltsdev \
  --account-key $ACCOUNT_KEY \
  --public-access off
```

**Cost**: 5GB free, then ~$0.02/GB/month for LRS (Locally Redundant Storage)

---

## Step 5: Create Speech Service

```bash
# Create Speech service (F0 free tier)
az cognitiveservices account create \
  --name cog-pronielts-speech-dev \
  --resource-group rg-pronielts-dev \
  --kind SpeechServices \
  --sku F0 \
  --location brazilsouth \
  --yes

# Get API key
az cognitiveservices account keys list \
  --name cog-pronielts-speech-dev \
  --resource-group rg-pronielts-dev \
  --query 'key1' \
  --output tsv
```

**Free Tier Limits**:
- 5 hours of audio per month
- ~300 assessments @ 1 minute each

**Paid Tier** (S0):
- $1 per hour of audio
- Unlimited requests

---

## Step 6: Create Key Vault

### 6.1 Create Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name kv-pronielts-dev \
  --resource-group rg-pronielts-dev \
  --location brazilsouth \
  --sku standard

# Set access policy for yourself
az keyvault set-policy \
  --name kv-pronielts-dev \
  --upn <your-email@example.com> \
  --secret-permissions get list set delete
```

### 6.2 Store Secrets

```bash
# Speech API Key
az keyvault secret set \
  --vault-name kv-pronielts-dev \
  --name SpeechApiKey \
  --value '<your-speech-api-key>'

# Database Connection String
az keyvault secret set \
  --vault-name kv-pronielts-dev \
  --name DatabaseConnectionString \
  --value '<your-db-connection-string>'

# Blob Storage Connection String
az keyvault secret set \
  --vault-name kv-pronielts-dev \
  --name BlobConnectionString \
  --value '<your-blob-connection-string>'

# Encryption Key (generate with Python)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
az keyvault secret set \
  --vault-name kv-pronielts-dev \
  --name EncryptionKey \
  --value '<generated-fernet-key>'

# JWT Secret
openssl rand -base64 32
az keyvault secret set \
  --vault-name kv-pronielts-dev \
  --name JwtSecretKey \
  --value '<generated-secret>'
```

**Cost**: 10,000 operations/month free

---

## Step 7: Create App Service

### 7.1 Create App Service Plan

```bash
# Create App Service Plan (F1 free tier)
az appservice plan create \
  --name plan-pronielts-dev \
  --resource-group rg-pronielts-dev \
  --sku F1 \
  --is-linux

# Verify
az appservice plan show \
  --name plan-pronielts-dev \
  --resource-group rg-pronielts-dev
```

### 7.2 Create Web App

```bash
# Create Web App for backend
az webapp create \
  --resource-group rg-pronielts-dev \
  --plan plan-pronielts-dev \
  --name app-pronielts-backend-dev \
  --runtime "PYTHON:3.11"

# Configure deployment
az webapp config appsettings set \
  --resource-group rg-pronielts-dev \
  --name app-pronielts-backend-dev \
  --settings \
    WEBSITES_PORT=8000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Configure startup command
az webapp config set \
  --resource-group rg-pronielts-dev \
  --name app-pronielts-backend-dev \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app"
```

### 7.3 Configure Environment Variables

```bash
# Set environment variables (reference Key Vault)
az webapp config appsettings set \
  --resource-group rg-pronielts-dev \
  --name app-pronielts-backend-dev \
  --settings \
    MOCK_MODE=false \
    DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://kv-pronielts-dev.vault.azure.net/secrets/DatabaseConnectionString/)" \
    SPEECH_KEY="@Microsoft.KeyVault(SecretUri=https://kv-pronielts-dev.vault.azure.net/secrets/SpeechApiKey/)" \
    SPEECH_REGION=brazilsouth \
    BLOB_CONNECTION_STRING="@Microsoft.KeyVault(SecretUri=https://kv-pronielts-dev.vault.azure.net/secrets/BlobConnectionString/)" \
    ENCRYPTION_KEY="@Microsoft.KeyVault(SecretUri=https://kv-pronielts-dev.vault.azure.net/secrets/EncryptionKey/)" \
    SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://kv-pronielts-dev.vault.azure.net/secrets/JwtSecretKey/)"
```

### 7.4 Enable Key Vault Access

```bash
# Enable managed identity
az webapp identity assign \
  --name app-pronielts-backend-dev \
  --resource-group rg-pronielts-dev

# Get principal ID
PRINCIPAL_ID=$(az webapp identity show \
  --name app-pronielts-backend-dev \
  --resource-group rg-pronielts-dev \
  --query principalId \
  --output tsv)

# Grant Key Vault access
az keyvault set-policy \
  --name kv-pronielts-dev \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

**Free Tier Limits** (F1):
- 1GB RAM
- 1GB disk space
- 60 CPU minutes/day
- Custom domain not available

**Paid Tier** (B1 - Basic):
- ~$13/month
- 1.75GB RAM
- 10GB disk space
- Unlimited CPU time

---

## Step 8: Create Azure AD B2C Tenant (Web Admin Auth)

### 8.1 Create B2C Tenant

1. Go to [Azure Portal](https://portal.azure.com)
2. Search "Azure AD B2C"
3. Click "Create a tenant"
4. Fill in:
   - **Organization name**: PronIELTS
   - **Initial domain name**: pronielts (will be pronielts.onmicrosoft.com)
   - **Country/Region**: Brazil
5. Click "Review + create"

### 8.2 Register Application

1. In B2C tenant, go to "App registrations"
2. Click "New registration"
3. Fill in:
   - **Name**: PronIELTS Web Admin
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**:
     - Platform: Single-page application (SPA)
     - URI: `http://localhost:5173` (dev) and `https://your-web-app-url.azurewebsites.net` (prod)
4. Click "Register"
5. Copy **Application (client) ID**

### 8.3 Create User Flow

1. In B2C, go to "User flows"
2. Click "New user flow"
3. Select "Sign up and sign in"
4. Name: `B2C_1_signupsignin`
5. Identity providers: Email signup
6. User attributes: Email, Display Name
7. Click "Create"

### 8.4 Configure API Permissions

1. In app registration, go to "API permissions"
2. Add permission → Microsoft Graph
3. Delegated permissions: `User.Read`, `openid`, `profile`
4. Click "Grant admin consent"

**Cost**: Free up to 50,000 MAU (Monthly Active Users)

---

## Step 9: Create Static Web App (Web Admin Hosting)

```bash
# Create Static Web App (Free tier)
az staticwebapp create \
  --name stapp-pronielts-web-dev \
  --resource-group rg-pronielts-dev \
  --location brazilsouth \
  --sku Free

# Get deployment token
az staticwebapp secrets list \
  --name stapp-pronielts-web-dev \
  --resource-group rg-pronielts-dev \
  --query "properties.apiKey" \
  --output tsv
```

**Free Tier Includes**:
- 100GB bandwidth/month
- Custom domains
- Automatic HTTPS
- GitHub/Azure DevOps integration

---

## Step 10: Configure Terraform Backend

Store Terraform state in Azure Storage.

```bash
# Create storage account for Terraform state
az storage account create \
  --name stpronieltstfstate \
  --resource-group rg-pronielts-dev \
  --location brazilsouth \
  --sku Standard_LRS

# Create container
az storage container create \
  --name tfstate \
  --account-name stpronieltstfstate
```

---

## Step 11: Create Service Principal for CI/CD

```bash
# Create service principal
az ad sp create-for-rbac \
  --name sp-pronielts-github \
  --role contributor \
  --scopes /subscriptions/<your-subscription-id>/resourceGroups/rg-pronielts-dev \
  --sdk-auth

# Output (save this for GitHub secrets):
{
  "clientId": "<client-id>",
  "clientSecret": "<client-secret>",
  "subscriptionId": "<subscription-id>",
  "tenantId": "<tenant-id>",
  ...
}
```

---

## Step 12: Configure GitHub Secrets

In your GitHub repository, go to Settings → Secrets → Actions.

Add the following secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AZURE_CREDENTIALS` | JSON from Step 11 | Service principal credentials |
| `AZURE_APP_NAME` | `app-pronielts-backend-dev` | App Service name |
| `AZURE_STATIC_WEB_APPS_TOKEN` | From Step 9 | Static Web App token |
| `AZURE_SQL_CONNECTION_STRING` | From Step 3.2 | Database connection |

---

## Step 13: Run Database Migrations

```bash
# From your local machine, connect to Azure SQL
# Update backend/.env with Azure SQL connection string
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed database
# Option 1: Via psql/sqlcmd (if installed)
sqlcmd -S sql-pronielts-dev.database.windows.net \
  -d sqldb-pronielts-dev \
  -U sqladmin \
  -P '<password>' \
  -i ../infrastructure/scripts/seed_database.sql

# Option 2: Via Python script
python -c "
from sqlalchemy import create_engine
engine = create_engine('<connection-string>')
with engine.connect() as conn:
    with open('../infrastructure/scripts/seed_database.sql') as f:
        conn.execute(f.read())
"
```

---

## Step 14: Deploy Backend

### Option A: Manual Deployment

```bash
cd backend

# Login to Azure
az login

# Set deployment source
az webapp deployment source config-zip \
  --resource-group rg-pronielts-dev \
  --name app-pronielts-backend-dev \
  --src backend.zip

# Monitor logs
az webapp log tail \
  --name app-pronielts-backend-dev \
  --resource-group rg-pronielts-dev
```

### Option B: GitHub Actions (Recommended)

Push to `main` branch triggers automatic deployment via `.github/workflows/backend-ci.yml`.

---

## Step 15: Deploy Web Admin

```bash
cd web

# Update .env.production
VITE_API_BASE_URL=https://app-pronielts-backend-dev.azurewebsites.net/api/v1
VITE_AZURE_CLIENT_ID=<from-step-8.2>
VITE_AZURE_TENANT=pronielts
VITE_AZURE_POLICY=B2C_1_signupsignin

# Build
npm run build

# Deploy via GitHub Actions
# (Triggered automatically on push to main)
```

---

## Step 16: Verify Deployment

### Backend Health Check

```bash
curl https://app-pronielts-backend-dev.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "mock_mode": false,
  "version": "1.0.0"
}
```

### Test API

```bash
# Get dialogs
curl https://app-pronielts-backend-dev.azurewebsites.net/api/v1/dialogs
```

### Web Admin

Navigate to: `https://stapp-pronielts-web-dev.azurestaticapps.net`

---

## Step 17: Monitor Resources

### Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app appi-pronielts-dev \
  --location brazilsouth \
  --resource-group rg-pronielts-dev \
  --application-type web

# Get instrumentation key
az monitor app-insights component show \
  --app appi-pronielts-dev \
  --resource-group rg-pronielts-dev \
  --query instrumentationKey \
  --output tsv

# Configure in App Service
az webapp config appsettings set \
  --resource-group rg-pronielts-dev \
  --name app-pronielts-backend-dev \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY='<key>'
```

### Set Up Alerts

```bash
# Create alert for high error rate
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group rg-pronielts-dev \
  --scopes /subscriptions/<sub-id>/resourceGroups/rg-pronielts-dev/providers/Microsoft.Web/sites/app-pronielts-backend-dev \
  --condition "count Http5xx > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group <action-group-id>
```

---

## Cost Summary (After Free Credits)

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Azure SQL Database | Basic | $5 |
| App Service | F1 Free | $0 |
| Blob Storage | Standard LRS | $0.02/GB (~$0.10) |
| Speech Service | F0 Free | $0 (5h limit) |
| Key Vault | Standard | $0 (10k ops limit) |
| Azure AD B2C | Free | $0 (50k MAU limit) |
| Static Web App | Free | $0 |
| **Total** | | **~$5-6/month** |

**To stay within free tier**:
- Use F1 App Service (limited CPU)
- Stay under 5 hours Speech API/month
- Keep database under 32GB
- Limit blob storage to 5GB

---

## Troubleshooting

### Issue: "Cannot connect to Azure SQL"

**Solution**:
```bash
# Check firewall rules
az sql server firewall-rule list \
  --resource-group rg-pronielts-dev \
  --server sql-pronielts-dev

# Add your current IP
az sql server firewall-rule create \
  --resource-group rg-pronielts-dev \
  --server sql-pronielts-dev \
  --name AllowMyIP2 \
  --start-ip-address $(curl -s ifconfig.me) \
  --end-ip-address $(curl -s ifconfig.me)
```

### Issue: "App Service shows 500 error"

**Solution**:
```bash
# Check logs
az webapp log tail \
  --name app-pronielts-backend-dev \
  --resource-group rg-pronielts-dev

# Restart app
az webapp restart \
  --name app-pronielts-backend-dev \
  --resource-group rg-pronielts-dev
```

### Issue: "Speech API quota exceeded"

**Solution**:
- Check usage in Azure Portal → Speech Service → Metrics
- Upgrade to S0 tier ($1/hour) or wait for next month

---

## Security Checklist

- [x] All secrets in Key Vault
- [x] Managed identity for App Service
- [x] SQL firewall configured
- [x] Blob storage private (no public access)
- [x] HTTPS enforced on all services
- [x] Azure AD B2C for admin authentication
- [x] Database connection encrypted
- [x] Regular security scans enabled

---

## Next Steps

1. Configure custom domain (optional)
2. Set up Azure DevOps pipeline (alternative to GitHub Actions)
3. Enable auto-scaling (when traffic increases)
4. Add Azure CDN for global distribution
5. Set up staging environment

---

## Useful Commands

```bash
# List all resources in group
az resource list --resource-group rg-pronielts-dev --output table

# Check costs
az consumption usage list --output table

# Delete all resources (careful!)
az group delete --name rg-pronielts-dev --yes --no-wait
```

---

**Document Version**: 1.0
**Last Updated**: 2026-01-23
**Estimated Setup Time**: 2-3 hours
