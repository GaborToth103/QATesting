import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler(), logging.FileHandler('/mnt/shared/tothg/project/QATesting/docs/info.log')])

logging.info("asd")