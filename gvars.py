import threading

PORT = 5999
state = "FOLLOWER"
test_range = 1000000
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
logger = None
debug = False
foundBy = ""
informed_electors = set()
