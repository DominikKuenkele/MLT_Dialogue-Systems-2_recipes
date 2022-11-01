from Template import Template


class VisualOutput(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.expressions = []

    def add_expression(self, step_name, image_url, text) -> None:
        self.expressions.append(f'''    {{
        "semantic_expression": "request({self._cleanse_attribute(step_name)})",
        "visual_information": [
            {{
                "attribute": "name",
                "type": "text/plain",
                "value": "{text}"
            }},
            {{
                "attribute": "image",
                "type": "image/jpeg",
                "value": "{image_url}"
            }}
        ]
    }}''')

    def _get_stub(self) -> str:
        return ',\n'.join(self.expressions)
