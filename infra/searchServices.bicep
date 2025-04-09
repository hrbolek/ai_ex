param searchServiceName string
param searchServiceSku string = 'basic'
param location string 

resource searchService 'Microsoft.Search/searchServices@2025-02-01-preview' = {
  name: searchServiceName
  location: location
  sku: {
    name: searchServiceSku
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    endpoint: 'https://${searchServiceName}.search.windows.net'
    hostingMode: 'default'
    publicNetworkAccess: 'Enabled'
    networkRuleSet: {
      ipRules: []
      bypass: 'None'
    }
    encryptionWithCmk: {
      enforcement: 'Unspecified'
    }
    disableLocalAuth: false
    authOptions: {
      apiKeyOnly: {}
    }
    disabledDataExfiltrationOptions: []
    semanticSearch: 'disabled'
  }
}


// resource searchIndex 'Microsoft.Search/searchServices/indexes@2022-09-01' = {
//   parent: searchService
//   name: '${searchServiceName}index'
//   properties: {
//   fields: [
//     {
//       name: 'content'
//       type: 'Edm.String'
//       searchable: true
//       filterable: false
//       retrievable: true
//       stored: true
//       sortable: false
//       facetable: false
//       key: false
//       analyzer: 'standard'
//       synonymMaps: []
//     }
//     {
//       name: 'url'
//       type: 'Edm.String'
//       searchable: false
//       filterable: false
//       retrievable: true
//       stored: true
//       sortable: false
//       facetable: false
//       key: false
//       synonymMaps: []
//     }
//     {
//       name: 'filepath'
//       type: 'Edm.String'
//       searchable: false
//       filterable: false
//       retrievable: true
//       stored: true
//       sortable: false
//       facetable: false
//       key: false
//       synonymMaps: []
//     }
//     {
//       name: 'title'
//       type: 'Edm.String'
//       searchable: true
//       filterable: false
//       retrievable: true
//       stored: true
//       sortable: false
//       facetable: false
//       key: false
//       synonymMaps: []
//     }
//     {
//       name: 'meta_json_string'
//       type: 'Edm.String'
//       searchable: false
//       filterable: false
//       retrievable: true
//       stored: true
//       sortable: false
//       facetable: false
//       key: false
//       synonymMaps: []
//     }
//     {
//       name: 'contentVector'
//       type: 'Collection(Edm.Single)'
//       searchable: true
//       filterable: false
//       retrievable: true
//       stored: true
//       sortable: false
//       facetable: false
//       key: false
//       dimensions: 3072
//       vectorSearchProfile: 'contentVector_profile'
//       synonymMaps: []
//     }
//     {
//       name: 'id'
//       type: 'Edm.String'
//       searchable: false
//       filterable: false
//       retrievable: true
//       stored: true
//       sortable: false
//       facetable: false
//       key: true
//       synonymMaps: []
//     }
//   ]
//   scoringProfiles: []
//   suggesters: []
//   analyzers: []
//   normalizers: []
//   tokenizers: []
//   tokenFilters: []
//   charFilters: []
//   similarity: {
//     '@odata.type': '#Microsoft.Azure.Search.BM25Similarity'
//   }
//   semantic: {
//     configurations: [
//       {
//         name: 'azureml-default'
//         prioritizedFields: {
//           titleField: {
//             fieldName: 'title'
//           }
//           prioritizedContentFields: [
//             {
//               fieldName: 'content'
//             }
//           ]
//           prioritizedKeywordsFields: []
//         }
//       }
//     ]
//   }
//   vectorSearch: {
//     algorithms: [
//       {
//         name: 'contentVector_config'
//         kind: 'hnsw'
//         hnswParameters: {
//           metric: 'cosine'
//           m: 4
//           efConstruction: 400
//           efSearch: 500
//         }
//       }
//     ]
//     profiles: [
//       {
//         name: 'contentVector_profile'
//         algorithm: 'contentVector_config'
//       }
//     ]
//     vectorizers: []
//     compressions: []
//   }
// }
//   }
