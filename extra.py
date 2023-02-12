# Content
# Este arquivo contém o script que utilizei para carregar os produtos de products.json no banco de dados
# Para isso, precisei recriar a classe Product, pois na aplicação original, ela é criada utilizando flask-sqlalchemy,
# e importá-la aqui me traria problemas de contexto, pois o flask-sqlalchemy precisa de uma aplicação flask para funcionar
# Isto implica que alterações na classe Product traria problemas neste script, mas rodarei apenas uma vez, então não é um problema

import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime, func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.orm import sessionmaker
from alpha_store import tools
import random
import json


config = tools.load_config()

db_user = config["DATABASE"]["db_user"]
db_password = config["DATABASE"]["db_pass"]
db_host = config["DATABASE"]["db_host"]
db_name = config["DATABASE"]["db_name"]

db_uri = f"postgresql+pg8000://{db_user}:{db_password}@{db_host}/{db_name}"

engine = sqlalchemy.create_engine(db_uri, echo=True)

Base = declarative_base()


class Products(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(64), nullable=False)
    release_date = Column(DateTime, nullable=False)
    added_at = Column(DateTime, default=func.now())
    image_url = Column(String(256), nullable=False)
    score = Column(Float, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "added_at": self.added_at,
            "image_url": self.image_url,
            "score": self.score,
            "category": self.category,
            "release_date": self.release_date,
        }

    def __repr__(self) -> str:
        return f"<Products name={self.name}> description={self.description}>"


Session = sessionmaker(bind=engine)
session = Session()


# read json file
with open("products.json", "r") as f:
    data = json.load(f)

products = []

for product in data:
    products.append(
        Products(
            name=product["name"],
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            price=product["price"],
            category=product["category"],
            release_date=product["release_date"],
            image_url=product["image"],
            score=product["score"]
        )
    )

# add products to database
session.add_all(products)
session.commit()
