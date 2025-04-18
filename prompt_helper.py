def build_prompt(user_query):
    return f"""
You are a Prometheus PromQL expert.

The available metrics include:
- node_cpu_seconds_total
- node_memory_MemTotal_bytes
- node_memory_MemAvailable_bytes
- node_network_receive_bytes_total
- node_network_transmit_bytes_total
- node_filesystem_avail_bytes

Convert the following request into a valid PromQL query:

"{user_query}"

Only return the raw PromQL query. No explanation.
"""
