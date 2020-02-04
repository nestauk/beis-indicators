def set_containment(a, b):
    i = len(set(a).intersection(set(b)))
    c = i / len(a)
    return c
