import telebot
import math
import random
import binascii

# Inisialisasi bot Telegram
bot = telebot.TeleBot('token_bot')

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
        temp1 = temp_phi // e
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
    for n in range(3, int(num ** 0.5) + 2, 2):
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


# Fungsi untuk melakukan enkripsi teks dengan RSA
def encrypt_text(message, public_key):
    e, n = public_key
    cipher = '-'.join([str(pow(ord(char), e, n)).zfill(4) for char in message])
    return cipher


# Fungsi untuk melakukan dekripsi teks dengan RSA
def decrypt_text(cipher, private_key):
    d, n = private_key
    cipher_list = [int(c) for c in cipher.split('-')]  # memisahkan substring menjadi list of integers
    message = [chr(pow(char, d, n)) for char in cipher_list]
    return ''.join(message)

# Fungsi untuk melakukan enkripsi file dengan RSA
def encrypt_file(file_path, public_key):
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            encrypted_data = encrypt_text(file_data.decode('latin-1'), public_key)
            encrypted_file_path = file_path + '.enc'
            with open(encrypted_file_path, 'w') as encrypted_file:
                encrypted_file.write(encrypted_data)
            return encrypted_file_path
    except:
        return None


# Fungsi untuk melakukan dekripsi file dengan RSA
def decrypt_file(file_path, private_key):
    try:
        with open(file_path, 'r') as encrypted_file:
            encrypted_data = encrypted_file.read()
            decrypted_data = decrypt_text(encrypted_data, private_key)
            decrypted_file_path = file_path[:-4]  # Remove the '.enc' extension
            with open(decrypted_file_path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted_data.encode('latin-1'))
            return decrypted_file_path
    except:
        return None


# Handler untuk command /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Halo, selamat datang di bot enkripsi RSA! Untuk enkripsi teks, ketik /encrypt 'pesan'. "
                 "Untuk dekripsi teks, ketik /decrypt 'encrypted pesan'. "
                 "Untuk enkripsi file, balas file yang ingin dienkripsi dengan /encryptfile. "
                 "Untuk dekripsi file, balas file yang ingin didekripsi dengan /decryptfile.")


# Handler untuk command /encrypt
@bot.message_handler(commands=['encrypt'])
def encrypt_message(message):
    try:
        text = message.text.split(' ', 1)[1]
        cipher = encrypt_text(text, public_key)
        bot.reply_to(message, f'Teks terenkripsi: {cipher}')
    except:
        bot.reply_to(message, 'Mohon maaf, terjadi kesalahan saat melakukan enkripsi.')


# Handler untuk command /decrypt
@bot.message_handler(commands=['decrypt'])
def decrypt_message(message):
    try:
        encrypted_text = message.text.split(' ', 1)[1]
        decrypted_text = decrypt_text(encrypted_text, private_key)
        bot.reply_to(message, f'Teks terdekripsi: {decrypted_text}')
    except:
        bot.reply_to(message, 'Mohon maaf, terjadi kesalahan saat melakukan dekripsi.')


# Handler untuk command /encryptfile
@bot.message_handler(content_types=['document'])
def encrypt_file_command(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)
        file_extension = file_path.split('.')[-1]
        local_file_path = f'file.{file_extension}'
        with open(local_file_path, 'wb') as local_file:
            local_file.write(downloaded_file)
        encrypted_file_path = encrypt_file(local_file_path, public_key)
        if encrypted_file_path:
            with open(encrypted_file_path, 'rb') as encrypted_file:
                bot.send_document(message.chat.id, encrypted_file)
        else:
            bot.reply_to(message, 'Terjadi kesalahan saat melakukan enkripsi file.')
    except:
        bot.reply_to(message, 'Mohon maaf, terjadi kesalahan saat mengenkripsi file.')


# Handler untuk command /decryptfile
# Fungsi untuk melakukan dekripsi file dengan RSA
def decrypt_file(file_path, private_key):
    try:
        with open(file_path, 'r') as encrypted_file:
            encrypted_data = encrypted_file.read()
            decrypted_data = decrypt_text(encrypted_data, private_key)
            decrypted_file_path = file_path[:-4]  # Remove the '.enc' extension
            decrypted_file_path = decrypted_file_path + '.dec'  # Append '.dec' extension
            with open(decrypted_file_path, 'w') as decrypted_file:
                decrypted_file.write(decrypted_data)
            return decrypted_file_path
    except:
        return None
# Generate RSA keys
p = 61
q = 53
public_key, private_key = generate_keypair(p, q)
print("Kunci publik: ", public_key)
print("Kunci privat: ", private_key)

# Jalankan bot Telegram
bot.polling()
