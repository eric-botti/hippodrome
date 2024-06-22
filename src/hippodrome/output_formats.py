import random
from typing import Annotated, NewType, List, Optional, Type, Literal
import json

from pydantic import BaseModel, field_validator, Field, model_validator

FORMAT_INSTRUCTIONS = """Please reformat your previous response as a JSON instance that conforms to the JSON structure below.
Here is the output format:
{schema}
"""


class OutputFormatModel(BaseModel):
    @classmethod
    def get_format_instructions(cls) -> str:
        """Returns a string with instructions on how to format the output."""
        json_format = {}
        for field in cls.model_fields:
            if not cls.model_fields[field].exclude:
                json_format[field] = cls.model_fields[field].description

        # In the future, we could instead use get_annotations() to get the field descriptions
        return FORMAT_INSTRUCTIONS.format(schema=json.dumps(json_format))