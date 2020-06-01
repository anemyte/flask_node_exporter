# Flask Wrapper For Node Exporter

This simple Flask app works like proxy for node exporter. It starts a manager process, which runs
node_exporter binary on a random port and keeps it alive via healthchecks. When you access "/metrics" 
route on this Flask app, it makes a request to the exporter and returns you contents of that request. 

# Why

I've made this to monitor a website on a shared hosting. All ports, except ones intentionally opened by
hosting administrators, were closed so there was no chance to access node exporter on 9100 or any other port.
But there was a way to run Flask apps and so I made this little wrapper.

# Usage

Install packages from requirements.txt with:
```shell script
pip install -r requirements.txt
```
Get yourself a node exporter binary from [here](https://github.com/prometheus/node_exporter) if you still don't have one, 
then write path to your node exporter binary in `NODE_EXPORTER_BINARY_PATH` variable inside `app.py`. 

That's all.
