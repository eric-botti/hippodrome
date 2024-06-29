from typing import Type

from pydantic import ValidationError, Field

from hippodrome.output_formats import OutputFormatModel
from hippodrome.message import Message
from hippodrome.controllers import BaseController


class BaseHumanController(BaseController):
    is_human: bool = Field(default=True, frozen=True)

    def generate_formatted_response(
            self,
            output_format: Type[OutputFormatModel],
            additional_fields: dict = None,
            max_retries: int = 3
    ) -> OutputFormatModel | None:
        """For Human controllers, we can trust them enough to format their own responses... for now"""
        response = self.generate_response()

        if response:
            # only works because current outputs have only 1 field...
            try:
                fields = {output_format.model_fields.copy().popitem()[0]: response.content}
                if additional_fields:
                    fields.update(additional_fields)
                output = output_format.model_validate(fields)

            except ValidationError as e:
                retry_message = Message(type="retry", content=f"Error formatting response: {e} \n\n Please try again.")
                self.add_message(retry_message)
                output = None

        else:
            output = None

        return output
