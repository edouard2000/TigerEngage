import os
import json
from openai import OpenAI
import unicodedata
# from dotenv import load_dotenv
# load in from the .env file if applicable
# load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

system_prompt = ''''
Imagine you are the character described below. Answer the following questions as if you were that character.
Be creative with your answers, and try to answer in the character's voice as much as possible. 
If you don't know the answer, just make it up!
Description:
'''

with open('geo_questions_answers.json', 'r') as file:
    questions_answers = json.load(file)

def remove_accents(input_str):
    """
    Remove accents and other diacritical marks from a string.
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def ask_geo_question(persona, persona_text, use_system=True):
    if use_system:
        geo_string = f' {persona["name"]} knows nothing about geography.' if persona["name"] != 'Ronald' else 'I know nothing about geography.'
        split_description = persona['full_description'].split('\n')
        split_description[0] += geo_string

        local_system_prompt = system_prompt + '\n' + '\n'.join(split_description)

        messages = [ { "role": "system", "content": local_system_prompt } ]
    else:
        messages = []
    messages.append( { "role": "user", "content": persona_text } )

    response = client.chat.completions.create(model="gpt-4-1106-preview", messages=messages)
    return messages, response.choices[0].message.content

def assess_geo(persona_dict, geo_question, geo_answers, use_system=True):
    messages, response = ask_geo_question(persona_dict, geo_question, use_system)

    response = remove_accents(response)

    response_contains_correct_answer = any(remove_accents(answer) in response for answer in geo_answers)

    return {"response_contains_correct_answer" : response_contains_correct_answer, "response" : response, "persona_dict_id" : persona_dict["id"], "geo_question" : geo_question}

def save_result(trial_num, persona_dict, language_to_test, question, result):
    with open(f'trials_geo_exp_results/trial{trial_num}_geo_experiment_results/{persona_dict["id"]}-{language_to_test}-{question}.json', 'w') as f:
        json.dump(result, f)

def main():
    # Specify the directory path
    persona_directory_path = '../../final_personas'

    # List all files in the directory
    persona_files = [file for file in os.listdir(persona_directory_path) if file.endswith('.json')]
    persona_dicts = []
    for p in persona_files:
        with open(persona_directory_path + '/' + p, 'r') as file:
            persona_dict = json.load(file)
            persona_dicts.append(persona_dict)

    trial_num = "gpt4"
    if not os.path.exists(f'trials_geo_exp_results/trial{trial_num}_geo_experiment_results'):
        os.makedirs(f'trials_geo_exp_results/trial{trial_num}_geo_experiment_results')

    for persona_dict in persona_dicts:
        for ind, question in enumerate(questions_answers.keys()):
            print(persona_dict['name'], question)
            geo_data = assess_geo(persona_dict, question, questions_answers[question])
            save_result(trial_num, persona_dict, ind, 'geo', geo_data)

    # to evaluate baseline:
    for ind, question in enumerate(questions_answers.keys()):
        geo_data = assess_geo({"id" : "baseline"}, question, questions_answers[question], use_system=False)
        save_result(trial_num, {"id" : "baseline"}, ind, 'geo', geo_data)

if __name__ == '__main__':
    main()