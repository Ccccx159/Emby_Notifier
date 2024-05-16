from datetime import datetime, timezone, timedelta
import re

def iso8601_convert_CST(iso_time_str):
  """
  Converts an ISO 8601 formatted string to the China Standard Time (CST) timezone.

  Args:
    iso_time_str (str): The ISO 8601 formatted string representing a datetime.

  Returns:
    datetime: The converted datetime object in the China Standard Time (CST) timezone.
  """
  dt = datetime.fromisoformat(iso_time_str)
  return dt.astimezone(timezone.utc).astimezone(timezone(timedelta(hours=8)))


def contains_unicode_escape(s):
  """
  Checks if the given string contains any Unicode escape sequences.

  Args:
    s (str): The string to check.

  Returns:
    bool: True if the string contains Unicode escape sequences, False otherwise.
  """
  return re.search(r"\\u[0-9a-fA-F]{4}", s) is not None
