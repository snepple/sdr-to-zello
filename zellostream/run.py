# ... [Keep previous imports and helper functions] ...

def setup_active_instances():
    """Determines which channel slots have active Zello credentials."""
    active_configs = {}
    
    # Check Channel 1
    if os.getenv('CH1_USERNAME') or os.getenv('ZELLO_USERNAME'):
        active_configs[1] = setup_channel_config(1, 9123)
        
    # Check Channel 2
    if os.getenv('CH2_USERNAME'):
        active_configs[2] = setup_channel_config(2, 9124)
        
    return active_configs

try:
    state = get_error_state()
    config_map = setup_active_instances()
    
    if not config_map:
        raise Exception("No Zello credentials found. Set CH1_USERNAME or CH2_USERNAME.")

    # Start only the requested instances
    procs = {cid: start_instance(path) for cid, path in config_map.items()}
    log_buffers = {cid: deque(maxlen=10) for cid in procs.keys()}

    # ... [Keep the monitoring loop] ...
