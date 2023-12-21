import time
import uuid
from utils import *
from termcolor import colored

def sum_number(par):
    time.sleep(9)
    required_params = ["a", "b", "batch_id"]
    if any(param not in par for param in required_params):
        return {
            "data": {},
            "status": False,
            "message": "Required parameters missing a or b",
        }, 400
    try:
        batch_id = par["batch_id"]
        result = par['a'] + par['b']
        print(colored(f"Batch_id : {batch_id} Result is {result}", "cyan"))
        update_progress(batch_id, 100)
        return {
                 "data":{
                            "result" : result,
                            "batch_id":batch_id
                        },
                "status": True,
                "message": "Success",
                },200
    
    except Exception as e:
        return {
            "data": {},
            "status": False,
            "message": str(e),
        }, 400


if __name__ == '__main__':
    batch_id = str(uuid.uuid4())

    data = {"batch_id":batch_id, 'a': 1, 'b': 2}
    print(colored(sum_number(data), "green"))




