import csv
import io
from datetime import datetime, timezone
from typing import List

from src.db import ExpenseRow


def rows_to_csv_bytes(rows: List[ExpenseRow]) -> io.BytesIO:
    sio = io.StringIO(newline="")

    columns = list(ExpenseRow.model_fields.keys())

    writer = csv.DictWriter(sio, fieldnames=columns)
    writer.writeheader()
    for r in rows:
        writer.writerow(r.model_dump())

    # Wrap text in BytesIO and give it a filename
    bio = io.BytesIO(sio.getvalue().encode("utf-8"))
    bio.name = f"expenses_{datetime.now(timezone.utc).date().isoformat()}.csv"
    return bio
