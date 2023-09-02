import os, sys, time
from datetime import datetime, timedelta
from shutil import copyfile
import traceback
import re

import MyLibs.PyObject_to_PyFile as PyFile
from MyLibs.Time import *


T1 = now_utc()
#data1 = datetime_to_str(local_to_utc(T1), '%Y.%m')
data1 = datetime_to_str(T1, '%Y.%m')
T2 = T1 - timedelta(days = 30)
#data2 = datetime_to_str(local_to_utc(T2), '%Y.%m')
data2 = datetime_to_str(T2, '%Y.%m')
dates = set([data1, data2])


print(T1, data1)
print(T2, data2)
print(dates)