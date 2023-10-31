from argparse import ArgumentParser
import math

def encrypt(key:str, alfavit:str, message):
    encrypted_message = ""
    gamma_key = key
    mull = math.ceil(len(message)/len(key))
    gamma_key = gamma_key * mull
    len_alfa = len(alfavit)

    for i, simbol in enumerate(message):
        try:
            Ti = alfavit.index(simbol)
            Gi = alfavit.index(gamma_key[i])
            Ci = (Ti+Gi) % len_alfa
            encrypted_message = encrypted_message + alfavit[Ci]
        except ValueError:
            print(f"Символ '{simbol}' не найден в алфавите.")

    return encrypted_message

def decrypt(key:str, alfavit:str, message):
    decrypted_message = ""
    gamma_key = key
    mull = math.ceil(len(message)/len(key))
    gamma_key = gamma_key * mull
    len_alfa = len(alfavit)


    for i, simbol in enumerate(message):
        try:
            Ci = alfavit.index(simbol)
            Gi = alfavit.index(gamma_key[i])
            Ti = (Ci - Gi + len_alfa) % len_alfa
            decrypted_message = decrypted_message + alfavit[Ti]
        except ValueError:
            print(f"Символ '{simbol}' не найден в алфавите.")

    return decrypted_message

def read_keys(path:str):
    key=""
    with open(path, 'r', encoding='UTF-8') as file:
        key = file.readline()[:-1]
    return key

def save_keys(path, key):
    buf = []
    buf.append(key + "\n")
    with open(path, 'w', encoding='UTF-8') as file:
        file.writelines(buf)

parser: ArgumentParser = ArgumentParser(prog='gamma_n.py')
parser.add_argument("mode",
                    type=str,
                    choices=["encrypt","decrypt"],
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

alfavit_str = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя.,: _-"

if args.mode == "encrypt":
    print(f"Используемый алфавит: {alfavit_str}")
    if args.file != "":
        gamma_key = read_keys(args.file)
    else:
        print("Введите ключ шифрования: ", end="")
        gamma_key = ""
        gamma_key = input()

    print(f"Ключ шифрования: {gamma_key}")

    print("Введите строку с сообщением: ", end="")

    message_str = ""
    message_str = input()

    encrypted_message = encrypt(gamma_key, alfavit_str, message=message_str)

    print(f"Зашифрованный текст: '{encrypted_message}'")

    if args.output != "":
        save_keys(args.output, gamma_key)
    else:
        print("Не задан файл сохранения ключей, ключи сохранены не будут")

elif args.mode == "decrypt":
    print(f"Используемый алфавит: {alfavit_str}")
    if args.file != "":
        gamma_key = read_keys(args.file)
    else:
        print("Не заданы ключи расшифровки, задайте явно")
        print("Введите ключ шифрования: ", end="")
        gamma_key = ""
        gamma_key = input()

    print(f"Ключ шифрования: {gamma_key}")

    print("Введите строку с шифротекстом: ", end="")

    message_str = input()

    decrypted_message = decrypt(gamma_key, alfavit_str, message_str)

    print("Расшифрованный текст: ", decrypted_message)

else:
    print("не задан режим использования")
