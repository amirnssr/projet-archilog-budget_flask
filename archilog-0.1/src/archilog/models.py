import uuid
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, String, Float, MetaData, Table, insert, update, delete


# Creation de la base de donnees
engine = create_engine("sqlite:///data.db", echo=True)
metadata = MetaData()



# Definition de la table
profile_table = Table(
    "profile",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String),
    Column("amount", Float),
    Column("category", String, nullable=True),
)

# Creation de la table dans la base de données
metadata.create_all(engine)

def init_db():
    metadata.create_all(engine)

@dataclass
class Entry:
    id: uuid.UUID
    name: str
    amount: float
    category: str | None

    @classmethod
    def from_db(cls, id: str, name: str, amount: float, category: str | None):
        return cls(uuid.UUID(id), name, amount, category)


def create_entry(name: str, amount: float, category: str | None = None) -> None:
    new_entry = {
        "id": uuid.uuid4().hex,
        "name": name,
        "amount": amount,
        "category": category,
    }
    stmt = insert(profile_table).values(new_entry)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def get_entry(id: uuid.UUID) -> Entry:
    with engine.connect() as conn:
        result = conn.execute(profile_table.select().where(profile_table.c.id == id.hex)).fetchone()
        if result:
            return Entry.from_db(*result)
        else:
            raise Exception("Entry not found")


def get_all_entries() -> list[Entry]:
    with engine.connect() as conn:
        results = conn.execute(profile_table.select()).fetchall()
        return [Entry.from_db(*r) for r in results]
    
    
def update_entry(id: uuid.UUID, name: str, amount: float, category: str | None) -> None:
    stmt = (
        update(profile_table)
        .where(profile_table.c.id == id.hex)
        .values(name=name, amount=amount, category=category)
    )
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def delete_entry(id: uuid.UUID) -> None:
    stmt = delete(profile_table).where(profile_table.c.id == id.hex)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
