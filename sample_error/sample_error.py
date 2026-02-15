import logging

logging.basicConfig(
    filename='test.log',     
    level=logging.DEBUG,     
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def process_data(data):
    logging.info("Processing data...")
    return validate_data(data)

def validate_data(data):
    if not isinstance(data, dict):
        raise ValueError(f"Invalid data type: {type(data)}. Expected dict.")
    return data.get("value") / 0

def run_process():
    try:
        data = ["not", "a", "dict"]
        process_data(data)
    except Exception as e:
        import traceback
        logging.error("ERROR: Application encountered a critical failure")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    run_process()
