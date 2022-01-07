from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.operators import is_
from db.models import Photo, User, RatingAssociation


async def add_photo(user_id: int, data: str, title: str, t_upload, pool: sessionmaker):
    async with pool() as sess:
        async with sess.begin():
            sess.add(Photo(user_id=user_id, data=data, title=title, t_upload=t_upload))


async def add_user(user_id: int, name: str, pool: sessionmaker):
    async with pool() as sess:
        async with sess.begin():
            sess.add(User(id=user_id, name=name))


async def get_available(pool: sessionmaker) -> list:
    async with pool.begin() as sess:
        return [(p, t) for p, t in (await sess.execute(select(Photo.title, Photo.id))).all()]


async def get_photo(photo_id: int, pool: sessionmaker) -> str:
    async with pool() as sess:
        return (await sess.execute(select(Photo.data).where(Photo.id==photo_id))).scalar()


async def send_reaction(user_id: int, photo_id: int, action: bool, pool: sessionmaker):
    async with pool() as sess:
        async with sess.begin():
            upsert_action = insert(RatingAssociation).values(user_id=user_id, photo_id=photo_id, action=action).\
                on_conflict_do_update(
                index_elements=[RatingAssociation.user_id, RatingAssociation.photo_id], set_=dict(action=action))
            await sess.execute(upsert_action)


async def get_rating_by_id(photo_id: int, pool: sessionmaker) -> tuple:
    async with pool() as sess:
        likes_dislikes = select(func.count('*').filter(is_(RatingAssociation.action, True)),
                                func.count('*').filter(is_(RatingAssociation.action, False))).\
            where(RatingAssociation.photo_id==photo_id)
        return (await sess.execute(likes_dislikes)).first()
