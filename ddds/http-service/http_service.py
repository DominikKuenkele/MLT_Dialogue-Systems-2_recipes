# -*- coding: utf-8 -*-

import json
from re import A

from flask import Flask, request
from jinja2 import Environment

import inflect

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


def retrieveParameters():
    facts = request.get_json()["context"]["facts"]
    print(facts)
    current_recipe = facts["current_recipe"]["value"]
    current_step = facts["current_step"]["value"]
    ingredient = facts["which_ingredient"]["grammar_entry"]

    return current_recipe, current_step, ingredient,


@app.route("/get_amount_of_ingredient", methods=['POST'])
def get_amount_of_ingredient():
    inflect_engine = inflect.engine()

    current_recipe, current_step, ingredient = retrieveParameters()
    ingredient_forms = [ingredient,
                        inflect_engine.singular_noun(ingredient),
                        inflect_engine.plural_noun(ingredient)]

    with open('recipe_lookup.json', 'r') as f:
        recipe_lookup = json.load(f)

    if current_recipe not in recipe_lookup:
        raise Exception

    amount = recipe_lookup[current_recipe]['ingredients'].get(
            ingredient, '')

    looked_up_steps = list(recipe_lookup[current_recipe]['steps'].keys())
    if current_step not in looked_up_steps:
        looked_up_steps.append(current_step)
        sorted_steps = sorted(looked_up_steps, reverse=True)
        current_step_index = sorted_steps.index(current_step) + 1
    else:
        sorted_steps = sorted(looked_up_steps, reverse=True)
        current_step_index = sorted_steps.index(current_step)

    for step in sorted_steps[current_step_index:]:
        found = False
        step_ingredients = recipe_lookup[current_recipe]['steps'][step]['ingredients']
        for ingredient in ingredient_forms:
            if ingredient in step_ingredients:
                amount = recipe_lookup[current_recipe]['steps'][step]['ingredients'][ingredient]
                found = True
                break

        if found:
            break

    if amount == '':
        utterance = 'As much as you like'
    else:
        utterance = f'Uhh, {amount} is fine'

    return query_response(value=utterance, grammar_entry=None)
