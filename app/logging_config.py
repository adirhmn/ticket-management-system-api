import json
import logging
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        
        # Capture stack traces if exception info exists
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        # Capture extra custom parameters dynamically
        standard_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'message'
        }
        extra = {k: v for k, v in record.__dict__.items() if k not in standard_fields}
        if extra:
            log_record["extra"] = extra
            
        return json.dumps(log_record)
