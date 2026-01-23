import urllib.request
import time
import sys

url = 'http://127.0.0.1:5000/'

try:
    for i in range(300):
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                print(time.strftime('%Y-%m-%d %H:%M:%S'), 'OK', r.status)
        except Exception as e:
            print(time.strftime('%Y-%m-%d %H:%M:%S'), 'ERR', repr(e))
        sys.stdout.flush()
        time.sleep(1)
except KeyboardInterrupt:
    print('Stopped')
