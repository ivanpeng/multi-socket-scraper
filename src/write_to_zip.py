import zipfile
import os
from os.path import isfile, join

filepath = "testfilestozip/"
flist = [f for f in os.listdir(filepath) if isfile((join(filepath, f)))]

with zipfile.ZipFile("testZip.zip", 'a') as z:
    for f in flist:
        z.write(join(filepath,f))