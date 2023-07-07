""" 
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Copyright (C) 2023 Fabrizio Smeraldi <fabrizio@smeraldi.net>
"""

""" ECG acquisition using an asynchronous queue - producer/consumer model """

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



async def run_ble_client(device, queue):
    """ This task connects to the BLE server (the heart rate sensor)
    identified by device, starts ECG notification and pushes the ECG 
    data to the queue. The tasks terminates when the sensor disconnects 
    or the user hits enter. """

    
    def keyboard_handler():
        """ Called by the asyncio loop when the user hits Enter """
        input() # clear input buffer
        print (f"Quitting on user command")
        quitclient.set() # causes the ble client task to exit

    
    def disconnected_callback(client):
        """ Called by BleakClient if the sensor disconnects """
        print("Sensor disconnected")
        quitclient.set() # causes the ble client task to exit


    # we use this event to signal the end of the client task
    quitclient=asyncio.Event()
    print(f"Connecting to {device}...")
    # the context manager will handle connection/disconnection for us
    async with BleakClient(device, disconnected_callback=
                           disconnected_callback) as client:
        print(f"Connected: {client.is_connected}")
        # create the Polar Measurement Data object; set queue for
        # ecg data
        pmd=PolarMeasurementData(client, ecg_queue=queue)
        # ask about ACC settings
        settings=await pmd.available_settings('ECG')
        print("Request for available ECG settings returned the following:")
        for k,v in settings.items():
            print(f"{k}:\t{v}")
        # Set the loop to call keyboard_handler when one line of input is
        # ready on stdin
        loop=asyncio.get_running_loop()
        loop.add_reader(sys.stdin, keyboard_handler)
        print(">>> Hit Enter to exit <<<")
        # start notifications; bleakheart will start pushing
        # data to the queue we passed to PolarMeasurementData
        (err_code, err_msg, _)= await pmd.start_streaming('ECG')
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
            await pmd.stop_streaming('ECG')
        loop.remove_reader(sys.stdin)
        # signal the consumer task to quit
        queue.put_nowait(('QUIT', None, None, None))


async def run_consumer_task(queue):
    """ This task retrieves ECG data from the queue and does 
    all the processing. You should ensure it returns control before 
    the next frame is received from the sensor. 

    In this example, we simply prints decoded ECG data as it 
    is received """
    print("After connecting, will print ECG data in the form")
    print("('ECG', tstamp, [s1,S2,...,sn])")
    print("where samples s1,...sn are in microVolt, tstamp is in ns")
    print("and it refers to the last sample sn.")
    while True:
        frame = await queue.get()
        if frame[0]=='QUIT':   # intercept exit signal
            break
        print(frame)

        
async def main():
    print("Scanning for BLE devices")
    device=await scan()
    if device==None:
        print("Polar device not found.")
        sys.exit(-4)
    # the queue needs to be long enough to cache all the frames, since
    # PolarMeasurementData uses put_nowait
    ecgqueue=asyncio.Queue()
    # producer task will return when the user hits enter or the
    # sensor disconnects
    producer=run_ble_client(device, ecgqueue)
    consumer=run_consumer_task(ecgqueue)
    # wait for the two tasks to exit
    await asyncio.gather(producer, consumer)
    print("Bye.")


# execute the main coroutine
asyncio.run(main())
