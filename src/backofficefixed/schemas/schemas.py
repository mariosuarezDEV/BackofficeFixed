from pydantic import BaseModel


class ConexionBD(BaseModel):
    server: str
    port: int
    database: str
    user: str
    passwd: str
