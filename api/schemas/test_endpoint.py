from pydantic import BaseModel

class Test_EndpointBase(BaseModel):
    name: str

class Test_EndpointCreate(Test_EndpointBase):
    pass

class Test_EndpointResponse(Test_EndpointBase):
    id: int

    class Config:
        orm_mode = True