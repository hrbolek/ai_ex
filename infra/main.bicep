param searchServiceName string
param location string
param githubRepoName string
param githubHandleName string
param searchServiceSku string

module searchServices 'searchServices.bicep' = {
    name: 'searchServicesModule'
    params: {
        location: location
        searchServiceName: searchServiceName
        searchServiceSku: searchServiceSku
    }
}

module storageAccount 'storageAccount.bicep' = {
    name: 'storageAccountModule'
    params: {
        storageAccountName: 'st${searchServiceName}'
        location: location
    }
}

module aiSearchService 'aiSearchService.bicep' = {
    name: 'aiSearchServiceModule'
    params: {
        aiSearchServiceName: 'ai-${searchServiceName}'   
        location: location      
    }
}

module staticWebApp 'staticWebApp.bicep' = {
    name: 'staticWebAppModule'
    params: {
        githubRepoName: githubRepoName
        githubHandleName: githubHandleName 
        location: location
    }
}
