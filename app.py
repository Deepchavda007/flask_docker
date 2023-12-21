import os
import time
from utils import *
from main import sum_number
from threading import Thread
from termcolor import colored
from logger_config import setup_logger
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.exceptions import BadRequest


logger = setup_logger("My_Logger")


def create_response(status, message, data, code):
    return jsonify({"status": status, "message": message, "data": data}), code


def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    app.logger = logger
    app.queue = request_queue

    return app


# Creating Flask App
app = create_app()

# ----------------- ERROR HANDLERS ----------------- #


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    app.logger.error(f"BadRequest: {e.description}")
    return create_response(False, str(e), {}, 400)


@app.errorhandler(500)
def handle_server_error(e):
    app.logger.error("Internal Server Error")
    return create_response(False, "Internal Server Error", {}, 500)


def safe_process_requests():
    while True:
        try:
            process_requests()
        except Exception as e:
            log_exception(e)
            app.logger.error(colored(f"Error in process_requests thread: {e}", "red"))

def process_requests():
    while True:
        data = app.queue.get()
        try:
            sum_number(data)
        except Exception as e:
            log_exception(e)
            app.logger.error(colored(f"Error processing request: {e}", "red"))
        finally:
            app.queue.task_done()


def request_progress(parameters):
    batch_id = parameters.get("batch_id")
    if not batch_id:
        return create_response(False, "batch_id is missing", {}, 400)

    progress, error = get_progress(batch_id)

    if error:
        return create_response(
            False, error, {"batch_id": batch_id, "progress": progress}, 400
        )
    else:
        return create_response(
            True, "Success", {"batch_id": batch_id, "progress": progress}, 200
        )


@app.route("/request_progress", methods=["GET"])
def request_progress_route():
    return handle_request(request_progress)


@app.route("/queue_data", methods=["GET"])
def queue_data_route():
    data = [item for item in app.queue.queue]
    return jsonify(data)


def handle_request(func):
    try:
        par = request.json if request.method == "POST" else request.args
        app.logger.info(colored(par, "cyan"))
        print(colored(par, "cyan"))
        response, status_code = func(par)
        return response, status_code
    except Exception as e:
        log_exception(e)
        return {
            "data": {},
            "status": False,
            "message": f"Error: An error occurred {e}",
        }, 400


def take_sum_request(par):
    required_params = ["a", "b", "batch_id"]
    if any(param not in par for param in required_params):
        return create_response(False, "Required parameter missing", {}, 400)

    # Check if 'a' and 'b' are integers
    if not isinstance(par['a'], int) or not isinstance(par['b'], int):
        return create_response(False, "'a' and 'b' must be integers", {}, 400)

    update_progress(par["batch_id"], 0)

    app.queue.put(par)

    return create_response(True, "Success", par, 200)


@app.route('/sum', methods=['POST'])
@cross_origin()
def sum_numbers():
    return handle_request(take_sum_request)


def main():
    # Setup and start the processing thread.
    def start_processing_thread():
        processing_thread = Thread(target=safe_process_requests)
        processing_thread.daemon = True  # Ensure thread dies with the main process
        processing_thread.start()
        return processing_thread

    processing_thread = start_processing_thread()

    # Checking the thread's health every 10 seconds and restart if it's dead.
    def monitor_and_restart_thread():
        while True:
            time.sleep(10)
            if not processing_thread.is_alive():
                app.logger.warning("Processing thread was dead. Restarting...")
                start_processing_thread()

    monitor_thread = Thread(target=monitor_and_restart_thread)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Start the Flask app.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=False)




###--------------------------------------------------------------------------###

if __name__ == "__main__":
    main()

