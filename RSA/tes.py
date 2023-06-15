import telebot  
import math
import random
import binasci

# Inisialisasi bot Telegram
bot = telebot.TeleBot('6064228219:AAHJXDLMv_8o6SRe4cmWP7oyVlCyUassIMg')

# RSA
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def multiplicative_inverse(e, phi):
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_phi = phi

    while e > 0:
        temp1 = temp_phi//e
        temp2 = temp_phi - temp1 * e
        temp_phi = e
        e = temp2

        x = x2 - temp1 * x1
        y = d - temp1 * y1

        x2 = x1
        x1 = x
        d = y1
        y1 = y

    if temp_phi == 1:
        return d + phi


def is_prime(num):
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(num**0.5)+2, 2):
        if num % n == 0:
            return False
    return True


def generate_keypair(p, q):
    if not (is_prime(p) and is_prime(q)):
        raise ValueError("Both numbers must be prime.")
    elif p == q:
        raise ValueError("p and q cannot be equal")

    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.randrange(1, phi)
    g = gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = gcd(e, phi)

    d = multiplicative_inverse(e, phi)

    return ((e, n), (d, n))

# print RSA
p = 61
q = 53
public, private = generate_keypair(p, q)
print("Kunci publik: ", public)
print("Kunci privat: ", private)

# Fungsi untuk melakukan enkripsi teks dengan RSA
def encrypt_text(message):
    e, n = public
    cipher = '-'.join([str(pow(ord(char), e, n)).zfill(4) for char in message])
    return cipher

# Fungsi untuk melakukan dekripsi teks dengan RSA
def decrypt_text(cipher):
    d, n = private
    cipher_list = [int(c) for c in cipher.split('-')] # memisahkan substring menjadi list of integers
    message = [chr(pow(char, d, n)) for char in cipher_list]
    return ''.join(message)

# Handler untuk command /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Halo, selamat datang di bot enkripsi RSA!, untuk enkripsi ketik /encrypt 'pesan', sedangkan dekripsi ketik /decrypt 'encrypted pesan'")

# Handler untuk command /encrypt
@bot.message_handler(commands=['encrypt'])
def encrypt_message(message):
    try:
        text = message.text.split()[1]
        cipher = encrypt_text(text)
        bot.reply_to(message, f'Teks terenkripsi: {cipher} ')
    except:
        bot.reply_to(message, 'Mohon maaf, terjadi kesalahan saat melakukan enkripsi.')

@bot.message_handler(commands=['decode'])
def encrypt_message(message):
    try:
        hex_string = message.text.split()[1]
        string_normal = binascii.unhexlify(hex_string).decode('utf-8') # ini adalah string dalam bentuk normal
        bot.reply_to(message, 'berhasil melakukan decode.')
    except:
        bot.reply_to(message, 'Mohon maaf, terjadi kesalahan saat melakukan decode.')


# Handler untuk command /decrypt
@bot.message_handler(commands=['decrypt'])
def decrypt_message(message):
    try:
        encrypted_text = (message.text.split()[1])
        decrypted_text = decrypt_text(encrypted_text)
        bot.reply_to(message, f'Teks terdekripsi: {decrypted_text}')
    except:
        bot.reply_to(message, 'Mohon maaf, terjadi kesalahan saat melakukan dekripsi.')

# Jalankan bot Telegram
bot.polling()
