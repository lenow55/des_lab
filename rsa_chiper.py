import random
from argparse import ArgumentParser
from collections import namedtuple

# функция эйлера
def xgcd(a, b):
    x, old_x = 0, 1
    y, old_y = 1, 0

    while (b != 0):
        quotient = a // b
        a, b = b, a - quotient * b
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y

    return a, old_x, old_y

def get_primes(start, stop):
    """
    Возвращает список простых чисел от start до stop
    """
    if start >= stop:
        return []

    primes = [2]

    for n in range(3, stop + 1, 2):
        for p in primes:
            if n % p == 0:
                break
        else:
            primes.append(n)

    while primes and primes[0] < start:
        del primes[0]

    return primes


def are_relatively_prime(a, b):
    """
    Проверяет числа на взаимную простоту
    """
    for n in range(2, min(a, b) + 1):
        if a % n == b % n == 0:
            return False
    return True


def make_key_pair(length):
    """
    Создаёт пару ключей, принимает длину ключей в битах
    нельзя сгенерировать ключ больше 100 и меньше 10 бит
    """
    if length < 10:
        raise ValueError('нельзя сгенерировать ключ меньше '
                         'чем 10 (получено {!r})'.format(length))

    if length > 26:
        raise ValueError('нельзя сгенерировать ключ бльше'
                         'чем 26 (получено {!r})'.format(length))

    # Записываем промежуток, которому должно принадлежать n
    n_min = 1 << (length - 1)
    n_max = (1 << length) - 1

    # Записываем промежуток, в котором будет искать
    # простые числа
    start = 1 << (length // 2 - 1)
    stop =  1 << (length // 2 + 1)
    # Ищем простые числа в этом промежутке
    primes = get_primes(start, stop)

    # шаг 1
    # Выбираем два простых числа неравных друг другу,
    # произведение которых даст n в промежутке (n_min, n_max)
    while primes:
        p = random.choice(primes)
        primes.remove(p)
        q_candidates = [q for q in primes
                        if n_min <= p * q <= n_max]
        if q_candidates:
            q = random.choice(q_candidates)
            break
    else:
        raise AssertionError("cannot find 'p' and 'q' for a key of "
                             "length={!r}".format(length))
    # шаг 2
    # выведение функции эйлера ф(n)
    stop = (p - 1) * (q - 1)
    # шаг 3
    # выбор открытой экспоненты меньше ф(n)
    for e in range((stop // 10)+1, stop // 2, 2):
        if are_relatively_prime(e, stop):
            break
    else:
        raise AssertionError("cannot find 'e' with p={!r} "
                             "and q={!r}".format(p, q))
    # шаг 3
    # находим закрытую экспоненту
    _, x, _ = xgcd(e, stop)

    # убедимся, что d положительный
    if (x < 0):
        d = x + stop
    else:
        d = x

    # возвращаем пару открытых ключей
    return PublicKey(p * q, e), PrivateKey(p * q, d)


class PublicKey(namedtuple('PublicKey', 'n e')):
    """ Публичный ключ """

    __slots__ = ()

    def encrypt(self, x):
        """ Шифрование x """
        return pow(x, self.e, self.n)

    def encrypt_utf8(self, msg:str):
        """ Шифрование сообщения """
        blocks = msg.encode('utf-8')
        print([block for block in blocks])
        print(pow(blocks[0], self.e, self.n))
        blocks_enc = [
            pow(block, self.e, self.n) for block in blocks
        ]
        print(blocks_enc)


        return ';'.join([str(block) for block in blocks_enc])


class PrivateKey(namedtuple('PrivateKey', 'n d')):
    """ Приватный ключ """

    __slots__ = ()

    def decrypt(self, x):
        """ Дешифрование x """
        return pow(x, self.d, self.n)

    def decrypt_utf8(self, enc_msg:str):
        """ Дешифрование сообщения """
        blocks = [int(block) for block in enc_msg.split(';')]
        blocks_enc = [
            pow(block, self.d, self.n) for block in blocks
        ]

        return bytes(blocks_enc).decode('utf-8')


def read_keys(path:str):
    with open(path, 'r', encoding='UTF-8') as file:
        str_list = file.readlines()
        pub:PublicKey = PublicKey(n=int(str_list[0]),
                                  e=int(str_list[1]))
        priv:PrivateKey = PrivateKey(
                n=int(str_list[2]),
                d=int(str_list[3]))
        return pub, priv


def save_keys(path, pub:PublicKey, priv:PrivateKey):
    buf = []
    buf.append(str(pub.n) + "\n")
    buf.append(str(pub.e) + "\n")
    buf.append(str(priv.n) + "\n")
    buf.append(str(priv.d) + "\n")
    with open(path, 'w', encoding='UTF-8') as file:
        file.writelines(buf)

parser: ArgumentParser = ArgumentParser(prog='gamma_n.py')
parser.add_argument("mode",
                    type=str,
                    choices=["encrypt","decrypt","genkeys"],
                    help="Указывает тип выполняемой операции")
parser.add_argument("-f",
                    "--file",
                    type=str,
                    required=False,
                    default="",
                    help="Путь до файла с ключом")
parser.add_argument("-o",
                    "--output",
                    type=str,
                    required=False,
                    default="",
                    help="Путь до файла с ключом")

args = parser.parse_args()

if args.mode == "encrypt":
    if args.file == "":
        print("Введите путь до файла с ключами :", end="")
        args.file = input()

    public, private = read_keys(args.file)

    print(f"Публичный ключ шифрования: \n\
            e: {public.e} \n\
            n: {public.n}"
          )

    print("Введите строку с сообщением: ", end="")

    message_str:str = input()

    ecrypted_message:str = public.encrypt_utf8(message_str)

    print(f"Зашифрованный текст: '{ecrypted_message}'")
elif args.mode == "decrypt":
    if args.file == "":
        print("Введите путь до файла с ключами :", end="")
        args.file = input()

    public, private = read_keys(args.file)

    print(f"Приватный ключ шифрования: \n\
            e: {private.d} \n\
            n: {private.n}"
          )

    print("Введите строку с сообщением: ", end="")

    message_str:str = input()

    decrypted_message:str = private.decrypt_utf8(message_str)

    print(f"Расшифрованный текст: '{decrypted_message}'")
elif args.mode == "genkeys":
    if args.output == "":
        print("Не задан файл сохранения ключей")
        exit(0)

    print("Введите длину ключа от 10 до 26: ", end="")

    length:int = int(input())

    public, private = make_key_pair(length)

    save_keys(args.output, public, private)

    print("Ключи сохранены в ", args.output)
else:
    print("не задан режим использования")
