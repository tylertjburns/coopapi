from pydantic.dataclasses import dataclass as pydandataclass, Field
from cooptools.randoms import a_string, a_phrase

class DummySchemaConfig:
    allow_population_by_field_name = True
    schema_extra = {
        "example": {
            'id': a_string(10),
            'desc': a_phrase(10),
            'active': True,
        }
    }

@pydandataclass(config=DummySchemaConfig)
class DummySchema:
    id: str = Field(...)
    desc: str = Field(...)
    active: bool = Field(...)