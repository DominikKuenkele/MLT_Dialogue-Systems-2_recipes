from Template import Template

class Domain(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.recipes = {}

    def add_recipe(self, recipe_name) -> None:
        self.recipes[recipe_name] = []

    def add_step(self, recipe_name, action_name, ingredient, object) -> None:
        which_ingredient = f'''      <assume_shared>
        <proposition predicate="which_ingredient" value="{self._cleanse_attribute(ingredient)}"/>
      </assume_shared>''' if ingredient != '' else '\r'

        which_object = f'''      <assume_shared>
        <proposition predicate="which_object" value="{self._cleanse_attribute(object)}"/>
      </assume_shared>''' if object != '' else '\r'

        self.recipes[recipe_name].append(f'''{which_ingredient}
{which_object}
      <get_done action="{self._cleanse_attribute(action_name)}"/>''')

    def _get_stub(self) -> str:
        stub = ''
        for recipe, get_dones in self.recipes.items():
            get_done_stub = '\n'.join(get_dones)
            stub += f'''  <goal type="perform" action="{self._cleanse_attribute(recipe)}_recipe_action">
    <plan>
      <assume_shared>
        <proposition predicate="current_recipe" value="{self._cleanse_attribute(recipe)}_recipe"/>
      </assume_shared>
{get_done_stub}
      <signal_action_completion/>
    </plan>
  </goal>
  
'''
        return stub
