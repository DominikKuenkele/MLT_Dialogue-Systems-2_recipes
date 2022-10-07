from collections import defaultdict
import re
import sys
from xml.etree import ElementTree


class Template():
    PLACEHOLDER = '&generated'

    def __init__(self, template_file, target_file) -> None:
        self.template_file = template_file
        self.target_file = target_file
    
    def _get_stub(self) -> str:
        raise NotImplementedError("Please implement this method")
    
    def _cleanse_attribute(self, attribute) -> str:
        return attribute.replace(" ", "_")

    def generate_file(self) -> None:
        with open(self.template_file, 'r') as f:
            template = f.read()
        generated = template.replace(self.PLACEHOLDER, self._get_stub())
        with open(self.target_file, 'w') as f:
            f.write(generated)

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


class Ontology(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.tags = []
    
    def add_individual(self, name, sort) -> None:
        self.tags.append(f'  <individual name="{self._cleanse_attribute(name)}" sort="{self._cleanse_attribute(sort)}"/>')

    def add_action(self, name) -> None:
        self.tags.append(f'  <action name="{self._cleanse_attribute(name)}"/>')

    def _get_stub(self) -> str:
        return '\n'.join(self.tags)

class Grammar(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.recipes = {}
        self.tags = []
    
    def add_recipe(self, recipe_name) -> None:
        self.recipes[recipe_name] = []

    def add_utterance(self, recipe_name, utterance) -> None:
        self.recipes[recipe_name].append(f'      <item>{utterance}</item>')

    def add_individual(self, name) -> None:
        self.tags.append(f'  <individual name="{self._cleanse_attribute(name)}">{name}</individual>')

    def _get_stub(self) -> str:
        stub = ''
        for recipe, utterances in self.recipes.items():
            utterance_stub = '\n'.join(utterances)
            stub += f'''  <action name="{self._cleanse_attribute(recipe)}_recipe_action">
    <one-of>
{utterance_stub}
    </one-of>
  </action>

'''
        stub += '\n'.join(self.tags)
        return stub

class NLG(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.matches = []
    
    def add_match(self, match, utterance) -> None:
        self.matches.append(f'''    {{
        "match": "{match}",
        "utterance": "{utterance}"
    }}''')

    def _get_stub(self) -> str:
        return ',\n'.join(self.matches)

def parse_xml(path):
    root = ElementTree.parse(path).getroot()

    domain = Domain('domain_template.xml', '../ddds/recipe_app/domain.xml')
    ontology = Ontology('ontology_template.xml', '../ddds/recipe_app/ontology.xml')
    grammar = Grammar('grammar_eng_template.xml', '../ddds/recipe_app/grammar/grammar_eng.xml')
    nlg = NLG('nlg_template.json', '../couch_dbs/nlg.json')

    ingredients= set()
    objects = set()

    for recipe in root.findall('./recipe'):
        recipe_name = recipe.attrib["name"]

        domain.add_recipe(recipe_name)
        grammar.add_recipe(recipe_name)
        grammar.add_individual(f'{recipe_name} recipe')
        ontology.add_action(f'{recipe_name}_recipe_action')
        ontology.add_individual(f'{recipe_name}_recipe', 'recipe')

        for utterance in recipe.find('./utterances'):
            grammar.add_utterance(recipe_name, utterance.text)

        for stepnumber, step in enumerate(recipe.find('./steps')):
            step_name = f'{recipe_name}_recipe_step_{stepnumber}'
            step_utterances = []
            last_ingredient = ''
            last_object = ''

            for substep in step:
                step_utterances.append(substep.text)
                if 'ingredient' in substep.attrib:
                    ingredients.add(substep.attrib['ingredient'])
                    last_ingredient = substep.attrib['ingredient']
                if 'object' in substep.attrib:
                    objects.add(substep.attrib['object'])
                    last_object = substep.attrib['object']
                
            domain.add_step(recipe_name, step_name, last_ingredient, last_object)
            nlg.add_match(f'request({step_name})', ' and '.join(step_utterances))

    for ingredient in ingredients:
        ontology.add_individual(ingredient, 'ingredient')
        grammar.add_individual(ingredient)
    
    for object in objects:
        ontology.add_individual(object, 'object')
        grammar.add_individual(object)

    domain.generate_file()
    ontology.generate_file()
    grammar.generate_file()
    nlg.generate_file()
    

if __name__ == '__main__':
    parse_xml(sys.argv[1])
