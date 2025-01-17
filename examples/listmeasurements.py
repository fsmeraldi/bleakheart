""" 
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Copyright (C) 2023 Fabrizio Smeraldi <fabrizio@smeraldi.net>
"""

""" List the measurement available from a Polar device through the 
PolarMeasurementData API """

import sys
import asyncio
from bleak import BleakScanner, BleakClient
from bleakheart import PolarMeasurementData 


async def scan():
    """ Scan for a Polar device. """
    device= await BleakScanner.find_device_by_filter(
        lambda dev, adv: dev.name and "polar" in dev.name.lower())
    return device


async def main():
    print("Scanning for BLE devices")
    device=await scan()
    if device==None:
        print("Polar device not found.")
        sys.exit(-4)
    print(f"Connecting to {device}...")
    async with BleakClient(device) as client:
        print(f"Connected: {client.is_connected}")
        meas= await PolarMeasurementData(client).available_measurements()
        print("Measurements supported by Polar device:")
        print(meas)

        
# execute the main coroutine
asyncio.run(main())
