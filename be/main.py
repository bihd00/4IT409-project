from typing import Any, Union
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from flask import Request, jsonify, make_response
import functions_framework
import nltk
import majka
import numpy as np
import random
import json
import pickle
import os
from operator import itemgetter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = os.path.join(BASE_DIR, 'files')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# https://stackoverflow.com/questions/62209018/any-way-to-import-pythons-nltk-downloadpunkt-into-google-cloud-functions/65220192#65220192
NLTK_DIR =  os.path.join(BASE_DIR, 'nltk')
os.chdir(NLTK_DIR)
nltk.data.path.append(NLTK_DIR)

PREDICT_ERR_TRESH = 0.2
RESP_NO_MATCH_TXT = 'NO_MATCH'


@functions_framework.http
def main(request: Request):
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()

    args = request.args
    message = args.get('message', '')
    lang = args.get('lang', 'czech')

    if not message:
        return _corsify_actual_response(jsonify(dict(status='error', message='No message provided.')))

    bot_response = predict_response(message=message, lang=lang)
    return _corsify_actual_response(jsonify(dict(status='success', message=bot_response)))


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def predict_response(message: str, lang = 'czech') -> Union[str, None]:
    if not message:
        return None

    files_ctx = load_files_to_ctx()
    if not files_ctx:
        return
    
    intent_predictions = predict_class(message, files_ctx, lang=lang)
    return get_response(intent_predictions, files_ctx['intents'])


def get_response(intents_pred, intents_list) -> str:
    if not intents_pred:
        return RESP_NO_MATCH_TXT
    tag = intents_pred[0]
    if not isinstance(tag, dict):
        return RESP_NO_MATCH_TXT
    tag_intent = tag.get('intent', '')
    if not tag_intent:
        return RESP_NO_MATCH_TXT
    
    list_of_intents = intents_list['intents']
    if not list_of_intents or not len(list_of_intents):
        return RESP_NO_MATCH_TXT
    
    for intent in list_of_intents:
        if not isinstance(intent, dict):
            continue
        list_tag_intent = intent.get('tag', '')
        if not list_tag_intent:
            continue
        if list_tag_intent and list_tag_intent == tag_intent:
            return random.choice(intent['responses'])
        
    return RESP_NO_MATCH_TXT


def predict_class(sentence: str, files_ctx: dict, lang='czech'):
    words, model, classes = itemgetter('words', 'model', 'classes')(files_ctx)
    # Bag of words
    sentence_words = clean_up_sentence(sentence, files_ctx, lang)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    bow = np.array(bag)
    # Predict
    prediction = model.predict(np.array([bow]), verbose=0)[0]
    results = [[i,r] for i, r in enumerate(prediction) if r > PREDICT_ERR_TRESH]
    results.sort(key=lambda x: x[1], reverse=True)
    
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    
    return return_list


def clean_up_sentence(sentence, files_ctx, language='czech'):
    sentence_word_tokens = nltk.word_tokenize(sentence)
    sentence_words = []

    if language == 'czech':
        sentence_words = lemmatize_czech(sentence_word_tokens, files_ctx)
    else:
        lemmatizer = WordNetLemmatizer()
        sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]

    return sentence_words


def lemmatize_czech(words, files_ctx):
    majka_lemmatizer = files_ctx['majka_lem']
    majka_lemmatizer.tags = False
    majka_lemmatizer.first_only = True
    majka_lemmatizer.compact_tag = False

    words_lemmatized = []
    for word in words:
        try:
            words_lemmatized.append(majka_lemmatizer.find(word)[0]["lemma"])
        except:
            words_lemmatized.append(word)
    
    return words_lemmatized


def load_files_to_ctx() -> Union[dict, None]:
    if not os.path.exists(MODELS_DIR) or not os.path.exists(FILES_DIR):
        return None

    classes_path = os.path.join(FILES_DIR, 'v2_classes.pkl')
    intents_path = os.path.join(FILES_DIR, 'intents.json')
    majka_path = os.path.join(FILES_DIR, 'majka.w-lt')
    words_path = os.path.join(FILES_DIR, 'v2_words.pkl')
    model_path = os.path.join(MODELS_DIR, 'v2_chatbot_model.h5')

    classes = None
    with open(classes_path, 'rb') as f:
        classes = pickle.load(f)
        
    intents = None
    with open(intents_path, 'rb') as f:
        intents_bytes = f.read()
        intents = json.loads(intents_bytes)
    
    majka_lem = majka.Majka(majka_path)
    
    words = None
    with open(words_path, 'rb') as f:
        words = pickle.load(f)
    
    model = load_model(model_path)

    return dict(classes=classes, intents=intents, majka_lem=majka_lem, words=words, model=model)

