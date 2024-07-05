from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String,Float,ForeignKey,create_engine
from sqlalchemy.orm import Mapped, mapped_column,relationship,sessionmaker
import logging
from typing import List


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class Category(db.Model):
     __tablename__ = "category"
     id : Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
     category_name : Mapped[str] = mapped_column(String(50))
     product:Mapped[List["Product"]] = relationship(back_populates="category")

class Product(db.Model):
    __tablename__ = "product"
    product_id    : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(50))
    price: Mapped[int] = mapped_column(Integer)
    category_id  : Mapped[int] = mapped_column(ForeignKey("category.id"))
    category:Mapped["Category"] = relationship("Category",back_populates="product")
    image:Mapped["Image"] = relationship(back_populates="product")


class Image(Base):
   __tablename__ = "image"
   image_id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
   image : Mapped[str] = mapped_column(String(255))
   p_id : Mapped[int] =  mapped_column(ForeignKey("product.product_id"))
   product :Mapped["Product"]= (relationship("Product",back_populates="image"))


def init_db(db_uri='postgresql://flask_user:12345@localhost:5432/flaskdb'):
    logger = logging.getLogger("FlaskApp")
    engine = create_engine(db_uri)
    Base.metadata.create_all(engine)
    logger.info("Created database")

def get_session(db_uri):
    engine = create_engine(db_uri)
    Session = sessionmaker(bind = engine)
    session = Session()
    return session






   
   
