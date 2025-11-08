import threading
import time

import uvicorn

import logic
from routes import app


def check_arl_status_thread():
    while True:
        logic.update_arl_status()
        time.sleep(20 * 60)  # Check every 20 minutes


if __name__ == '__main__':
    threading.Thread(target=check_arl_status_thread).start()
    uvicorn.run(app, host="0.0.0.0", port=80)
