# 🖤 BleakHeart 

An asynchronous BLE Heart Monitor library that supports additional measurements (such as ECG and accelerometer data) available from Polar sensors through the Polar Measurement Data interface. 

BleakHeart is written in Python using the [asyncio](https://docs.python.org/3/library/asyncio.html) framework; BLE communication is based on [Bleak](https://bleak.readthedocs.io/en/latest/#).

## Installation

Install from PyPI using ```pip```:
```
python3 -m pip install "bleakheart"
```

## Features

* Supports heart rate acquisition for devices supporting the standard BLE [heart rate service](https://www.bluetooth.com/specifications/specs/heart-rate-service-1-0/), including RR intervals, instant heart rate, energy expenditure and (client-based) time stamps;
* Reads Accelerometer and ECG signals from the Polar H10 chest strap; 
* Offers partial support for measurements available from other Polar devices through the Polar Measurement Data interface;
* Normalises Polar sensor timestamps to Epoch time; 
* Reads the battery charge state through the standard BLE [battery service](https://www.bluetooth.com/specifications/specs/battery-service/) (also available on other types of BLE devices).

## Usage

BleakHeart supports a variety of software design choices. Specifically:
* A data producer/consumer model can be easily implemented by asking BleakHeart to push sensor data onto asynchronous queues;
* Alternatively, data can be sent to a callback. Simple tasks such as sensor logging can be accomplished with only a minimal understanding of ```asyncio```;
* All data are tagged with their measurement type; thus the same queue or callback can be used to handle different types of measurements if desired.

Please see the examples directory for detailed examples of some of the possible workflows, and use the ```help``` function on BleakHeart objects for more information.

## Limitations

BleakHeart has mainly been tested on a Polar H10 chest strap (under Linux), since that is what I have available. However, reports from Windows and MacOS users have been positive. Other Polar devices are only partly supported; measurements other than ECG and acceleration are returned as raw bytearrays. Offline recording to the internal Polar H10 memory is not supported.

## Credits and contributing

This software was originally developed and is maintained by [Fabrizio Smeraldi](http://www.eecs.qmul.ac.uk/~fabri/). Many thanks to 

* Alex Ong - [alex-ong](https://github.com/alex-ong),
* Chris Spooner - [Chris-Spooner999](https://github.com/Chris-Spooner999),
* Fareza - [farezae](https://github.com/farezae),
* Léo Flaventin Hauchecorne - [hl037](https://github.com/hl037),
* Wesley Huff - [HufflyCodes](https://github.com/HufflyCodes),
* Will Powell - [WillPowellUK](https://github.com/WillPowellUK)

for testing, suggestions and code. If you would like to contribute, please [get in touch](mailto:fabrizio@smeraldi.net).

## Academic use

If you use this software for academic research, please reference this repository and [let me know](mailto:fabrizio@smeraldi.net). I will cite your paper! :)

## Disclaimer and license

Polar is a trademark of Polar Electro Oy; [Bleak](https://bleak.readthedocs.io/en/latest/#) is an open-source BLE library developed by Henrik Blidh. The author is not affiliated with either.

This software is provided subject to the terms of the [Mozilla Public License version 2.0](https://www.mozilla.org/en-US/MPL/2.0/), in the hope that it will be useful; see the ```LICENSE``` file for details.

## Resources

* The official [Polar BLE SDK](https://github.com/polarofficial/polar-ble-sdk), contains software for Android and iOS and some interesting documentation, in particular:
    * An explanation of [ECG on the Polar H10](https://github.com/polarofficial/polar-ble-sdk/blob/master/technical_documentation/H10_ECG_Explained.docx)
    * A specification of the proprietary [Polar Measurement Data](https://github.com/polarofficial/polar-ble-sdk/blob/52ef4c4b77e5f83b0839f0f4f72623a9b9d79372/technical_documentation/Polar_Measurement_Data_Specification.pdf) service
    * An explanation of the [time system](https://github.com/polarofficial/polar-ble-sdk/blob/master/documentation/TimeSystemExplained.md) in Polar devices (BleakHeart transparently normalises this to Epoch time).
* The [Heart Rate service](https://www.bluetooth.com/specifications/specs/heart-rate-service-1-0/) specification, on  the BLE SIG website.
* The [Battery service](https://www.bluetooth.com/specifications/specs/battery-service/) specification, on the BLE SIG website.
