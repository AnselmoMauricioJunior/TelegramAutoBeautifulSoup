import requests
import os
from dotenv import load_dotenv
import re

class Bard:
    def __init__(self) -> None:
        load_dotenv()
        self.token = os.getenv("__Secure-1PSID")
        self.linkAPI = os.getenv("URL_API_BARD")

    def perguntar(self,pergunta):
        
        url_pergunta = self.linkAPI+'assistant.lamda.BardFrontendService/StreamGenerate'
        
        padraoPergunta = '[null,"[[\\"{}\\",0,null,[],null,null,0],[\\"pt\\"],[null,null,null,null,null,[]],null,null,null,[0],0,[],[],1,0]"]'
        data={
            'f.req': padraoPergunta.format(pergunta),
            'at':'AOTFbH6Pgo5ghAyh5VRBXqa97ztL:1694617285880'
        }
        headers ={
            'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
            'Cookie':'__Secure-1PSID='+ '{}'.format(self.token)
        }
        response = requests.post(url_pergunta,        
        data=data,
        headers=headers)
        id_resposta, resposta = self.formatar_resposta(response)
        self.remover_pergunta_historico(id_resposta)
        return resposta
        
    def remover_pergunta_historico(self,id_pegunta):        
        url_pergunta = self.linkAPI+'batchexecute'        
        padraoPergunta = '[[["GzXR5e","[\\"{}\\"]",null,"generic"]]]'
        data={
            'f.req': padraoPergunta.format(id_pegunta),
            'at':'AOTFbH6Pgo5ghAyh5VRBXqa97ztL:1694617285880'
        }
        headers ={
            'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
            'Cookie':'__Secure-1PSID='+ '{}'.format(self.token)
        }
        response = requests.post(url_pergunta,        
        data=data,
        headers=headers)
        
    def formatar_resposta(self,response):
        resp =response.text[23:]
        resp = resp.replace(',null,',',').replace(',null','').replace('null,','')
        resp = resp.replace(',false,','').replace(',false','').replace('false,','')
        resp = resp.replace(',true,','').replace(',true','').replace('true,','')
        resp = resp.replace(',[],','').replace('["','"')
        resp = resp.replace('"]','"').replace('],',',').replace('[','').replace(']','')
        resp = resp.replace(',null,',',').replace(',null','').replace('null,','')
        resp = resp.replace(',false,','').replace(',false','').replace('false,','')
        resp = resp.replace(',true,','').replace(',true','').replace('true,','')
        resp = resp.replace('\\"','')
        resp = resp[0:resp.find("SWML_DESCRIPTION")]
        resp = re.sub(r"\,pt1(.*?)\,", ",", resp)
        resp = re.sub(r"\,pt-PT1(.*?)\,", ",", resp)
        resp = re.sub(r"\,pt-PT1(.*?)", "", resp)
        resp = resp.replace(', Brasil,','')
        resp = re.sub(r"\,ptrc(.*?)\,", ",", resp)

        id_resposta = 'c_'+re.search(r"c_(.*?)\,", resp).group(1)

        id_rc = 'rc_'+re.search(r"rc_(.*?)\,", resp).group(1)+','
        resposta = re.search(r"{}(.*)".format(id_rc), resp).group(1)
        resposta = resposta.replace('\\\\','\\')
        resposta = resposta.replace("\\r","\r").replace('\\n',"\n").replace('\\u003d',"\u003d")
        resposta = resposta.replace("**","~~").replace("*","#").replace("~~","*")
        return id_resposta,resposta

        
   

#bard = Bard()
#resposta = bard.perguntar('Gere um helloword em java')
#print(resposta)

