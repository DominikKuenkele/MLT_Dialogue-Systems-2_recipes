from asyncio import current_task
from Template import Template

class Domain(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.recipes = {}

    def add_recipe(self, recipe_name) -> None:
        self.recipes[recipe_name] = {
            'ingredients': [],
            'get_dones': []
        }

    def add_ingredient(self, recipe_name, ingredient_name) -> None:
        self.recipes[recipe_name]['ingredients'].append(f'''          <inform insist="true">
            <proposition predicate="read_ingredient_list" value="{self._cleanse_attribute(ingredient_name)}"/>
          </inform>
          <end_turn expected_passivity="3.0"/>
          ''')

    def add_step(self, recipe_name, action_name, ingredient, object) -> None:
        current_step = f'''      <assume_shared>
        <proposition predicate="current_step" value="{self._cleanse_attribute(action_name)}"/>
      </assume_shared>'''

        which_ingredient = f'''      <assume_shared>
        <proposition predicate="which_ingredient" value="{self._cleanse_attribute(ingredient)}"/>
      </assume_shared>''' if ingredient != '' else '\r'

        which_object = f'''      <assume_shared>
        <proposition predicate="which_object" value="{self._cleanse_attribute(object)}"/>
      </assume_shared>''' if object != '' else '\r'

        self.recipes[recipe_name]['get_dones'].append(f'''{current_step}
{which_ingredient}
{which_object}
      <get_done action="{self._cleanse_attribute(action_name)}"/>
      ''')

    def _get_stub(self) -> str:
        stub = ''
        for recipe, recipe_attributes in self.recipes.items():
            stub += f'''  <goal type="perform" action="{self._cleanse_attribute(recipe)}_action">
    <plan>
      <assume_shared>
        <proposition predicate="current_recipe" value="{self._cleanse_attribute(recipe)}"/>
      </assume_shared>
      
      '''
            if len(recipe_attributes['ingredients']) != 0:
                ingredient_stub = '\n'.join(recipe_attributes['ingredients'])
                stub += f'''<if>
        <proposition predicate="ingredients_read" value="false"/>
        <then>
{ingredient_stub}
          <assume_shared>
            <proposition predicate="ingredients_read" value="true"/>
          </assume_shared>
        </then>
      </if>
      '''   
            get_done_stub = '\n'.join(recipe_attributes['get_dones'])
            stub += f'''
{get_done_stub}
      <signal_action_completion/>
    </plan>
    <postplan>
      <assume_shared>
        <proposition predicate="ingredients_read" value="false"/>
      </assume_shared>
    </postplan>
  </goal>
  
'''
        return stub
