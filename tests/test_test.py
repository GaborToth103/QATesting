import logging

logging.basicConfig(
    filename='your_log_file.log', 
    filemode='w', 
    encoding='utf-8',  # Specify UTF-8 encoding
    level=logging.DEBUG
)

logging.debug('haló')
