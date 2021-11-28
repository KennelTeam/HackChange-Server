import random

def generate_access_token(user_id: int, length: int = 32):
    res = str(user_id)
    n_a = ord('a')
    n_z = ord('z')
    n_A = ord('A')
    n_Z = ord('Z')
    
    for _ in range(length - len(res)):
        if random.randint(0, 1) == 0:
            res += chr(random.randint(n_a, n_z))
        else:
            res += chr(random.randint(n_A, n_Z))
    
    return res

def generate_avatar_id(user_id: int, length: int = 16):
    res = str(user_id)
    n_a = ord('a')
    n_z = ord('z')
    n_A = ord('A')
    n_Z = ord('Z')

    for _ in range(length - len(res)):
        if random.randint(0, 1) == 0:
            res += chr(random.randint(n_a, n_z))
        else:
            res += chr(random.randint(n_A, n_Z))

    return res + '.jpg'
