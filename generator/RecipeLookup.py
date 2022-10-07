import json
from Template import Template

class RecipeLookup(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.lookup = {}

    def add_recipe(self, recipe_name) -> None:
        self.lookup[self._cleanse_attribute(recipe_name)] = {
            "ingredients": {},
            "steps": {}
        }
    
    def add_ingredient(self, ingredient, amount, recipe_name, step=None) -> None:
        ingredient = self._cleanse_attribute(ingredient)
        recipe_name = self._cleanse_attribute(recipe_name)
        if step == None:
            self.lookup[recipe_name]["ingredients"][ingredient] = amount
        else:
            step = self._cleanse_attribute(step)
            if step not in self.lookup[recipe_name]["steps"]:
                self.lookup[recipe_name]["steps"] = {
                    step: {
                        "ingredients": {}
                    }
                }
            self.lookup[recipe_name]["steps"][step]["ingredients"][ingredient] = amount

    def _get_stub(self) -> str:
        return json.dumps(self.lookup, indent=4)