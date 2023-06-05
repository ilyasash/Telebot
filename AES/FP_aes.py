import telebot
import hashlib
from Crypto.Cipher import AES
from Crypto import Random

# Inisialisasi bot Telegram
bot = telebot.TeleBot('5865372117:AAFRnrHzl5qwPM-3E1z0hjo9GIdboHNBca8')

# Fungsi untuk melakukan enkripsi teks dengan AES
def encrypt_text(message, key):
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    encrypted_message = iv + cipher.encrypt(message.encode())
    return encrypted_message

# Fungsi untuk melakukan dekripsi teks dengan AES
def decrypt_text(cipher_text, key):
    iv = cipher_text[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    decrypted_message = cipher.decrypt(cipher_text[AES.block_size:]).decode()
    return decrypted_message

# Handler untuk command /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Halo, selamat datang di bot enkripsi AES! Untuk enkripsi, ketik /encrypt 'pesan'. Untuk dekripsi, ketik /decrypt 'pesan terenkripsi'")

# Handler untuk command /encrypt
@bot.message_handler(commands=['encrypt'])
def encrypt_message(message):
    try:
        text = message.text.split(maxsplit=1)[1]
        key = hashlib.sha256(text.encode()).digest() # Menggunakan SHA-256 untuk menghasilkan kunci AES dari pesan
        encrypted_message = encrypt_text(text, key)
        bot.reply_to(message, f'Teks terenkripsi: {encrypted_message.hex()}')
    except:
        bot.reply_to(message, 'Mohon maaf, terjadi kesalahan saat melakukan enkripsi.')

# Handler untuk command /decrypt
@bot.message_handler(commands=['decrypt'])
def decrypt_message(message):
    try:
        cipher_text = message.text.split(maxsplit=1)[1]
        key = hashlib.sha256(cipher_text.encode()).digest()
        decrypted_message = decrypt_text(bytes.fromhex(cipher_text), key)
        bot.reply_to(message, f'Teks terdekripsi: {decrypted_message}')
    except:
        bot.reply_to(message, 'Mohon maaf, terjadi kesalahan saat melakukan dekripsi.')

# Jalankan bot Telegram
bot.polling()
