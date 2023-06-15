import telebot  
import math
import random
import binascii

# Inisialisasi bot Telegram
bot = telebot.TeleBot('6064228219:AAHJXDLMv_8o6SRe4cmWP7oyVlCyUassIMg')

# RSA
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

