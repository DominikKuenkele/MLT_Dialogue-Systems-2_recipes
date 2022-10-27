import json

from numpy import object_
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

    def add_ingredient(self, recipe_name, ingredient, amount, form) -> None:
        recipe_name = self._cleanse_attribute(recipe_name)
        ingredient = self._cleanse_attribute(ingredient)
        self.lookup[recipe_name]['ingredients'][ingredient] = {
            'amount': amount,
            'form': form
        }

    def add_substep(self, recipe_name, step_name, ingredient_attributes={}, object_attributes={}, time=None, condition=None):
        recipe_name = self._cleanse_attribute(recipe_name)
        step_name = self._cleanse_attribute(step_name)

        ingredient_lookup = {}
        if len(ingredient_attributes) != 0:
            ingredient = self._cleanse_attribute(ingredient_attributes['name'])
            ingredient_lookup[ingredient] = {
                'amount': ingredient_attributes['amount'],
                'form': ingredient_attributes['form']
            }

        object_lookup = {}
        if len(object_attributes) != 0:
            object = self._cleanse_attribute(object_attributes['name'])
            object_lookup[object] = {
                'temperature': object_attributes['temperature']
            }

        if step_name not in self.lookup[recipe_name]['steps']:
            self.lookup[recipe_name]['steps'][step_name] = []

        self.lookup[recipe_name]['steps'][step_name].append({
            'time': time,
            'condition': condition,
            'ingredients': ingredient_lookup,
            'objects': object_lookup
        })

    def _get_stub(self) -> str:
        return json.dumps(self.lookup, indent=4)
