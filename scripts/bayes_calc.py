import numpy as np
import time

def add_two_arrays(a,b):
    for i,j in zip(a,b):
        v = i+j
        #time.sleep(0.1)
        print(v)