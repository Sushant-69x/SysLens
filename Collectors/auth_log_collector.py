import re
import os
from datetime import datetime
from Utils.logger import get_logger

logger = get_logger('AuthLogCollector')

# Windows log file path for testing
# On real Linux this would be /var/log/auth.log
AUTH_LOG_PATHS = [
    '/var/log/auth.log',       # Debian/Ubuntu/Kali
    '/var/log/secure',         # CentOS/RHEL
    'test_auth.log'            # Windows test file
]

# Regex patterns for auth log parsing
PATTERNS = {
    'FAILED_LOGIN': re.compile(
        r'(\w+\s+\d+\s+\d+:\d+:\d+).*sshd.*Failed password for (?:invalid user )?(\S+) from (\S+) port'
    ),
    'SUCCESS_LOGIN': re.compile(
        r'(\w+\s+\d+\s+\d+:\d+:\d+).*sshd.*Accepted password for (\S+) from (\S+) port'
    ),
    'SUDO': re.compile(
        r'(\w+\s+\d+\s+\d+:\d+:\d+).*sudo.*:\s+(\S+).*COMMAND=(.*)'
    ),
    'INVALID_USER': re.compile(
        r'(\w+\s+\d+\s+\d+:\d+:\d+).*sshd.*Invalid user (\S+) from (\S+)'
    )
}

class AuthLogCollector:
    def __init__(self, db_manager):
        self.db = db_manager
        self.log_path = self._find_log_file()
        self.last_position = 0

    def _find_log_file(self):
        for path in AUTH_LOG_PATHS:
            if os.path.exists(path):
                logger.info(f"Auth log found: {path}")
                return path
        logger.warning("No auth log found. Using test_auth.log")
        return 'test_auth.log'

    def _parse_line(self, line):
        for event_type, pattern in PATTERNS.items():
            match = pattern.search(line)
            if match:
                groups = match.groups()
                timestamp_str = groups[0]

                try:
                    current_year = datetime.now().year
                    timestamp = datetime.strptime(
                        f"{current_year} {timestamp_str}",
                        "%Y %b %d %H:%M:%S"
                    )
                except ValueError:
                    timestamp = datetime.now()

                if event_type in ('FAILED_LOGIN', 'SUCCESS_LOGIN', 'INVALID_USER'):
                    username = groups[1] if len(groups) > 1 else None
                    source_ip = groups[2] if len(groups) > 2 else None
                elif event_type == 'SUDO':
                    username = groups[1] if len(groups) > 1 else None
                    source_ip = None
                else:
                    username = None
                    source_ip = None

                return {
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'event_type': event_type,
                    'username': username,
                    'source_ip': source_ip,
                    'service': 'sshd',
                    'raw_line': line.strip()
                }
        return None

    def collect(self):
        events = []

        if not os.path.exists(self.log_path):
            logger.warning(f"Log file not found: {self.log_path}")
            return events

        try:
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(self.last_position)
                lines = f.readlines()
                self.last_position = f.tell()

            for line in lines:
                parsed = self._parse_line(line)
                if parsed:
                    events.append(parsed)

            if events:
                logger.info(f"Parsed {len(events)} auth events")

        except PermissionError:
            logger.error(f"Permission denied reading {self.log_path}")
        except Exception as e:
            logger.error(f"Auth log error: {e}")

        return events

    def collect_and_store(self):
        events = self.collect()
        for event in events:
            self.db.insert('auth_events', event)
        return events