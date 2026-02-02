# GitHub Secrets Configuration

This document lists all the secrets required for the CI/CD pipelines to work correctly.

## How to Add Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add each secret listed below

---

## Required Secrets

### Azure Authentication (Required for Infrastructure & Backend Deploy)

These secrets are used to authenticate with Azure for Terraform and App Service deployment.

| Secret Name | Description | How to Get |
|-------------|-------------|-----------|
| `ARM_CLIENT_ID` | Azure Service Principal App ID | `az ad sp create-for-rbac --name "pronielts-github" --role Contributor --scopes /subscriptions/<sub-id> --query appId` |
| `ARM_CLIENT_SECRET` | Azure Service Principal Password | Output from the command above (`password` field) |
| `ARM_SUBSCRIPTION_ID` | Azure Subscription ID | `az account show --query id` |
| `ARM_TENANT_ID` | Azure Tenant ID | `az account show --query tenantId` |

**Create Service Principal (run once):**

```bash
az login
az ad sp create-for-rbac \
  --name "pronielts-github-actions" \
  --role Contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

The output JSON contains all the values you need:
- `clientId` → `ARM_CLIENT_ID`
- `clientSecret` → `ARM_CLIENT_SECRET`
- `subscriptionId` → `ARM_SUBSCRIPTION_ID`
- `tenantId` → `ARM_TENANT_ID`

---

### Backend Deployment Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|-----------|
| `AZURE_CREDENTIALS` | Full Azure credentials JSON | Output from `az ad sp create-for-rbac --sdk-auth` |
| `AZURE_APP_SERVICE_NAME` | Name of the App Service | `app-pronielts-dev` (from Terraform output) |
| `AZURE_RESOURCE_GROUP` | Resource Group name | `rg-pronielts-dev` (from Terraform output) |

**AZURE_CREDENTIALS format:**

```json
{
  "clientId": "<ARM_CLIENT_ID>",
  "clientSecret": "<ARM_CLIENT_SECRET>",
  "subscriptionId": "<ARM_SUBSCRIPTION_ID>",
  "tenantId": "<ARM_TENANT_ID>"
}
```

---

### Web Admin Deployment Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|-----------|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Static Web App deployment token | Terraform output: `terraform output static_web_app_api_key` |
| `VITE_API_URL` | Backend API URL (optional) | `https://app-pronielts-dev.azurewebsites.net` |

---

### Code Coverage (Optional)

| Secret Name | Description | How to Get |
|-------------|-------------|-----------|
| `CODECOV_TOKEN` | Codecov upload token | Sign up at [codecov.io](https://codecov.io), link your repo |

---

## Environment Protection Rules

For production deployments, we recommend setting up environment protection rules:

1. Go to **Settings** > **Environments**
2. Create environments: `dev`, `prod`, `dev-destroy`, `prod-destroy`
3. For `prod` and destroy environments:
   - Enable **Required reviewers**
   - Add yourself or your team as reviewers

---

## Quick Setup Script

Run this script to create all Azure secrets at once:

```bash
#!/bin/bash

# Login to Azure
az login

# Set your subscription
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create Service Principal
SP_OUTPUT=$(az ad sp create-for-rbac \
  --name "pronielts-github-actions" \
  --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --sdk-auth)

echo "=== Add these secrets to GitHub ==="
echo ""
echo "ARM_CLIENT_ID=$(echo $SP_OUTPUT | jq -r .clientId)"
echo "ARM_CLIENT_SECRET=$(echo $SP_OUTPUT | jq -r .clientSecret)"
echo "ARM_SUBSCRIPTION_ID=$(echo $SP_OUTPUT | jq -r .subscriptionId)"
echo "ARM_TENANT_ID=$(echo $SP_OUTPUT | jq -r .tenantId)"
echo ""
echo "AZURE_CREDENTIALS='$SP_OUTPUT'"
echo ""
echo "AZURE_APP_SERVICE_NAME=app-pronielts-dev"
echo "AZURE_RESOURCE_GROUP=rg-pronielts-dev"
```

---

## Secrets by Workflow

### backend-ci.yml
- `AZURE_CREDENTIALS`
- `AZURE_APP_SERVICE_NAME`
- `AZURE_RESOURCE_GROUP`
- `CODECOV_TOKEN` (optional)

### mobile-ci.yml
- `CODECOV_TOKEN` (optional)

### web-ci.yml
- `AZURE_STATIC_WEB_APPS_API_TOKEN`
- `VITE_API_URL` (optional)

### infrastructure-deploy.yml
- `ARM_CLIENT_ID`
- `ARM_CLIENT_SECRET`
- `ARM_SUBSCRIPTION_ID`
- `ARM_TENANT_ID`

### terraform-state-setup.yml
- `ARM_CLIENT_ID`
- `ARM_CLIENT_SECRET`
- `ARM_SUBSCRIPTION_ID`
- `ARM_TENANT_ID`

---

## Deployment Order

1. **First time setup:**
   - Add Azure authentication secrets (ARM_*)
   - Run `terraform-state-setup.yml` workflow with `apply` action
   - Run `infrastructure-deploy.yml` workflow with `apply` action
   - Get outputs from Terraform (App Service name, Static Web App token)
   - Add remaining secrets

2. **Subsequent deployments:**
   - Push code changes to trigger CI/CD automatically
   - Or use workflow_dispatch for manual deployments

---

## Troubleshooting

### "Error: AADSTS700016: Application not found"
- Service Principal was deleted or not created
- Recreate with the command above

### "Error: The subscription is not registered"
- Run: `az provider register --namespace Microsoft.Web`

### "Error: AuthorizationFailed"
- Service Principal doesn't have Contributor role
- Re-run the sp create command with correct scope

---

**Last Updated:** 2026-02-02
