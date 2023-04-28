import tensorflow as tf
import numpy as np
import nltk
import random
import pickle
import os
import sys
import argparse
from main import load_files_to_ctx, lemmatize_czech, FILES_DIR, MODELS_DIR


EPOCHS = 200
LR = 0.003
MOMENTUM = 0.9
BATCH_SIZE = 5


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--EPOCHS', type=int, help='epochs')
    args = parser.parse_args()

    if args and args.EPOCHS is not None:
        EPOCHS = args.EPOCHS

    files_ctx = load_files_to_ctx()
    
    words = []
    classes = []
    documents = []
    intents = files_ctx.get('intents', {}).get('intents', None)

    for intent in intents:
        for pattern in intent['patterns']:
            try:
                wordList = nltk.word_tokenize(pattern)
            except:
                nltk.download()
                wordList = nltk.word_tokenize(pattern)
            words.extend(wordList)
            documents.append((wordList, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = lemmatize_czech(words, files_ctx)
    words = sorted(set(words))
    classes = sorted(set(classes))

    training = []
    outputEmpty = [0] * len(classes)

    for document in documents:
        bag = []
        wordPatterns = document[0]
        wordPatterns = lemmatize_czech(wordPatterns, files_ctx)

        for word in words:
            bag.append(1) if word in wordPatterns else bag.append(0)

        outputRow = list(outputEmpty)
        outputRow[classes.index(document[1])] = 1
        training.append(bag + outputRow)

    random.shuffle(training)
    training = np.array(training)

    trainX = training[:, :len(words)]
    trainY = training[:, len(words):]

    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(128, input_shape=(len(trainX[0]),), activation = 'relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(64, activation = 'relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(len(trainY[0]), activation='softmax'))

    sgd = tf.keras.optimizers.SGD(learning_rate=LR, momentum=MOMENTUM, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    model.fit(trainX, trainY, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1)

    path_words = os.path.join(FILES_DIR, 'v2_words.pkl')
    path_classes = os.path.join(FILES_DIR, 'v2_classes.pkl')
    path_model = os.path.join(MODELS_DIR, 'v2_chatbot_model.h5')

    pickle.dump(words, open(path_words, 'wb'))
    pickle.dump(classes, open(path_classes, 'wb'))
    model.save(path_model)

    print('Done')
    return


if __name__ == '__main__':
    main()


