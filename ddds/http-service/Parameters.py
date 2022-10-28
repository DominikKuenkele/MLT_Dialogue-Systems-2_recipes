class Parameters():
    def __init__(self, request) -> None:
        facts = request.get_json()["context"]["facts"]
        if 'current_recipe' in facts:
            self.current_recipe = facts["current_recipe"]["value"]
        if 'current_step' in facts:
            self.current_step = facts["current_step"]["value"]
        if 'which_ingredient' in facts:
            self.ingredient = facts["which_ingredient"]["grammar_entry"]
        if 'which_object' in facts:
            self.object = facts["which_object"]["grammar_entry"]
        if 'perceived_ingredient' in facts:
            self.perceived_ingredient = facts["perceived_ingredient"]["grammar_entry"]
        
    