from dataclasses import dataclass
from enum import Enum


@dataclass
class Product:
    _id: int 
    name: str
    category: str 
    price_default: float
    price_discount: float
    available_status: Enum
    link: str 


@dataclass
class Category:
    name: str 
    link: str
