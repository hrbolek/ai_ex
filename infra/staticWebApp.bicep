param githubRepoName string
param githubHandleName string
param location string

resource staticSites_semanticindexreact_name_resource 'Microsoft.Web/staticSites@2024-04-01' = {
  name: githubRepoName
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: 'https://github.com/${githubHandleName}/${githubRepoName}'
    branch: 'main'
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
    provider: 'GitHub'
    enterpriseGradeCdnStatus: 'Disabled'
  }
}

resource staticSites_semanticindexreact_name_default 'Microsoft.Web/staticSites/basicAuth@2024-04-01' = {
  parent: staticSites_semanticindexreact_name_resource
  name: 'default'
  properties: {
    applicableEnvironmentsMode: 'SpecifiedEnvironments'
  }
}
