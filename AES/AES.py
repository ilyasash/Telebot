import os
from Crypto.Cipher import AES
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = 'YOUR_TOKEN_BOT'

# Fungsi enkripsi teks menggunakan AES
def encrypt_text(key, plaintext):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(bytes(plaintext, 'utf-8'))
    return cipher.nonce + tag + ciphertext

# Fungsi dekripsi teks menggunakan AES
def decrypt_text(key, ciphertext):
    nonce = ciphertext[:16]
    tag = ciphertext[16:32]
    ciphertext = ciphertext[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode('utf-8')

# Fungsi enkripsi file menggunakan AES
def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = os.urandom(16)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(filesize.to_bytes(8, byteorder='big'))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

    return out_filename

# Fungsi dekripsi file menggunakan AES
def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = int.from_bytes(infile.read(8), byteorder='big')
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break

                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

    return out_filename

# Handler untuk menerima file
def receive_file(update, context):
    file = context.bot.get_file(update.message.document.file_id)
    # Simpan file yang diterima dengan nama 'received_file'
    file.download('received_file')
    context.user_data['received_file'] = 'received_file'  # Simpan nama file di user_data
    context.bot.send_message(chat_id=update.effective_chat.id, text='File diterima')

# Handler command /start
def start(update, context):
    message = "Halo! Selamat datang di Bot Kriptografi.\n\n"
    message += "Berikut adalah daftar fungsi yang dapat digunakan:\n"
    message += "/encrypt <plaintext> : Enkripsi teks menggunakan AES.\n"
    message += "/decrypt <ciphertext> : Dekripsi teks menggunakan AES.\n"
    message += "/encryptfile : Enkripsi file menggunakan AES.\n"
    message += "/decryptfile : Dekripsi file menggunakan AES."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Handler command /encrypt
def encrypt(update, context):
    plaintext = ' '.join(context.args)
    key = os.urandom(32)
    ciphertext = encrypt_text(key, plaintext)
    message = "Teks berhasil dienkripsi.\n\n"
    message += "Key: " + key.hex() + "\n\n"
    message += "Ciphertext: " + ciphertext.hex()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Handler command /decrypt
def decrypt(update, context):
    if len(context.args) < 2:
        message = "Argumen tidak valid. Gunakan /decrypt <ciphertext> <key>."
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return

    ciphertext = bytes.fromhex(context.args[0])
    key = bytes.fromhex(context.args[1])
    plaintext = decrypt_text(key, ciphertext)
    message = "Teks berhasil didekripsi.\n\n"
    message += "Plaintext: " + plaintext
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Handler command /encryptfile
def encryptfile(update, context):
    if 'received_file' not in context.user_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Mohon kirimkan file terlebih dahulu')
        return

    key = os.urandom(32)
    in_filename = context.user_data['received_file']
    out_filename = encrypt_file(key, in_filename)
    # Mengirim file terenkripsi
    context.bot.send_document(chat_id=update.effective_chat.id, document=open(out_filename, 'rb'))
    # Mengirim key dalam format string heksadesimal
    context.bot.send_message(chat_id=update.effective_chat.id, text="Key: " + key.hex())
    os.remove(out_filename)  # Hapus file hasil enkripsi setelah dikirim

# Handler command /decryptfile
def decryptfile(update, context):
    if 'received_file' not in context.user_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Mohon kirimkan file terlebih dahulu')
        return

    if len(context.args) < 1:
        message = "Argumen tidak valid. Gunakan /decryptfile <key>."
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return

    key = bytes.fromhex(context.args[0])
    in_filename = context.user_data['received_file']
    out_filename = decrypt_file(key, in_filename)
    context.bot.send_document(chat_id=update.effective_chat.id, document=open(out_filename, 'rb'))
    os.remove(out_filename)  # Hapus file hasil dekripsi setelah dikirim

# Inisialisasi updater
updater = Updater(token=TOKEN, use_context=True)

# Daftarkan handler
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('encrypt', encrypt))
updater.dispatcher.add_handler(CommandHandler('decrypt', decrypt))
updater.dispatcher.add_handler(CommandHandler('encryptfile', encryptfile))
updater.dispatcher.add_handler(CommandHandler('decryptfile', decryptfile))
updater.dispatcher.add_handler(MessageHandler(Filters.document, receive_file))

# Jalankan bot
updater.start_polling()
updater.idle()
