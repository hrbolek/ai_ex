from .AzureLightClient import AzureLightClient

async def read_subscription(
    azureLightClient: AzureLightClient
):
    async with azureLightClient as alc:
        response = await alc.get(endpoint="/subscriptions?api-version=2020-01-01")
        subscriptions = response.get("value", [])
        assert len(subscriptions) > 0, "No subscriptions are available"
        subscription = subscriptions[0]
        # subscription['subscriptionId']
        return subscription
