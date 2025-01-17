"""
bleakheart
----------

An asynchronous BLE Heart Monitor library with support for additional data 
from Polar monitors (ECG, accelerometers, etc)
"""

__copyright__= "Copyright (C) F. Smeraldi <fabrizio@smeraldi.net> 2023,24"
__license__= "Mozilla Public License Version 2.0"
__summary__= ("An asynchronous BLE Heart Monitor library with support for "
              "additional data from Polar monitors (ECG, accelerometers, etc)")
__uri__= "https://github.com/fsmeraldi/bleakheart"

from .version import __version__
from .core import BatteryLevel, HeartRate, PolarMeasurementData
