import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import os

import matplotlib.pyplot as plt
import numpy as np
import pickle
import csv

path = "/Users/dogfish/GI/git/SHIB_decision_support"
file = "SHIBUSDT.csv"
sdf = pd.read_csv(os.path.join(path, file))

def didSHIBfall(time, open, close, threshold=0.05):
  drop_interval = -1
  drop = 0
  xx = 0
  drop_found = False

  sdf = open[xx]
  first_time = time[0]
  first_open = open[0]
  # print(f"first open: {first_open}")
  # if first_open > (3e-5):
  #   print('blah')
  max_drop = max(open) - min(close)
  max_pcnt = max_drop / first_open

  if max_pcnt > threshold:
    drop_interval = -1
    for xx in range(0, len(time) - 1):
      blah = [first_open - close[xx], first_open - open[xx + 1]]
      max_blah = max(blah)
      drop = max_blah / first_open
      if drop >= threshold:
        drop_found = True
        mx = blah.index(max_blah)
        if mx == 0:
          rx = xx
          sdf = close[xx]
        else:
          rx = xx + 1
          sdf = open[xx+1]
        drop_interval = time[rx] - first_time
        break

    if not drop_found: # xx == (len(time)-1) and (len(time) >1):
      xx = 0

  return drop_found,drop_interval,xx,drop,sdf,first_open

th_drop_intervals = []
th_drop_kxs = []
th_drop_xxs = []
th_drop_vals = []
th_drop_sdf = []
th_drop_open = []

thresholds = [5/100] # list( np.array(range(4,20,7)) / 100 ) #0.01,0.2,0.01)
for threshold in thresholds:

  print(" ")
  print("Evaluating at Next Threshold")
  print(" ")

  # time,open,high,low,close,Volume,Volume MA,RSI,RSI-based MA,Upper Bollinger Band,Lower Bollinger Band,P/S ratio
  sx = 0
  ex = -1
  drop_intervals = []
  drop_kxs = []
  drop_xxs = []
  drop_vals = []
  drop_sdf = []
  drop_open = []
  # _time = list(sdf['time'][sx:ex])
  # _open = list(sdf['open'][sx:ex])
  # _close = list(sdf['close'][sx:ex])
  # drop_found,interval,start_x,drop,sdfoc = didSHIBfall(_time,_open,_close,threshold=threshold)
  # xx = start_x
  drop_found = False

  for k in range(0,sdf.shape[0]):

    _time = list(sdf['time'][k:ex])
    _open = list(sdf['open'][k:ex])
    _close = list(sdf['close'][k:ex])

    if len(_time) <= 0:
      break

    drop_found,interval,xx,drop,sdfoc,first_open = didSHIBfall(_time,_open,_close,threshold=0.05)

    sx = k + xx  # record the event
    if drop_found and ((len(drop_open)==0) or (first_open > drop_open[-1]) or (sx > drop_xxs[-1])):
      # print(f"sx & xx: {sx} & {xx}")
      drop_intervals += [interval]
      drop_kxs += [k]
      drop_xxs += [sx]
      drop_vals += [drop]
      drop_sdf += [sdfoc]
      drop_open += [first_open]
      # print(f"{sx}")
      # if xx <= 0:
      #   sx += 1
    # else:
    # # if not drop_found: # (interval == -1) or (xx <= 0):
    #   sx += 1

  th_drop_intervals += [drop_intervals]
  th_drop_kxs       += [drop_kxs]
  th_drop_xxs       += [drop_xxs]
  th_drop_vals      += [drop_vals]
  th_drop_sdf       += [drop_sdf]

  # plot
  fig, ax = plt.subplots()

  drop_int_csum = np.cumsum( drop_intervals )
  # hst,edges = np.histogram(np.diff(drop_xxs), bins=15)
  # drop_diffs = [drop_xxs[k]-drop_xxs[k-1] for k in range(1,len(drop_xxs)) if (drop_xxs[k]-drop_xxs[k-1])<(7*24)] # np.diff(drop_xxs)
  drop_diffs = [drop_xxs[k]-drop_kxs[k] for k in range(1,len(drop_xxs)) if (drop_xxs[k]-drop_kxs[k])<(21*24)]
  hst,edges = np.histogram( drop_diffs, bins=15)

  _ = plt.hist( drop_diffs, bins='auto')
  plt.title(f"SHIB {threshold*100.0}% Event Rates Histogram")
  plt.xticks(edges,rotation=40)
  # plt.show()


  fg2, ax2 = plt.subplots()
  # ax2.plot( drop_int_csum, drop_vals, linewidth=2.0)
  ax2.plot( drop_int_csum, drop_sdf, linewidth=2.0 )
  # for dx in range(0,len(drop_int_csum)):
  #   plt.scatter( drop_int_csum, y, s=80, c=z, marker=">")
  # plt.show()


  fg3, ax3 = plt.subplots()
  ax3.plot( sdf['time'], sdf['open'] )
  ax3.scatter( sdf['time'][drop_xxs], sdf['open'][drop_xxs], s=80, c=drop_vals, marker=".")#>")
  plt.show()
  print('')

th_drop_stats = [th_drop_intervals, th_drop_xxs, th_drop_vals, th_drop_sdf]
with open('SHIBthresholds.pkl', 'wb') as f:
  pickle.dump(th_drop_stats, f)

# for k in range(thresholds):
#   t = thresholds[k]
th_drop_intervals = pd.DataFrame(list(np.array(th_drop_intervals).T))
th_drop_intervals.columns = ['rate']
th_drop_intervals.to_csv('SHIBUSDT_event.csv')

# with open('SHIBUSDT_event.csv','w') as f:
  # write = csv.writer(f)
  # write.writerows(th_drop_intervals)

# # Getting back the objects:
# with open('objs.pkl') as f:  # Python 3: open(..., 'rb')
#   obj0, obj1, obj2 = pickle.load(f)