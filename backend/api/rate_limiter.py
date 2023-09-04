import logging
from datetime import datetime, timedelta
import time

# Initialize logging
logging.basicConfig(filename='app.log', level=logging.INFO)  # Change level to INFO for more detailed logs
console = logging.StreamHandler()
logging.getLogger().addHandler(console)

# Class to manage API state during runtime
class ApiState:
    def __init__(self):
        self.total_requests = 0
        self.total_items_fetched = 0
        self.total_items_saved = 0
        self.batch_counter = 0
        self.first_request_time = None 

    def check_and_reset_rate_limit(self):
        current_time = datetime.now()
        if self.first_request_time is None:
            self.first_request_time = current_time

        if current_time - self.first_request_time >= timedelta(hours=1):
            self.total_requests = 0
            self.first_request_time = current_time

        if self.total_requests >= 990:  # Adjusted the limit to 990 as per your standalone function
            logging.warning("Approaching rate limit. Pausing for 1 hour.")
            time.sleep(3600)  # 1 hour
            self.total_requests = 0  # Reset the counter

# Instantiate ApiState class to manage API state globally
api_state = ApiState()
