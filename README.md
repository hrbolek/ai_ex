Container apps
Container Apps Environment

from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup, Container, ResourceRequests, ResourceRequirements, ImageRegistryCredential, OperatingSystemTypes, IpAddress, Port, ContainerGroupNetworkProtocol)

SUBSCRIPTION_ID = "tvuj-subscription-id"
RESOURCE_GROUP = "jmeno-resource-group"
CONTAINER_GROUP_NAME = "moje-container-app"
LOCATION = "westeurope"

IMAGE = "dockerhubuser/myimage:latest"  # např. "library/nginx:latest"
CONTAINER_PORT = 80  # změň podle potřeby

credential = DefaultAzureCredential()
client = ContainerInstanceManagementClient(credential, SUBSCRIPTION_ID)

container_resource_requests = ResourceRequests(memory_in_gb=1.0, cpu=1.0)
container_resource_requirements = ResourceRequirements(requests=container_resource_requests)
container = Container(
    name=CONTAINER_GROUP_NAME,
    image=IMAGE,
    resources=container_resource_requirements,
    ports=[Port(protocol=ContainerGroupNetworkProtocol.tcp, port=CONTAINER_PORT)],
)

group = ContainerGroup(
    location=LOCATION,
    containers=[container],
    os_type=OperatingSystemTypes.linux,
    ip_address=IpAddress(
        ports=[Port(protocol=ContainerGroupNetworkProtocol.tcp, port=CONTAINER_PORT)],
        type="Public"
    ),
    restart_policy="Always"
)

# Vytvoření/aktualizace instance
client.container_groups.begin_create_or_update(RESOURCE_GROUP, CONTAINER_GROUP_NAME, group).result()

print("Hotovo! Container běží.")
