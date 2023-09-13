import re
import os
import requests
from bs4 import BeautifulSoup
from xhtml2pdf import pisa
import json


class Licao:
    def __init__(self):
        start_urls = 'https://mais.cpb.com.br/licao-adultos/'
        
        response = self.Request(url=start_urls)

        soup = BeautifulSoup(response.text, 'html.parser')
        licao_corrente = soup.find('licao-corrente', {'class': 'licoes'})
        json_data_str = re.search(r'\[(.*?)\]', str(licao_corrente)).group(0)
        json_data = json.loads(json_data_str)
        url_licao_corrente = json_data[0].get('link', None)
        self.Request(url=url_licao_corrente,callback=self.parse_licao)        

    def parse_licao(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        all_divs = str(soup.find('div'))
        lista_de_divs = all_divs.split("<div")
        lista_de_divs = lista_de_divs[1:]
        lista_de_divs = ["<div" + div for div in lista_de_divs]

        licao_da_semana = self.extract_licao(lista_de_divs)
        nome_licao = self.get_nome_licao(licao_da_semana)
        licao_da_semana = self.formatar_licao(licao_da_semana)
        self.gerar_pdf(nome_licao,licao_da_semana)

    def get_nome_licao(self,licao_da_semana):
        for linha in licao_da_semana:
            if 'class="descriptionText numberLicao"' in linha:
                soup = BeautifulSoup(linha, 'html.parser')
                return soup.div.get_text().strip()

    def gerar_pdf(self,nome,licao_da_semana):
        if not os.path.exists("licoes"):
            os.makedirs("licoes")

        with open("licoes/"+nome+".pdf", "wb") as pdf_file:
            pisa.CreatePDF(''.join(licao_da_semana), dest=pdf_file)

    def extract_licao(self,lista_de_divs):
        licao_da_semana = []
        cont=0
        for div in lista_de_divs:
            if self.is_valid_div(div):
                div = self.remove_links_from_div(div)
                div = self.remove_p_tags_from_div(div)

                if 'class="imageLicao"' in div:                  
                    url_imagem_licao = self.extract_image_url_from_div(div)
                    div = self.set_img_licao(url_imagem_licao)  

                licao_da_semana.append(div)
            
                if 'class="conteudoLicaoDia"' in div:
                    cont+= 1 

                if cont == 7:
                    break
        return licao_da_semana

    def is_valid_div(self, div_text):
        return any(classe_valida in div_text for classe_valida in self.list_classe_validas())

    def remove_links_from_div(self, div_text):
        return re.sub(r'<a[^>]*>.*?</a>', '', div_text)

    def remove_p_tags_from_div(self, div_text):
        return re.sub(r'<p data-pm-slice=[^>]*>.*?</p>', '', div_text)

    def extract_image_url_from_div(self, div_text):
        return re.search(r'url\((.*?)\)', div_text).group(1)

    def set_img_licao(self,url_imagem):
        return '<img class="cpbMaisLogo" style="text-align: center;" src="'+url_imagem+'"</img>' 

    def list_classe_validas(self):
        return ['class="titleLicao"',
        'class="imageLicao"',
        'class="descriptionText diaSabadoLicao"',
        'class="descriptionText dateLicao"',
        'class="descriptionText anoBiblicoDia"',
        'class="descriptionText"',
        'class="versoMemorizarLicao boxLicao"',
        'class="descriptionText numberLicao"',
        'class="leiturasSemanaLicao"',
        'class="conteudoLicaoDia"',
        'class="rodapeLicaoDia"',
        'class="titleLicaoDay"',
        'class="rodapeBoxLicaoDia boxLicao"',
        'class="mdl-typography--display-1"']
    
    def formatar_licao(self,licao_da_semana):
        codigo_css = """<style>
                        .dateLicao, .anoBiblicoDia, .diaExtensoLicao {
                            text-align: right;
                        }
                        .titleLicao, .imageLicao {
                            text-align: center;
                        }
                        .versoMemorizar {
                            font-style: italic;
                        }
                        .versoMemorizarChamada, .leiturasSemanaChamada {
                            text-transform: uppercase;
                            font-weight: 600;
                            font-size: 14px;
                        }
                        .titleLicao {
                            margin-top: 20px;
                            text-align: center;
                            color: #767777;
                        }
                        .mdl-typography--display-1, .mdl-typography--display-1-color-contrast {
                            font-family: "Roboto","Helvetica","Arial",sans-serif;
                            font-size: 34px;
                            font-weight: 400;
                            line-height: 40px;
                        }
                        .boxLicao {
                            font-size: 14px;
                            padding: 5px 8px;
                            background: #f1f1f1;
                        }
                        .rodapeBoxLicaoDia {
                            margin-top: 5%;
                            font-size: 13px;
                            font-style: italic;
                        }
                        .leiturasSemanaChamada {
                            letter-spacing: 0.1em;
                        }
                        .leiturasSemanaChamada, .leiturasSemana {
                            font-size: 14px;
                        }
                        p {
                            font-size: 12px;
                            letter-spacing: 0;
                            margin: 0 0 16px;
                        }
                        .descriptionText {
                            font-size: 14px;
                            font-weight: 400;
                        }
                        .conteudoLicaoDia, .autorComentario {
                            text-align: justify;
                        }
                        ul, ol {
                            font-size: 14px;
                            line-height: 24px;
                        }
                        .leiturasSemanaLicao {
                            margin: 10px 0;
                        }
                        </style>
                        """
        licao_da_semana.append(codigo_css)
        return licao_da_semana

    def Request(self, url,callback=None):
        response = requests.get(url,verify = False)

        if callback is None:
            return response

        callback(response)

#Licao()