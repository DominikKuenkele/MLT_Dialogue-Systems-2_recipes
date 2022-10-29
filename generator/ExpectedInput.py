from Template import Template


class ExpectedInput(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.top_items = []

    def add_top_item(self, recipe_name, image_url) -> None:
        self.top_items.append({
            'action': f'{self._cleanse_attribute(recipe_name)}_action',
            'image_url': image_url,
            'alt_name': recipe_name
        })

    def _get_stub(self) -> str:
        stub = ''

        if len(self.top_items) > 1:
            perform_goal_stub = ', '.join([f'goal(perform({top_item["action"]}))' for top_item in self.top_items])
            current_plan_item = f'findout(?set([{perform_goal_stub}]))'

            plan_stubs = []
            for top_item in self.top_items:
                plan_stubs.append(f'''    {{
        "current_plan_item": "{current_plan_item}",
        "semantic_expression": "request({top_item["action"]})",
        "alternative": {{
            "visual_information": [
                {{
                    "attribute": "name",
                    "type": "text/plain",
                    "value": "{top_item["alt_name"]}"
                }},
                {{
                    "attribute": "image",
                    "type": "image/jpeg",
                    "value": "{top_item["image_url"]}"
                }}
            ]
        }}
    }}''')
            stub = ',\n'.join(plan_stubs)

        return stub
