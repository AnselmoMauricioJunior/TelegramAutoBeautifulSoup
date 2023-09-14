import telebot
import os
from dotenv import load_dotenv
from Meditacao import Meditacao
from Licao import Licao
from GoogleBard import Bard

load_dotenv()
print("Obtendo token...")
bot_token = os.getenv("TOKEN_TELEGRAM")
bot = telebot.TeleBot(bot_token)
print("Aplicação iniciada")

def nome_arquivo_mais_recente(caminho_pasta):
    arquivos = [os.path.join(caminho_pasta, arquivo) for arquivo in os.listdir(caminho_pasta)]
    if not arquivos:
        return None

    arquivos.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    return os.path.basename(arquivos[0])

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):    
    bot.reply_to(message, "Olá, Como posso te ajudar?")

@bot.message_handler(commands=['meditacao'])
def send_meditacao(message):
    bot.reply_to(message, "Baixando meditação...")
    bot.send_message(message.chat.id,"Aguarde")
    Meditacao()

    caminho_pasta = "meditacoes"
    file_path = nome_arquivo_mais_recente(caminho_pasta)

    with open(caminho_pasta+"/"+file_path, 'rb') as pdf_file:
        bot.send_document(message.chat.id, pdf_file)

@bot.message_handler(commands=['licao'])
def send_licao(message):
    bot.reply_to(message, "Baixando lição...")
    bot.send_message(message.chat.id,"Aguarde")
    Licao()

    caminho_pasta = "licoes"
    file_path = nome_arquivo_mais_recente(caminho_pasta)

    with open(caminho_pasta+"/"+file_path, 'rb') as pdf_file:
        bot.send_document(message.chat.id, pdf_file)

@bot.message_handler(commands=['bot'])
def send_bot(message):   
    bot.send_message(message.chat.id,"Digitando...") 
    pergunta = message.text.replace('/bot ','')  
    bard = Bard()  
    resposta = bard.perguntar(pergunta)
    bot.reply_to(message, resposta)

bot.infinity_polling()