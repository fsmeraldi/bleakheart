""" 
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Copyright (C) 2023 Fabrizio Smeraldi <fabrizio@smeraldi.net>
"""

""" Accelerometer acquisition using a callback function """

import sys
import asyncio
from bleak import BleakScanner, BleakClient
# Allow importing bleakheart from parent directory
sys.path.append('../')
from bleakheart import PolarMeasurementData 


async def scan():
    """ Scan for a Polar device. """
    device= await BleakScanner.find_device_by_filter(
        lambda dev, adv: dev.name and "polar" in dev.name.lower())
    return device


async def run_ble_client(device, callback):
    """ This task connects to the sensor, starts heart rate notification
    and monitors connection and stdio for disconnects/user input. """

    def keyboard_handler():
        """ Called by the asyncio loop when the user hits Enter """
        input() # clear input buffer
        print (f"Quitting on user command")
        quitclient.set() # causes the client task to exit


    def disconnected_callback(client):
        """ Called by BleakClient if the sensor disconnects """
        print("Sensor disconnected")
        # signal exit
        quitclient.set() # causes the client task to exit

    # we use this event to signal the end of the client task
    quitclient=asyncio.Event()
    # the context manager will handle connection/disconnection for us
    async with BleakClient(device, disconnected_callback=
                           disconnected_callback) as client:
        print(f"Connected: {client.is_connected}")
        # create the Polar Measurement Data object; set callback
        pmd=PolarMeasurementData(client, callback=callback)
        # ask about ACC settings
        settings=await pmd.available_settings('ACC')
        print("Request for available ACC settings returned the following:")
        for k,v in settings.items():
            print(f"{k}: {v}")
        # Set the loop to call keyboard_handler when one line of input is
        # ready on stdin
        loop=asyncio.get_running_loop()
        loop.add_reader(sys.stdin, keyboard_handler)
        print(">>> Hit Enter to exit <<<")        
        # start notifications; bleakheart will start sending data to
        # the callback. You can set parameters as desired - invalid
        # settings return an error
        (err_code, err_msg, _) =await pmd.start_streaming('ACC', RANGE=2,
                                                          SAMPLE_RATE=25)
        if err_code!=0:
            print(f"PMD returned an error: {err_msg}")
            sys.exit(err_code)
        # this task does not need to do anything else; wait until
        # user hits enter or the sensor disconnects 
        await quitclient.wait()
        # no need to stop notifications if we are exiting the context
        # manager anyway, as they will disconnect the client; however,
        # it's easy to stop them if we want to
        if client.is_connected:
            await pmd.stop_streaming('ACC')
        loop.remove_reader(sys.stdin)


def accel_callback(data):
    """ This callback is sent the acceleration data and does all the 
    processing. You should ensure it returns before the next 
    frame is received from the sensor. 

    In this example, we simply print decoded acceleration data as it 
    is received """
    print(data)

        
async def main():
    print("Scanning for BLE devices")
    device=await scan()
    if device==None:
        print("Polar device not found.")
        sys.exit(-4)
    print("After connecting, will print accelerometer data in the form")
    print(" ('ACC', tstamp, [(x1,y1,z1),(x2,y2,z2),...,(xn,yn,zn)])")
    print("where samples (xi, yi, zi) are in milliG, tstamp is in ns")
    print("and it refers to the last sample (xn,yn,zn).")
    # client task will return when the user hits enter or the
    # sensor disconnects
    await run_ble_client(device, accel_callback)
    print("Bye.")


# execute the main coroutine
asyncio.run(main())
