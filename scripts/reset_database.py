"""Drops all PolicyShadow tables from the database. Dry run unless --yes is passed."""

import sys

from sqlalchemy import inspect, text

from policyshadow.persistence.db import engine
from policyshadow.persistence.models import Base


def main() -> None:
    inspector = inspect(engine)
    existing = [name for name in Base.metadata.tables if inspector.has_table(name)]
    with engine.connect() as conn:
        for name in existing:
            count = conn.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar()
            print(f"{name}: {count} rows")
    if "--yes" not in sys.argv:
        print("Dry run only. Re-run with --yes to drop the tables above.")
        return
    Base.metadata.drop_all(engine)
    print("Dropped:", existing)


if __name__ == "__main__":
    main()
