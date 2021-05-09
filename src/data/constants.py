import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(ROOT_DIR, "src")
DATA_DIR = os.path.join(ROOT_DIR, "data")
DATA_DIR_RAW = os.path.join(DATA_DIR, "raw")
DATA_DIR_INTERIM = os.path.join(DATA_DIR, "interim")
DATA_DIR_PROCESSED = os.path.join(DATA_DIR, "processed")