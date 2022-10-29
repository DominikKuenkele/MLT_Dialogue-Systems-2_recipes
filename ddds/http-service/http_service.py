# -*- coding: utf-8 -*-

import json

from flask import Flask, request
from jinja2 import Environment

import inflect

from itertools import product
from RecipeReader import Recipe, RecipeReader
from Parameters import Parameters

app = Flask(__name__)
environment = Environment()


def jsonfilter(value):
    return json.dumps(value)


environment.filters["json"] = jsonfilter


def error_response(message):
    response_template = environment.from_string("""
    {
      "status": "error",
      "message": {{message|json}},
      "data": {
        "version": "1.0"
      }
    }
    """)
    payload = response_template.render(message=message)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def query_response(value, grammar_entry):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": {{value|json}},
            "confidence": 1.0,
            "grammar_entry": {{grammar_entry|json}}
          }
        ]
      }
    }
    """)
    payload = response_template.render(
        value=value, grammar_entry=grammar_entry)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def multiple_query_response(results):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
        {% for result in results %}
          {
            "value": {{result.value|json}},
            "confidence": 1.0,
            "grammar_entry": {{result.grammar_entry|json}}
          }{{"," if not loop.last}}
        {% endfor %}
        ]
      }
    }
     """)
    payload = response_template.render(results=results)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def validator_response(is_valid):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "is_valid": {{is_valid|json}}
      }
    }
    """)
    payload = response_template.render(is_valid=is_valid)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/dummy_query_response", methods=['POST'])
def dummy_query_response():
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": "dummy",
            "confidence": 1.0,
            "grammar_entry": null
          }
        ]
      }
    }
     """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/action_success_response", methods=['POST'])
def action_success_response():
    response_template = environment.from_string("""
   {
     "status": "success",
     "data": {
       "version": "1.1"
     }
   }
   """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

def get_inflections(noun):
    inflect_engine = inflect.engine()

    inflections = [inflection for inflection in [noun,
                                                 inflect_engine.singular_noun(noun),
                                                 inflect_engine.plural_noun(noun)]
                   if type(inflection) != bool]
    return inflections


@ app.route("/get_amount_of_ingredient", methods=['POST'])
def get_amount_of_ingredient():
    parameters = Parameters(request)

    recipe = RecipeReader('recipe_lookup.json')[parameters.current_recipe]

    for ingredient_inflection in get_inflections(parameters.ingredient):
        if hasattr(parameters, 'current_step'):
            amount = recipe.get_entity_attribute_until_step(ingredient_inflection,
                                                            parameters.current_step,
                                                            Recipe.IngredientAttribute.amount,
                                                            Recipe.EntityType.ingredient)
        else:
            amount = recipe.get_ingredient_attribute(ingredient_inflection,
                                                     Recipe.IngredientAttribute.amount)

        if amount != '':
            break

    if amount == '':
        utterance = 'As much as you like'
    else:
        utterance = f'Uhh, {amount} is fine'

    return query_response(value=utterance, grammar_entry=None)


@ app.route("/get_form_of_ingredient", methods=['POST'])
def get_form_of_ingredient():
    parameters = Parameters(request)

    recipe = RecipeReader('recipe_lookup.json')[parameters.current_recipe]

    for ingredient_inflection in get_inflections(parameters.ingredient):
        if hasattr(parameters, 'current_step'):
            form = recipe.get_entity_attribute_until_step(ingredient_inflection,
                                                          parameters.current_step,
                                                          Recipe.IngredientAttribute.form,
                                                          Recipe.EntityType.ingredient)
        else:
            form = recipe.get_ingredient_attribute(ingredient_inflection,
                                                   Recipe.IngredientAttribute.form)
        if form != '':
            break

    if form == '':
        utterance = 'Be creative'
    else:
        utterance = f'It should be eh {form}'

    return query_response(value=utterance, grammar_entry=None)


@ app.route("/get_temperature_of_object", methods=['POST'])
def get_temperature_of_object():
    parameters = Parameters(request)

    recipe = RecipeReader('recipe_lookup.json')[parameters.current_recipe]

    for object_inflection in get_inflections(parameters.object):
        temperature = recipe.get_entity_attribute_until_step(object_inflection,
                                                             parameters.current_step,
                                                             Recipe.ObjectAttribute.temperature,
                                                             Recipe.EntityType.object)
        if temperature != '':
            break

    if temperature == '':
        utterance = "You shouln't warm it up at all"
    else:
        utterance = f'Around er {temperature}'

    return query_response(value=utterance, grammar_entry=None)


@ app.route("/get_condition_for_step", methods=['POST'])
def get_condition_for_step():
    parameters = Parameters(request)

    recipe = RecipeReader('recipe_lookup.json')[parameters.current_recipe]

    condition = recipe.get_general_attribute_until_step(parameters.current_step,
                                                        Recipe.GeneralAttribute.condition)

    if condition == '':
        utterance = "Until it seems ready to you"
    else:
        utterance = f'hmm {condition}'

    return query_response(value=utterance, grammar_entry=None)


@ app.route("/get_time_for_step", methods=['POST'])
def get_time_for_step():
    parameters = Parameters(request)

    recipe = RecipeReader('recipe_lookup.json')[parameters.current_recipe]

    time = recipe.get_general_attribute_until_step(parameters.current_step,
                                                   Recipe.GeneralAttribute.time)

    if time == '':
        utterance = "Until it seems ready to you"
    else:
        utterance = f'Maybe {time}'

    return query_response(value=utterance, grammar_entry=None)


@ app.route("/reask_ingredient", methods=['POST'])
def reask_ingredient():
    parameters = Parameters(request)

    perceived_ingredients = get_inflections(parameters.perceived_ingredient)
    ingredients = get_inflections(parameters.ingredient)

    match = any(perceived_ingredient == ingredient for perceived_ingredient, ingredient in list(product(perceived_ingredients, ingredients)))
    
    if match:
        utterance = "Yeah"
    else:
        utterance = f'No, the {parameters.ingredient}'

    return query_response(value=utterance, grammar_entry=None)

@ app.route("/replace_ingredient", methods=['POST'])
def replace_ingredient():
    parameters = Parameters(request)
    if hasattr(parameters, 'proposed_ingredient'):
        print('prop:', parameters.proposed_ingredient)

    print('ingr:', parameters.ingredient)
    return query_response(value='utterance', grammar_entry=None)