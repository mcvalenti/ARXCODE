'''
Created on 03/05/2017

@author: mcvalenti
'''

# from progressbar import Bar
# 
# bar = Bar('#', left='|', right='|', fill=' ',fill_left=True)
# n=0
# for i in range(20):
#     # Do some work
#     n=n+1
#     
# import time
# from progressbar import Bar 
# 
# bar = Bar('#', max=20, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
# for i in range(20):
#     time.sleep(.05) # Do some work
#     bar.next()
# bar.finish()
from time import sleep
import progressbar

with progressbar.ProgressBar(max_value=10) as progress:
    for i in range(10):
        # do something
        sleep(0.1)
        progress.update(i)