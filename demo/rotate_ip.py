"""Run this to rotate the Tor exit IP. Watch localhost:5000 change."""
import time
from stem import Signal
from stem.control import Controller

with Controller.from_port(port=9151) as c:
    c.authenticate()
    c.signal(Signal.NEWNYM)

print("New Tor circuit requested — wait 5s then refresh the browser.")
time.sleep(5)
print("Done. Refresh http://localhost:5000")
