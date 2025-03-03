import json
import typing

from alchemancer import Field


class JsonBField(Field):
    def _serialize(self, value: typing.Any, attr: str | None, obj: typing.Any, **kwargs):
        if value is None:
            return None

        if isinstance(value, dict):
            return value

        if len(value) == 0:
            return value

        leading_char = value[0]
        if leading_char != "[" and leading_char != "{":
            trailing_char = value[-1]
            if trailing_char != "]" and trailing_char != "}":
                return value

        return json.loads(value)

    def _deserialize(
        self,
        value: typing.Any,
        attr: str | None,
        data: typing.Mapping[str, typing.Any] | None,
        **kwargs,
    ):
        return json.dumps(value)


class JsonField(Field):
    def _serialize(self, value: typing.Any, attr: str | None, obj: typing.Any, **kwargs):
        if value is None:
            return None

        if isinstance(value, dict):
            return value

        if len(value) == 0:
            return value

        leading_char = None
        trailing_char = None
        for character in value:
            if character in [" ", "\n", "\t", "\n\r"]:
                continue

            leading_char = character
            break

        for character in reversed(value):
            if character in [" ", "\n", "\t", "\n\r"]:
                continue

            trailing_char = character
            break

        if (leading_char != "[" and leading_char != "{") and (
            trailing_char != "]" and trailing_char != "}"
        ):
            return value

        return json.loads(value)

    def _deserialize(
        self,
        value: typing.Any,
        attr: str | None,
        data: typing.Mapping[str, typing.Any] | None,
        **kwargs,
    ):
        return json.dumps(value)
