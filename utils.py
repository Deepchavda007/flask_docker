import sys
import traceback
from queue import Queue
from logger_config import setup_logger


logger = setup_logger("My_Logger")

PROGRESS = {}
REQUEST_ID_QUEUE = []
request_queue = Queue(maxsize=10000)

def log_exception(e):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    trace_details = traceback.format_exception(exc_type, exc_value, exc_traceback)

    logger.error(f"Error: {str(e)}")
    logger.error(f"Exception type: {exc_type}")
    logger.error(f"Exception value: {exc_value}")
    logger.error(f"Exception traceback details: {''.join(trace_details)}")


def get_progress(request_id):
    if request_id not in PROGRESS:
        return 0, "No such id available"
    else:
        progress = PROGRESS[request_id]
        return progress, ""
    
def remove_request_id(request_id):
    del PROGRESS[request_id]


def update_progress(request_id, value):
    PROGRESS[request_id] = value
    REQUEST_ID_QUEUE.append(request_id)

    if len(REQUEST_ID_QUEUE) == 1000:
        oldest_batch_id = REQUEST_ID_QUEUE.pop(0)
        remove_request_id(oldest_batch_id)

# @app.route('/sum', methods=['POST'])
# @cross_origin()
# def sum_numbers():
#     data = request.get_json() 
#     print(data)
#     result = sum_number(data)
#     return jsonify({'result': result})