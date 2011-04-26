import subprocess

workers = []
for number in range (10):
    ret = subprocess.call(['python', 'worker.py', 'wrk%s' % str(number), '&'])
    workers.append(ret)

trackers = []
for number in range(5):
    subprocess.call(['python', 'tracker.py', 'trk%s' % str(number), '&'])
    ret = tracker.append(ret)

print workers
print trackers


