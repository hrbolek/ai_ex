param aiSearchServiceName string 
param location string

resource accounts_ai_acr500896758024_name_resource 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: aiSearchServiceName
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    customSubDomainName: aiSearchServiceName
    publicNetworkAccess: 'Enabled'
  }
}

resource accounts_ai_acr500896758024_name_Default 'Microsoft.CognitiveServices/accounts/defenderForAISettings@2024-10-01' = {
  parent: accounts_ai_acr500896758024_name_resource
  name: 'Default'
  properties: {
    state: 'Disabled'
  }
}

resource accounts_ai_acr500896758024_name_text_embedding_3_large 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: accounts_ai_acr500896758024_name_resource
  name: 'text-embedding-3-large'
  sku: {
    name: 'GlobalStandard'
    capacity: 150
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-large'
      version: '1'
    }
    versionUpgradeOption: 'NoAutoUpgrade'
    currentCapacity: 150
    raiPolicyName: 'Microsoft.DefaultV2'
  }
}

// resource accounts_ai_acr500896758024_name_Microsoft_Default 'Microsoft.CognitiveServices/accounts/raiPolicies@2024-10-01' = {
//   parent: accounts_ai_acr500896758024_name_resource
//   name: 'Microsoft.Default'
//   properties: {
//     mode: 'Blocking'
//     contentFilters: [
//       {
//         name: 'Hate'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Prompt'
//       }
//       {
//         name: 'Hate'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Completion'
//       }
//       {
//         name: 'Sexual'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Prompt'
//       }
//       {
//         name: 'Sexual'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Completion'
//       }
//       {
//         name: 'Violence'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Prompt'
//       }
//       {
//         name: 'Violence'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Completion'
//       }
//       {
//         name: 'Selfharm'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Prompt'
//       }
//       {
//         name: 'Selfharm'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Completion'
//       }
//     ]
//   }
// }

// resource accounts_ai_acr500896758024_name_Microsoft_DefaultV2 'Microsoft.CognitiveServices/accounts/raiPolicies@2024-10-01' = {
//   parent: accounts_ai_acr500896758024_name_resource
//   name: 'Microsoft.DefaultV2'
//   properties: {
//     mode: 'Blocking'
//     contentFilters: [
//       {
//         name: 'Hate'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Prompt'
//       }
//       {
//         name: 'Hate'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Completion'
//       }
//       {
//         name: 'Sexual'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Prompt'
//       }
//       {
//         name: 'Sexual'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Completion'
//       }
//       {
//         name: 'Violence'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Prompt'
//       }
//       {
//         name: 'Violence'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Completion'
//       }
//       {
//         name: 'Selfharm'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Prompt'
//       }
//       {
//         name: 'Selfharm'
//         severityThreshold: 'Medium'
//         blocking: true
//         enabled: true
//         source: 'Completion'
//       }
//       {
//         name: 'Jailbreak'
//         blocking: true
//         enabled: true
//         source: 'Prompt'
//       }
//       {
//         name: 'Protected Material Text'
//         blocking: true
//         enabled: true
//         source: 'Completion'
//       }
//       {
//         name: 'Protected Material Code'
//         blocking: false
//         enabled: true
//         source: 'Completion'
//       }
//     ]
//   }
// }

