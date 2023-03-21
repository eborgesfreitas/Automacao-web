from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time


#criando navegador
servico = Service(ChromeDriverManager().install())
nav = webdriver.Chrome(service=servico)

#importar/visualizar base de dados
tabela_produtos = pd.read_excel('buscas.xlsx')

#pegar infos do produto
produto = 'iphone 12 64 gb'
termos_banidos = 'mini watch'
preco_minimo = 3000
preco_maximo = 4500


def busca_google_shopping(nav, produto, termos_banidos, preco_minimo, preco_maximo):
    #tratando nomes banidos e palavras obrigatorias na busca
    produto = produto.lower()
    termos_banidos = termos_banidos.lower()
    lista_termos_nome_produto = produto.split(" ")
    lista_termos_banidos = termos_banidos.split(" ")
    lista_ofertas = []
    
    #abrir navegador
    nav.get('https://www.google.com.br/')
    time.sleep(1)
    nav.find_element('xpath', '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys(produto, Keys.ENTER)

    #entrar na aba shopping
    elementos = nav.find_elements("class name", "hdtb-mitem")
    for item in elementos:
        if 'Shopping' in item.text:
            item.click()
            break

    #pegar as informações do produto
    lista_resultados = nav.find_elements('class name', 'i0X6df')

    # nome do produto
    for resultado in lista_resultados:
        nome = resultado.find_element('class name', 'tAxDx').text
        nome = nome.lower()

        #analisar termos banidos
        tem_termos_banidos = False
        for palavra in lista_termos_banidos:
            if palavra in nome:
                tem_termos_banidos = True
                
        #analisar se tem TODOS os termos obrigatorios do nome
        tem_todos_termos_produtos = True
        for palavra in lista_termos_nome_produto:
            if palavra not in nome:
                tem_todos_termos_produtos = False
                
        #excluindo produtos com termos banidos e permitindo apenas os que possuam todos os nomes obrigatorios
        if not tem_termos_banidos and tem_todos_termos_produtos:
            #tratamento dos valores do preço
            preco = resultado.find_element('class name', 'a8Pemb').text
            preco = preco.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            preco = float(preco)
            preco_minimo = float(preco_minimo)
            preco_maximo = float(preco_maximo)
            #se o preco está entre minimo e maximo
            if preco_minimo <= preco <= preco_maximo:
                #pegando o link do produto
                elemento_referencia = resultado.find_element('class name', 'bONr3b')
                elemento_pai = elemento_referencia.find_element('xpath', '..')
                link = elemento_pai.get_attribute('href')
                lista_ofertas.append((nome, preco, link))
    return lista_ofertas

lista_ofertas_google_shopping = busca_google_shopping(nav, produto, termos_banidos, preco_minimo, preco_maximo)
print(lista_ofertas_google_shopping)