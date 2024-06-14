import logging
import pprint
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Contact, User
from src.schemas.contact import ContactSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def search_contacts(
    filters: dict, limit: int, offset: int, db: AsyncSession, user: User
):
    logging.info(f"search contacts, filter={filters}")
    stmt = select(Contact).where(Contact.user == user)

    for field, value in filters.items():
        if value:
            stmt = stmt.where(getattr(Contact, field).ilike(f"%{value}%"))
    stmt = stmt.offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    print(contacts)
    return contacts.scalars().all()


async def get_contact_by_id(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def add_contact(body: ContactSchema, db: AsyncSession, user: User):
    print(f"$$$$ add contact user= {user}")
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    print("!!!! add contact, commet & refresh")
    print(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactSchema, db: AsyncSession, user: User
):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        return None
    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.phone = body.phone
    contact.email = body.email
    contact.birthday = body.birthday
    contact.addition = body.addition
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact is None:
        return None
    await db.delete(contact)
    await db.commit()
    return contact


async def next_birthday(bd_list: list[str], db: AsyncSession, user: User):
    stmt = select(Contact).filter(
        func.to_char(func.to_date(Contact.birthday, "YYYY-MM-DD"), "MM-DD").in_(bd_list)
    )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()
