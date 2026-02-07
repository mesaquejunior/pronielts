# Backend Configuration for Terraform State

terraform {
  backend "azurerm" {
    resource_group_name  = "rg-pronielts-tfstate"
    storage_account_name = "stpronieltstfstate"
    container_name       = "tfstate"
    key                  = "dev.terraform.tfstate"
  }
}
