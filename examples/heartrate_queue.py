""" 
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Copyright (C) 2023 Fabrizio Smeraldi <fabrizio@smeraldi.net>
"""

""" Heartrate acquisition using an asynchronous queue - 
producer/consumer model """

import sys
import asyncio
from bleak import BleakScanner, BleakClient
# Allow importing bleakheart from parent directory
sys.path.append('../')
from bleakheart import HeartRate


# change these two parameters and see what happens.
# INSTANT_RATE is unsupported when UNPACK is False
UNPACK = True
INSTANT_RATE= UNPACK and True


async def scan():
    """ Scan for a Polar device. If you have another compatible device,
    edit the string in the code below accordingly """
    device= await BleakScanner.find_device_by_filter(
        lambda dev, adv: dev.name and "polar" in dev.name.lower())
    return device


async def run_ble_client(device, hrqueue):
    """ This task connects to the BLE server (the heart rate sensor)
    identified by device, starts heart rate notification and pushes 
    heart rate data to hrqueue. The tasks terminates when the sensor 
    disconnects or the user hits enter. """
    
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
        # Set the loop to call keyboard_handler when one line of input is
        # ready on stdin
        loop=asyncio.get_running_loop()
        loop.add_reader(sys.stdin, keyboard_handler)
        print(">>> Hit Enter to exit <<<")
        # create the heart rate object; set queue and other
        # parameters
        heartrate=HeartRate(client, queue=hrqueue,
                            instant_rate=INSTANT_RATE,
                            unpack=UNPACK)
        # start notifications; bleakheart will start pushing data
        # to the queue
        await heartrate.start_notify()
        # this task does not need to do anything else; wait until
        # user hits enter or the sensor disconnects
        await quitclient.wait()
        # no need to stop notifications if we are exiting the context
        # manager anyway, as they will disconnect the client; however,
        # it's easy to stop them if we want to
        if client.is_connected:
            await heartrate.stop_notify()
        loop.remove_reader(sys.stdin)
        # signal the consumer task to quit
        hrqueue.put_nowait(('QUIT', None, None, None))


async def run_consumer_task(hrqueue):
    """ This task retrieves heart rate data from the queue and does 
    all the processing. You should ensure it returns control before 
    the next frame is received from the sensor. 

    In this example, we simply print the decoded heart rate data as it 
    is received """
    print("After connecting, will print heart rate data in the form")
    if UNPACK:
        print("   ('HR', tstamp, (bpm, rr_interval), energy)")
    else:
        print("   ('HR', tstamp, (bpm, [rr1,rr2,...]), energy)")
    print("where tstamp is in ns, rr intervals are in ms, and")
    print("energy expenditure (if present) is in kJoule.")
    while True:
        frame = await hrqueue.get()
        if frame[0]=='QUIT':   # intercept exit signal
            break
        print(frame)

        
async def main():
    print("Scanning for BLE devices")
    device=await scan()
    if device==None:
        print("Polar device not found. If you have another compatible")
        print("device, edit the scan() function accordingly.")
        sys.exit(-4)
    # the queue needs to be long enough to cache all the frames, since
    # put_nowait is used by HeartRate
    hrqueue=asyncio.Queue()
    # producer task will return when the user hits enter or the
    # sensor disconnects
    producer=run_ble_client(device, hrqueue)
    consumer=run_consumer_task(hrqueue)
    # wait for the two tasks to exit
    await asyncio.gather(producer, consumer)
    print("Bye.")


# execute the main coroutine
asyncio.run(main())
