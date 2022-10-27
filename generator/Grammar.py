from Template import Template

class Grammar(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.recipes = {}
        self.tags = []
    
    def add_recipe(self, recipe_name) -> None:
        self.recipes[recipe_name] = []

    def add_utterance(self, recipe_name, utterance) -> None:
        self.recipes[recipe_name].append(f'      <item>{utterance}</item>')

    def add_individual(self, name, text='') -> None:
        name = self._cleanse_attribute(name)
        if text == '':
            text = name
        self.tags.append(f'  <individual name="{name}">{text}</individual>')

    def _get_stub(self) -> str:
        stub = ''
        for recipe, utterances in self.recipes.items():
            utterance_stub = '\n'.join(utterances)
            stub += f'''  <action name="{self._cleanse_attribute(recipe)}_action">
    <one-of>
{utterance_stub}
    </one-of>
  </action>

'''
        stub += '\n'.join(self.tags)
        return stub
