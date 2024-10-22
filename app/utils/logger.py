import logging

def get_logger():
    logger = logging.getLogger("fastapi_logger")
    
    # Check if logger already has handlers to avoid duplicate logs
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        # Create handlers (file and console)
        file_handler = logging.FileHandler("app.log")
        console_handler = logging.StreamHandler()

        # Create a formatter that includes time and message
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


