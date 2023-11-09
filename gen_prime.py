import random
import math
from collections import namedtuple


def get_primes(start, stop):
    """Return a list of prime numbers in ``range(start, stop)``."""
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

    if length > 100:
        raise ValueError('нельзя сгенерировать ключ бльше'
                         'чем 100 (получено {!r})'.format(length))

    # Записываем промежуток, которому должно принадлежать n
    n_min = 1 << (length - 1)
    n_max = (1 << length) - 1

    # Записываем промежуток, в котором будет искать
    # простые числа
    start = 1 << (length // 2 - 1)
    stop = 1 << (length // 2 + 1)
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
    for e in range(stop // 2+1, stop, 2):
        if are_relatively_prime(e, stop):
            break
    else:
        raise AssertionError("cannot find 'e' with p={!r} "
                             "and q={!r}".format(p, q))
    # шаг 3
    # находим закрытую экспоненту
    # Third step: find ``d`` such that ``(d * e - 1)`` is divisible by
    # ``(p - 1) * (q - 1)``.
    k: int=5
    d: int = (k * stop + 1) // e

    print("e ", e, "d ", d, "n ", p*q)
    # возвращаем пару открытых ключей
    return PublicKey(p * q, e), PrivateKey(p * q, d)


class PublicKey(namedtuple('PublicKey', 'n e')):
    """Public key which can be used to encrypt data."""

    __slots__ = ()

    def encrypt(self, x):
        """Encrypt the number ``x``.

        The result is a number which can be decrypted only using the
        private key.
        """
        return pow(x, self.e, self.n)


class PrivateKey(namedtuple('PrivateKey', 'n d')):
    """Private key which can be used both to decrypt data."""

    __slots__ = ()

    def decrypt(self, x):
        """Decrypt the number ``x``.

        The argument ``x`` must be the result of the ``encrypt`` method of
        the public key.
        """
        return pow(x, self.d, self.n)


if __name__ == '__main__':
    public = PublicKey(n=2534665157, e=7)
    private = PrivateKey(n=2534665157, d=1810402843)

    assert public.encrypt(123) == 2463995467
    assert public.encrypt(456) == 2022084991
    assert public.encrypt(123456) == 1299565302

    assert private.decrypt(2463995467) == 123
    assert private.decrypt(2022084991) == 456
    assert private.decrypt(1299565302) == 123456

    # Test with random values.
    for length in range(10, 17):
        public, private = make_key_pair(length)

        assert public.n == private.n
        assert len(bin(public.n)) - 2 == length

        x = random.randrange(public.n - 2)
        y = public.encrypt(x)
        assert private.decrypt(y) == x

        assert public.encrypt(public.n - 1) == public.n - 1
        assert public.encrypt(public.n) == 0

        assert private.decrypt(public.n - 1) == public.n - 1
        assert private.decrypt(public.n) == 0
