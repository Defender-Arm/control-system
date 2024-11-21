import asyncio
from bleak import BleakClient

# Replace with your ESP32's MAC address and characteristic UUID
device_mac_address = "E8:9F:6D:55:15:7E"  # ESP32 MAC Address
characteristic_uuid = "your-characteristic-uuid"  # UUID for the characteristic

async def print_characteristic_value():
    async with BleakClient(device_mac_address) as client:
        print(f"Connected to {device_mac_address}")
        
        # Start notifications
        await client.start_notify(characteristic_uuid, notification_handler)
        
        # Keep the connection alive
        await asyncio.sleep(30)  # Adjust the sleep time as necessary
        
        await client.stop_notify(characteristic_uuid)

def notification_handler(sender, data):
    print(f"Received data from {sender}: {data.decode('utf-8')}")

# Run the event loop
asyncio.run(print_characteristic_value())
