resource "azurerm_resource_group" "openai_rg" {
  name     = var.rg_name 
  location = var.location
}

resource "azurerm_cognitive_account" "oai" {
  name                = var.cognitive_account_name
  location            = azurerm_resource_group.openai_rg.location
  resource_group_name = azurerm_resource_group.openai_rg.name
  kind                = "OpenAI"
  sku_name            = var.cognitive_account_sku
}

resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = var.cognitive_deployment_name
  cognitive_account_id = azurerm_cognitive_account.oai.id

  model {
    format  = "OpenAI"
    name    = var.llm_model_name
    version = var.llm_model_version
  }

  sku {
    name     = "GlobalStandard"
    capacity = 200
  }
}
