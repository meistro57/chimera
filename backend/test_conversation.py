#!/usr/bin/env python3
import asyncio
import aiohttp

async def test_conversation():
    async with aiohttp.ClientSession() as session:
        # Create conversation
        create_resp = await session.post('http://localhost:8000/api/conversations', json={
            'title': 'Test Chat',
            'participants': ['philosopher', 'comedian', 'scientist'],
            'topic': 'The meaning of life'
        })
        if create_resp.status != 200:
            print(f"Create failed: {create_resp.status} - {await create_resp.text()}")
            return

        data = await create_resp.json()
        conv_id = data['id']
        print(f"Created conversation: {conv_id}")

        # Start conversation
        start_resp = await session.post(f'http://localhost:8000/api/conversations/{conv_id}/start', json={
            'participants': ['philosopher', 'comedian', 'scientist']
        })
        if start_resp.status != 200:
            print(f"Start failed: {start_resp.status} - {await start_resp.text()}")
            return

        print(f"Started conversation: {conv_id}")
        await asyncio.sleep(5)  # Wait for messages

        # Get messages
        messages_resp = await session.get(f'http://localhost:8000/api/conversations/{conv_id}/messages')
        msgs = await messages_resp.json()
        print(f"Received {len(msgs.get('messages', []))} messages")

if __name__ == "__main__":
    asyncio.run(test_conversation())