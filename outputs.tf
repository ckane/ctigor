output "openai_endpoint" {
  value = azurerm_cognitive_account.oai.endpoint
}

output "openai_primary_key" {
  value = azurerm_cognitive_account.oai.primary_access_key
  sensitive = true
}

output "openai_secondary_key" {
  value = azurerm_cognitive_account.oai.secondary_access_key
  sensitive = true
}
