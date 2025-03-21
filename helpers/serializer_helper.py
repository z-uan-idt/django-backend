from rest_framework import serializers

import re


class SerializerHelper:
    @staticmethod
    def text_choice_value(value):
        return {
            "label": getattr(value, "label", None),
            "value": getattr(value, "value", None),
        }

    class TextChoiceValueField(serializers.ChoiceField):
        def to_representation(self, value):
            if value is None or not self.choices:
                return None

            choices = self.choices

            if hasattr(choices, "choices"):
                choices = choices.choices

            choice_value = dict(choices).get(value) or {}

            return {
                "label": getattr(choice_value, "label", None),
                "value": getattr(choice_value, "value", None),
            }

    class CoordinatesField(serializers.CharField):
        """
        Ví dụ: "90.987654,105.348321" or "90.987654,105.348321;90.987654,105.348321;..."
        """

        def __init__(self, **kwargs):
            kwargs.setdefault("error_messages", {})
            kwargs["error_messages"].update(
                {
                    "invalid_format": 'Tọa độ phải có dạng "lat,lng" hoặc "lat,lng;lat,lng;..."',
                    "invalid_coords": "Tọa độ không đúng định dạng. Latitude(-90, 90), Longitude(-180, 180)",
                    "invalid_latitude": "Vĩ độ không đúng định dạng (-90, 90)",
                    "invalid_longitude": "Kinh độ không đúng định dạng (-180, 180)",
                }
            )
            super().__init__(**kwargs)

        def to_internal_value(self, value):
            value = super().to_internal_value(value)

            pattern = r"^(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)(?:;(-?\d+(\.\d+)?),(-?\d+(\.\d+)?))*$"
            if not re.match(pattern, value):
                self.fail("invalid_format")

            coord_pairs = value.split(";")
            for pair in coord_pairs:
                lat, lng = map(float, pair.split(","))

                if not (-90 <= lat <= 90):
                    self.fail("invalid_latitude")

                if not (-180 <= lng <= 180):
                    self.fail("invalid_longitude")

            return tuple(tuple(map(float, pair.split(","))) for pair in coord_pairs)

        def to_representation(self, value):
            return value


    class ModelSerializer(serializers.ModelSerializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            model_class = self.Meta.model
            
            for field_name, field in self.fields.items():
                try:
                    model_field = model_class._meta.get_field(field_name)
                    
                    if hasattr(model_field, 'error_messages') and model_field.error_messages:
                        field.error_messages.update(model_field.error_messages)
                except Exception:
                    continue