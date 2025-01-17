""" 
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Copyright (C) 2023 Fabrizio Smeraldi <fabrizio@smeraldi.net>
"""

import sys
import asyncio
from bleak import BleakScanner, BleakClient
from bleakheart import BatteryLevel


async def scan():
    """ Scan for a Polar device. If you have another compatible device,
    edit the string in the code below accordingly """
    device= await BleakScanner.find_device_by_filter(
        lambda dev, adv: dev.name and "polar" in dev.name.lower())
    return device


async def main():
    print("Scanning for BLE devices")
    device=await scan()
    if device==None:
        print("Polar device not found. If you have another compatible")
        print("device, edit the scan() function accordingly.")
        sys.exit(-4)
    print(f"Connecting to {device}...")
    async with BleakClient(device) as client:
        print(f"Connected: {client.is_connected}")
        battlevel= await BatteryLevel(client).read()
        print(f"Battery level {battlevel}%")


# execute the main coroutine
asyncio.run(main())
