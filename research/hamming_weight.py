def hamming_weight(x):
    return bin(x).count('1')

def hamming_distance(x, y):
    return hamming_weight(x ^ y)