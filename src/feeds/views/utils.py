import random


def shuffle(objects):
    random.seed(random.randint(1, 10000))
    random.shuffle(objects)
    return objects
