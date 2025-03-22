variable "azure_subscription_id" {
  type        = string
  description = "Azure Subscription to use"
}

variable "rg_name" {
  type        = string
  description = "Name of resource group to create"
}

variable "cognitive_account_name" {
  type        = string
  description = "Name of Cognitive Account to create"
}

variable "cognitive_account_sku" {
  type        = string
  description = "SKU of Cognitive Account to create"
  default     = "S0"
}

variable "cognitive_deployment_name" {
  type        = string
  description = "Name of Cognitive Deployment to create"
}

variable "location" {
  type        = string
  description = "Location to deploy"
  default     = "eastus2"
}

variable "llm_model_name" {
  type        = string
  description = "LLM Model Name to use"
  default     = "gpt-4o-mini"
}

variable "llm_model_version" {
  type        = string
  description = "Version of chosen model to use"
  default     = "2024-07-18"
}
