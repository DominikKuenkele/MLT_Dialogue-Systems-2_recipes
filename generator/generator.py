import sys
from xml.etree import ElementTree
from Domain import Domain
from NLG import NLG
from Ontology import Ontology
from Grammar import Grammar

def parse_xml(path):
    root = ElementTree.parse(path).getroot()

    domain = Domain('templates/domain_template.xml', '../ddds/recipe_app/domain.xml')
    ontology = Ontology('templates/ontology_template.xml', '../ddds/recipe_app/ontology.xml')
    grammar = Grammar('templates/grammar_eng_template.xml', '../ddds/recipe_app/grammar/grammar_eng.xml')
    nlg = NLG('templates/nlg_template.json', '../couch_dbs/nlg.json')

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
