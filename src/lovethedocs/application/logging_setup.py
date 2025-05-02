import logging

# Configure once, then just import this module.
logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
