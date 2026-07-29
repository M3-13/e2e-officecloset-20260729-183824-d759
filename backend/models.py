import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class Category(enum.StrEnum):
    OBERTOPS = "Oberteile"
    HOSEN = "Hosen"
    KLEIDER = "Kleider"
    SCHUHE = "Schuhe"
    ACCESSOIRES = "Accessoires"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    clothing_items = relationship(
        "ClothingItem", back_populates="owner", cascade="all, delete-orphan"
    )
    outfits = relationship("Outfit", back_populates="owner", cascade="all, delete-orphan")


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(Enum(Category), nullable=False)
    image_path = Column(String(512), nullable=False)
    note = Column(Text, nullable=True, default=None)

    owner = relationship("User", back_populates="clothing_items")
    outfit_items = relationship(
        "OutfitItem", back_populates="clothing_item", cascade="all, delete-orphan"
    )


class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)

    owner = relationship("User", back_populates="outfits")
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    clothing_item_id = Column(Integer, ForeignKey("clothing_items.id"), nullable=False)

    outfit = relationship("Outfit", back_populates="items")
    clothing_item = relationship("ClothingItem", back_populates="outfit_items")

    __table_args__ = (UniqueConstraint("outfit_id", "clothing_item_id", name="uq_outfit_clothing"),)
