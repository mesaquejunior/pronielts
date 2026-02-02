# Backend Configuration for Terraform State
# IMPORTANT: Run shared/backend-setup first to create the storage account

# Uncomment this block after running backend-setup
# terraform {
#   backend "azurerm" {
#     resource_group_name  = "rg-pronielts-tfstate"
#     storage_account_name = "stpronieltstfstate"
#     container_name       = "tfstate"
#     key                  = "dev.terraform.tfstate"
#   }
# }

# For initial setup, use local backend (comment out when using remote)
# terraform {
#   backend "local" {
#     path = "terraform.tfstate"
#   }
# }
