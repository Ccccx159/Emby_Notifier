from datetime import datetime, timezone, timedelta

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