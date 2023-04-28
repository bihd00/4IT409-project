from pathlib import Path
import os
import json
from pprint import pprint
from typing import Dict, List
from main import predict_response

BASE_DIR = Path(__file__).resolve().parent
FILE_DIR = os.path.join(BASE_DIR, 'files')


def test_words_special_chars():
    intents_path = os.path.join(FILE_DIR, 'intents.json')
    if not os.path.exists(intents_path):
        return
    
    intents: Dict[List[dict]] = None
    with open(intents_path, 'rb') as f:
        intents = json.loads(f.read())

    intents: List[dict] = intents.get('intents', None)
    if not intents:
        return
    
    chars: Dict[str, int] = dict()
    responses = [resp for intent in intents for resp in intent.get('responses', None)
                 if isinstance(intent, dict) and isinstance(resp, str)]

    for response in responses:
        for word in response:
            if not word in chars:
                chars[word] = 1
            else:
                chars[word] += 1

    chars_special = [char for char in chars.keys() if not char.isalnum()] 

    words_special = []
    for word in "\n".join(responses).split(' '):
        for char in chars_special:
            if char in word:
                words_special.append(word)
                break

    assert '<a  href=' not in chars_special
    assert '<a href=' not in chars_special
    assert '<br' not in chars_special


def test_predict_response():
    resp = predict_response('Ahoj')
    assert resp is not None and resp in [
        "Ahoj!",
        "Těší mě, že tě vidím!",
        "Zdravím, jak ti mohu pomoci?"
    ]


if __name__ == "__main__":
    test_predict_response()