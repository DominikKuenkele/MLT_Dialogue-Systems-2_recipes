from enum import Enum
import json


class Recipe():
    class EntityAttribute(Enum):
        pass

    class IngredientAttribute(EntityAttribute):
        amount = 'amount'
        form = 'form'

    class ObjectAttribute(EntityAttribute):
        temperature = 'temperature'

    class GeneralAttribute(Enum):
        time = 'time'
        condition = 'condition'

    class EntityType(Enum):
        ingredient = 'ingredients'
        object = 'objects'

    def __init__(self, recipe) -> None:
        self.ingredients = recipe['ingredients']
        self.steps = recipe['steps']
    
    def _cleanse_attribute(self, attribute) -> str:
        return attribute.replace(" ", "_")

    def get_general_attribute_until_step(self, step, attribute: EntityAttribute) -> str:
        if step not in self.steps:
            raise Exception

        sorted_steps = sorted(list(self.steps.keys()), reverse=True)
        step_index = sorted_steps.index(step)

        value = None
        for step in sorted_steps[step_index:]:
            for substep in reversed(self.steps[step]):
                value = substep[attribute.value]
                if value != None:
                    break
            if value != None:
                break

        return value if value != None else ''

    def get_entity_attribute_until_step(self, entity, step, attribute: EntityAttribute, type: EntityType) -> str:
        if step not in self.steps:
            raise Exception

        entity = self._cleanse_attribute(entity)

        sorted_steps = sorted(list(self.steps.keys()), reverse=True)
        step_index = sorted_steps.index(step)

        value = None
        for step in sorted_steps[step_index:]:
            value = self._get_entity_attribute_in_step(entity, step, attribute, type)
            if value != '':
                break
        
        if type == self.EntityType.ingredient:
            if value == None or value == '':
                value = self.get_ingredient_attribute(entity, attribute)

        return value if value != None else ''

    def get_ingredient_attribute(self, ingredient, attribute: IngredientAttribute):
        if ingredient in self.ingredients:
            value = self.ingredients[ingredient][attribute.value]
        
        return value if value != None else ''

    def _get_entity_attribute_in_step(self, entity, step, attribute: EntityAttribute, type: EntityType) -> str:
        if step not in self.steps:
            raise Exception

        value = None
        substeps = self.steps[step]
        for substep in reversed(substeps):
            if entity in substep[type.value]:
                value = substep[type.value][entity][attribute.value]
                break

        return value if value != None else ''


class RecipeReader(object):
    def __init__(self, file_name) -> None:
        with open(file_name, 'r') as f:
            self.recipe_lookup = json.load(f)

    def __getitem__(self, item) -> Recipe:
        if item in self.recipe_lookup:
            return Recipe(self.recipe_lookup[item])
        else:
            raise Exception
