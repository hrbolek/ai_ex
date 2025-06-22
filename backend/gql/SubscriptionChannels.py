import asyncio
# user_channels[user_id][channel] = Queue
user_channels = {}

def get_user_channels(user_id):
    if user_id not in user_channels:
        user_channels[user_id] = {}
    return user_channels[user_id]

def get_channel_queue(user_id, channel_id):
    print(f"get_channel_queue {user_id}.{channel_id}")
    channels = get_user_channels(user_id)
    if channel_id not in channels:
        channels[channel_id] = asyncio.Queue()
    return channels[channel_id]