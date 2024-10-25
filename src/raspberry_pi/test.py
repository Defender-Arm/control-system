import asyncio
from bleak import BleakClient, BleakScanner

async def scan():
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Device: {device.name}, Address: {device.address}")


# Replace with your device's address
DEVICE_ADDRESS = "XX:XX:XX:XX:XX:XX"

async def on_disconnect(client):
    print(f"Disconnected from {client}")

async def on_receive(client, data):
    print(f"Received: {data}")
    await client.send(data)

async def connect_to_device(address):
    async with BleakClient(address) as client:
        if await client.is_connected():
            print(f"Connected to {address}")
            # Add your communication logic here
            await asyncio.sleep(5)  # Keep the connection for 5 seconds
        else:
            print(f"Failed to connect to {address}")

async def main():
    print("Scanning for Bluetooth devices...")
    await scan()
    await connect_to_device(DEVICE_ADDRESS)

if __name__ == "__main__":
    asyncio.run(main())