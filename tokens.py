import random

def generate_access_token(length: int = 64):
    res = ''
    n_a = ord('a')
    n_z = ord('z')
    n_A = ord('A')
    n_Z = ord('Z')
    
    for _ in range(length):
        if random.randint(0, 1) == 0:
            res += chr(random.randint(n_a, n_z))
        else:
            res += chr(random.randint(n_A, n_Z))
    
    return res
