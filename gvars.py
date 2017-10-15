import threading

PORT = 5999
state = "FOLLOWER"
executionMode = "COMPUTING"
test_range = 1000
processed_count = 0
lock = threading.Lock() 
isComposite = False
p = None 
intervals = None
calculated_intervals = None
original_interval_count = None 
start = None
connected_ips = []
votes = {}
leader_ip = ''
done = False
broadcasted_count = 0
