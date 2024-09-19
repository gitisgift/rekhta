from pydantic import BaseModel
from typing import List


class Ghazal(BaseModel):
    title: str
    body: str
    source: str = ''

class Sher(BaseModel):
    body: str

class Poet(BaseModel):
    name: str
    real_name: str
    image: str = ''
    year_of_birth: str = ''
    year_of_death: str = ''
    city: str = ''
    ghazals: List[Ghazal]
    shers: List[Sher]




