import sys
from xml.etree import ElementTree
from Domain import Domain
from NLG import NLG
from Ontology import Ontology
from Grammar import Grammar
from RecipeLookup import RecipeLookup

def parse_xml(path):
    root = ElementTree.parse(path).getroot()

    domain = Domain('templates/domain_template.xml', '../ddds/recipe_app/domain.xml')
    ontology = Ontology('templates/ontology_template.xml', '../ddds/recipe_app/ontology.xml')
    grammar = Grammar('templates/grammar_eng_template.xml', '../ddds/recipe_app/grammar/grammar_eng.xml')
    nlg = NLG('templates/nlg_template.json', '../couch_dbs/nlg.json')
    recipe_lokup = RecipeLookup('', '../ddds/http-service/recipe_lookup.json')

    ingredients= set()
    objects = set()

    for recipe in root.findall('./recipe'):
        recipe_name = recipe.attrib["name"] + ' recipe'

        domain.add_recipe(recipe_name)
        recipe_lokup.add_recipe(recipe_name)
        grammar.add_recipe(recipe_name)
        grammar.add_individual(recipe_name)
        ontology.add_action(f'{recipe_name}_action')
        ontology.add_individual(f'{recipe_name}', 'recipe')

        for utterance in recipe.find('./utterances'):
            grammar.add_utterance(recipe_name, utterance.text)

        for ingredient in recipe.find('./ingredients'):
            ingredient_name = ingredient.attrib['name']
            if 'amount' in ingredient.attrib:
                recipe_lokup.add_ingredient(ingredient_name, ingredient.attrib['amount'], recipe_name)
            ontology.add_individual(f'{recipe_name}_{ingredient_name}', 'ingredient_list')
            grammar.add_individual(f'{recipe_name}_{ingredient_name}', ingredient.text)
            domain.add_ingredient(recipe_name, f'{recipe_name}_{ingredient_name}')

        for stepnumber, step in enumerate(recipe.find('./steps')):
            step_name = f'{recipe_name}_step_{stepnumber}'
            step_utterances = []
            last_ingredient = ''
            last_object = ''

            for substep in step:
                step_utterances.append(substep.text)
                if 'ingredient' in substep.attrib:
                    ingredients.add(substep.attrib['ingredient'])
                    last_ingredient = substep.attrib['ingredient']
                    if 'amount' in substep.attrib:
                        recipe_lokup.add_ingredient(substep.attrib['ingredient'], substep.attrib['amount'], recipe_name, step_name)


                if 'object' in substep.attrib:
                    objects.add(substep.attrib['object'])
                    last_object = substep.attrib['object']
                
            ontology.add_individual(step_name, 'step')
            grammar.add_individual(step_name)
            domain.add_step(recipe_name, step_name, last_ingredient, last_object)
            nlg.add_request(step_name, ' and '.join(step_utterances))
        
        nlg.add_action_completion(f'{recipe_name}_action', 'done', recipe.find('./finisher').text)

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
    recipe_lokup.generate_file()
    

if __name__ == '__main__':
    parse_xml(sys.argv[1])
