"""
bleakheart
----------

An asynchronous BLE Heart Monitor library with support for additional data 
from Polar monitors (ECG, accelerometers, PPG)
"""

__all__=['BatteryLevel', 'HeartRate', 'PolarMeasurementData']

__copyright__= "Copyright (C) F. Smeraldi <fabrizio@smeraldi.net> 2023,25"
__license__= "Mozilla Public License Version 2.0"
__summary__= ("An asynchronous BLE Heart Monitor library with support for "
              "additional data from Polar monitors (ECG, accelerometers, PPG)")
__uri__= "https://github.com/fsmeraldi/bleakheart"

from ._version import __version__
from ._core import BatteryLevel, HeartRate, PolarMeasurementData
