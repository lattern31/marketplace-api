from datetime import datetime
from typing import Annotated

from sqlalchemy import text
from sqlalchemy.orm import mapped_column


intpk = Annotated[int, mapped_column(primary_key=True)]
strpk = Annotated[str, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())")
)]
