""" 
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

""" PPG acquisition on a Verity sensor using the SDK mode for additional
sampling options. Processing via a callback function. """


import sys
import asyncio
from bleak import BleakScanner, BleakClient
from bleakheart import PolarMeasurementData
import os
import math

if sys.platform=="win32":
    from threading import Thread
    add_reader_support=False
else:
    add_reader_support=True

async def scan():
    """ Scan for a Polar device. """
    device= await BleakScanner.find_device_by_filter(
        lambda dev, adv: dev.name and "polar" in dev.name.lower())
    return device


async def run_ble_client(device, callback):
    """ This task connects to the sensor, starts heart rate notification
    and monitors connection and stdio for disconnects/user input. """

    def keyboard_handler(loop=None):
        """ Called by the asyncio loop when the user hits Enter, 
        or run in a separate thread (if no add_reader support). In 
        this case, the event loop is passed as an argument """
        input() # clear input buffer
        print (f"Quitting on user command")
        # causes the client task to exit
        if loop==None:
            quitclient.set() # we are in the event loop thread
        else:
            # we are in a separate thread - call set in the event loop thread
            loop.call_soon_threadsafe(quitclient.set)    

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
        # Requesting SDK mode for wider PPG settings
        await pmd.start_streaming('SDK') 
        # ask about PPG settings
        settings=await pmd.available_settings('PPG')
        print("Request for available PPG settings returned the following:")
        for k,v in settings.items():
            print(f"{k}: {v}")
        loop=asyncio.get_running_loop()
        if add_reader_support:
            # Set the loop to call keyboard_handler when one line of input is
            # ready on stdin
            loop.add_reader(sys.stdin, keyboard_handler)
        else:
            # run keyboard_handler in a daemon thread
            Thread(target=keyboard_handler, kwargs={'loop': loop},
                    daemon=True).start()
        print(">>> Hit Enter to exit <<<")        
        # start notifications; bleakheart will start sending data to
        # the callback. You can set parameters as desired - invalid
        # settings return an error
        (err_code, err_msg, _) =await pmd.start_streaming('PPG',
                                                          SAMPLE_RATE=176,
                                                          CHANNELS=4,
                                                          RESOLUTION=22)
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
            await pmd.stop_streaming('PPG')            
        if add_reader_support:
            loop.remove_reader(sys.stdin)


def ppg_callback(data):
    """ This callback is sent the ppg data and does all the 
    processing. You should ensure it returns before the next 
    frame is received from the sensor. 

    In this example, we simply print decoded ppg data as it 
    is received """

    # print(f"Datatype:{data[0]}, Timestamp:{data[1]}")
    print("Raw Data:")
    print(data)


async def main():
    print("Scanning for BLE devices")
    device=await scan()
    if device==None:
        print("Polar device not found.")
        sys.exit(-4)
    print("After connecting, will print PPG data in the form")
    print(" ('PPG', tstamp, [(ppg0_1,ppg1_1,ppg2_1,ambient_1),"
          "(ppg0_2,ppg1_2,ppg2_2,ambient_2),...,"
          "(ppg0_n,ppg1_n,ppg2_n,ambient_n)])")
    print("where samples are unitless values, tstamp is in ns")
    # client task will return when the user hits enter or the sensor disconnects
    await run_ble_client(device, ppg_callback)
    print("Bye.")


# execute the main coroutine
asyncio.run(main())
