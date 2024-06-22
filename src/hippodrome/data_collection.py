import os
import pathlib
from typing import NewType

from hippodrome import message

from pymongo import MongoClient
from pydantic import BaseModel


DO_DATA_COLLECTION = os.environ.get("DO_DATA_COLLECTION", 0)

JSONL_DATA_DIR = os.environ.get("JSONL_DATA_DIR")

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")
DB_NAME = os.environ.get("MONGODB_NAME")

Model = NewType("Model", BaseModel)


def save(log_object: Model):
    collection = get_collection(log_object)

    # If data collection is disabled, return early
    if not DO_DATA_COLLECTION:
        return

    # Multiple data collection modes can be enabled at once

    # JSONL mode, saves data to a local JSONL file
    if JSONL_DATA_DIR:
        data_dir = JSONL_DATA_DIR
        log_file = os.path.join(data_dir, f"{collection}.jsonl")

        with open(log_file, "a+") as f:
            f.write(log_object.model_dump_json() + "\n")

    # MongoDB mode, saves data to a MongoDB database
    if MONGODB_CONNECTION_STRING:
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client[DB_NAME]
        db[collection].insert_one(log_object.model_dump())


def get_collection(log_object: Model) -> str:
    from hippodrome import Game, Player

    if isinstance(log_object, message.AgentMessage):
        collection = "messages"
    elif isinstance(log_object, Player):
        collection = "players"
    elif isinstance(log_object, Game):
        collection = "games"
    else:
        raise ValueError(f"Unknown log object type: {type(log_object)}")

    return collection
