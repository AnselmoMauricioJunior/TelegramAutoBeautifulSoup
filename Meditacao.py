import re
import os
import requests
from bs4 import BeautifulSoup
from xhtml2pdf import pisa


class Meditacao:
    def __init__(self):
        start_urls = 'https://mais.cpb.com.br/meditacoes-diarias/'
        
        response = self.Request(url=start_urls)

        soup = BeautifulSoup(response.text, 'html.parser')
        meditacao = soup.find('div', {'class': 'mdl-card__actions mdl-card--border'})
        url_meditacao = re.search(r'post_type=meditacao&amp;p=([0-9]+)', str(meditacao)).group(0)
        url_meditacao = url_meditacao.replace('amp;','')
        url_meditacao='https://mais.cpb.com.br/?'+url_meditacao
        self.Request(url=url_meditacao,callback=self.parse_meditacao)

        

    def parse_meditacao(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        all_divs = str(soup.find('div'))
        lista_de_divs = all_divs.split("<div")
        lista_de_divs = lista_de_divs[1:]
        lista_de_divs = ["<div" + div for div in lista_de_divs]
        
        meditacao_semana = self.extract_meditacao(lista_de_divs)
        nome_meditacao = self.get_nome_meditacao(meditacao_semana)
        meditacao_semana = self.formatar_meditacao(meditacao_semana)
        self.gerar_pdf(nome_meditacao,meditacao_semana)

    def gerar_pdf(self,nome,meditacao_semana):
        if not os.path.exists("meditacoes"):
            os.makedirs("meditacoes")

        with open("meditacoes/"+nome+".pdf", "wb") as pdf_file:
            pisa.CreatePDF(''.join(meditacao_semana), dest=pdf_file)

    def get_nome_meditacao(self,meditacao_semana):
        nome = ''
        for linha in meditacao_semana:

            if 'class="descriptionText diaSemanaMeditacao"' in linha:
                soup = BeautifulSoup(linha, 'html.parser')
                nome = nome + soup.div.get_text().strip()
            
            if 'class="descriptionText diaMesMeditacao"' in linha:
                soup = BeautifulSoup(linha, 'html.parser')
                nome = nome +' - '+soup.div.get_text().strip()

            if 'class="mdl-typography--headline"' in linha:
                soup = BeautifulSoup(linha, 'html.parser')
                nome = nome +' - '+ soup.div.get_text().strip()
                return nome
    def extract_meditacao(self,lista_de_divs):
        meditacao_da_semana = []
        for div in lista_de_divs:
            if self.is_valid_div(div):
                div = self.remove_links_from_div(div)
                div = self.remove_p_tags_from_div(div)

                meditacao_da_semana.append(div)
                            
        return meditacao_da_semana

    def is_valid_div(self, div_text):
        return any(classe_valida in div_text for classe_valida in self.list_classe_validas())

    def remove_links_from_div(self, div_text):
        return re.sub(r'<a[^>]*>.*?</a>', '', div_text)

    def remove_p_tags_from_div(self, div_text):
        return re.sub(r'<p data-pm-slice=[^>]*>.*?</p>', '', div_text)

     
    def list_classe_validas(self):
        return ['class="titleMeditacao"',
        'class="mdl-typography--headline"',
        'class="descriptionText versoBiblico"',
        'class="conteudoMeditacao"',
        'class="descriptionText diaSemanaMeditacao"',
        'class="descriptionText diaMesMeditacao"']
    
    def formatar_meditacao(self,meditacao_da_semana):
        codigo_css = """<style>
                        .diaMesMeditacao {
                            text-align: right;
                        }
                        .mdl-typography--headline, .mdl-typography--headline-color-contrast {
                            font-family: "Roboto","Helvetica","Arial",sans-serif;
                            font-size: 24px;
                            font-weight: 400;
                            line-height: 32px;
                            -moz-osx-font-smoothing: grayscale;
                        }
                        .descriptionText.versoBiblico {
                            margin: 30px 0 30px 0;
                            font-style: italic;
                            font-weight: 500;
                            font-size: 13px;
                            text-align: justify;
                            background: #f1f1f1;
                        }
                        p {
                            font-size: 14px;
                            letter-spacing: 0;
                            margin: 0 0 16px;
                        }
                        h6, p {
                            font-weight: 400;
                            line-height: 24px;
                        }
                        .conteudoMeditacao{
                            text-align: justify;
                        }                        
                        .titleMeditacao {
                            margin-top: 20px;
                            text-align: center;
                            color: #767777;
                            font-weight: bold;
                        }
                        </style>
                        """
        meditacao_da_semana.append(codigo_css)
        return meditacao_da_semana

    def Request(self, url,callback=None):
        response = requests.get(url,verify = False)

        if callback is None:
            return response

        callback(response)

#med = Meditacao()
