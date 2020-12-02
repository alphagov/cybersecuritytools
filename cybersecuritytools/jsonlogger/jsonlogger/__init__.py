""" Declare a logger to be used by any module """
import datetime
import json
import logging
import os
import sys


class JsonFormatter(logging.Formatter):
    """ Handle log invokes with string, dict or json.dumps """

    def format(self, record: logging.LogRecord) -> str:
        """ Detect formatting of self message and encode as valid JSON """
        data = {}
        data.update(vars(record))
        try:
            parsed = json.loads(record.msg)
            if type(parsed) in [dict, list]:
                data["msg"] = parsed
        except (ValueError, TypeError, json.JSONDecodeError):
            pass

        try:
            if ("args" in data) and len(data["args"]) > 0:
                args = data["args"]
                data["msg"] = data["msg"] % args
        except TypeError:
            pass

        data["timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        try:
            log_message = json.dumps(data, default=str)
        except (TypeError, ValueError) as err:
            log_message = "logger_error=" + str(err) + ";event=" + str(data)
        return log_message


def build_logger(log_name: str, log_level: str = "ERROR") -> logging.Logger:
    """ Create shared logger and custom JSON handler """
    logger = logging.getLogger(log_name)
    handler = logging.StreamHandler(sys.stdout)
    # For some reason mypy doesn't understand sub-classes
    handler.setFormatter(JsonFormatter)  # type: ignore
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, log_level))
    return logger


LOG_LEVEL = str(os.getenv("LOG_LEVEL", "ERROR"))
LOG = build_logger("json_logger", log_level=LOG_LEVEL)
