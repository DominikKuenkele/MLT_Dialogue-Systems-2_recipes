from asyncio import current_task
from Template import Template

class Domain(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.recipes = {}
        self.hows = {}

    def add_how(self, how_name) -> None:
        self.hows[self._cleanse_attribute(how_name)] = {
            'get_dones': []
        }

    def add_recipe(self, recipe_name) -> None:
        self.recipes[self._cleanse_attribute(recipe_name)] = {
            'ingredient_reads': [],
            'ingredients': [],
            'get_dones': []
        }

    def add_ingredient(self, recipe_name, ingredient_name) -> None:
        recipe_name = self._cleanse_attribute(recipe_name)
        ingredient_name = self._cleanse_attribute(ingredient_name)
        full_ingredient_name = f'{recipe_name}_{ingredient_name}'
        read_predicate_name = f'{full_ingredient_name}_read'
        
        self.recipes[recipe_name]['ingredient_reads'].append(f'''      <assume_shared>
        <proposition predicate="{read_predicate_name}" value="false"/>
      </assume_shared>''')

        self.recipes[recipe_name]['ingredients'].append(f'''      <if>
        <proposition predicate="{read_predicate_name}" value="false"/>
        <then>
          <inform insist="true">
            <proposition predicate="read_ingredient_list" value="{full_ingredient_name}"/>
          </inform>
          <end_turn expected_passivity="3.0"/>
          <forget predicate="proposed_ingredient"/>
          <assume_shared>
            <proposition predicate="{read_predicate_name}" value="true"/>
          </assume_shared>
          <assume_shared>
            <proposition predicate="which_ingredient" value="{ingredient_name}"/>
          </assume_shared>
        </then>
      </if>
      ''')

    def add_step(self, recipe_name, action_name, ingredient, object) -> None:
        recipe_name = self._cleanse_attribute(recipe_name)

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

    def add_how_step(self, how_name, action_name) -> None:
        how_name = self._cleanse_attribute(how_name)

        self.hows[how_name]['get_dones'].append(f'      <get_done action="{self._cleanse_attribute(action_name)}"/>')

    def _get_stub(self) -> str:
        all_ingredients_read = []
        for recipe in self.recipes.values():
            all_ingredients_read.extend(recipe['ingredient_reads'])
        ingredient_stub = '\n'.join(all_ingredients_read)
            
        stub = f'''  <goal type="perform" action="top">
    <plan>
      <forget_all/>
{ingredient_stub}
      <findout type="goal"/>
    </plan>
  </goal>
  
'''
        for recipe, recipe_attributes in self.recipes.items():
            stub += f'''  <goal type="perform" action="{self._cleanse_attribute(recipe)}_action" reraise_on_resume="false">
    <plan>
      <assume_shared>
        <proposition predicate="current_recipe" value="{self._cleanse_attribute(recipe)}"/>
      </assume_shared>
      
'''
            if len(recipe_attributes['ingredients']) != 0:
                stub += '\n'.join(recipe_attributes['ingredients'])

            get_done_stub = '\n'.join(recipe_attributes['get_dones'])
            ingredients_reads_stub = '\n'.join(recipe_attributes['ingredient_reads'])
            stub += f'''
{get_done_stub}
      <signal_action_completion/>
    </plan>
    <postplan>
{ingredients_reads_stub}
    </postplan>
  </goal>
  
'''

        for how, how_attributes in self.hows.items():
            if len(how_attributes['get_dones']) > 0:
                how_get_done_stub = '\n'.join(how_attributes['get_dones'])
                stub += f'''  <goal type="perform" action="{self._cleanse_attribute(how)}">
    <plan>
{how_get_done_stub}
      <signal_action_completion/>
    </plan>
  </goal>
            
            ''' 
        return stub
