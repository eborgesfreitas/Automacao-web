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

#FUNÇÕES PARA VERIFICAR TERMOS BANIDOS E TERMOS OBRIGATÓRIOS
def verificar_tem_termos_banidos(lista_termos_banidos, nome):
    tem_termos_banidos = False
    for palavra in lista_termos_banidos:
        if palavra in nome:
            tem_termos_banidos = True
    return tem_termos_banidos

def verificar_tem_todos_termos(lista_termos_nome_produto, nome):
    tem_todos_termos_produtos = True
    for palavra in lista_termos_nome_produto:
        if palavra not in nome:
            tem_todos_termos_produtos = False
    return tem_todos_termos_produtos


#FUNÇÃO PARA BUSCA NO GOOGLE SHOPPING
def busca_google_shopping(nav, produto, termos_banidos, preco_minimo, preco_maximo):
    #tratando nomes banidos e palavras obrigatorias na busca
    produto = produto.lower()
    termos_banidos = termos_banidos.lower()
    lista_termos_nome_produto = produto.split(" ")
    lista_termos_banidos = termos_banidos.split(" ")
    preco_minimo = float(preco_minimo)
    preco_maximo = float(preco_maximo)
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
        tem_termos_banidos = verificar_tem_termos_banidos(lista_termos_banidos, nome)
                
        #analisar se tem TODOS os termos obrigatorios do nome
        tem_todos_termos_produtos = verificar_tem_todos_termos(lista_termos_nome_produto, nome)
                
        #excluindo produtos com termos banidos e permitindo apenas os que possuam todos os nomes obrigatorios
        if not tem_termos_banidos and tem_todos_termos_produtos:
            #tratamento dos valores do preço
            preco = resultado.find_element('class name', 'a8Pemb').text
            preco = preco.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            preco = float(preco)
            
            #se o preco está entre minimo e maximo
            if preco_minimo <= preco <= preco_maximo:
                #pegando o link do produto
                elemento_referencia = resultado.find_element('class name', 'bONr3b')
                elemento_pai = elemento_referencia.find_element('xpath', '..')
                link = elemento_pai.get_attribute('href')
                lista_ofertas.append((nome, preco, link))
    return lista_ofertas


#FUNÇÃO PARA BUSCA NO BUSCAPÉ
def busca_buscape(nav, produto, termos_banidos, preco_minimo, preco_maximo):
    #tratando nomes banidos e palavras obrigatorias na busca e preço
    produto = produto.lower()
    termos_banidos = termos_banidos.lower()
    lista_termos_nome_produto = produto.split(" ")
    lista_termos_banidos = termos_banidos.split(" ")
    preco_minimo = float(preco_minimo)
    preco_maximo = float(preco_maximo)
    lista_ofertas = []

    #abrir navegador
    nav.get('https://www.buscape.com.br/')
    time.sleep(1)
    nav.find_element('xpath', '//*[@id="new-header"]/div[1]/div/div/div[3]/div/div/div[2]/div/div[1]/input').send_keys(produto, Keys.ENTER)
    time.sleep(2)

    #pegar as informações do produto
    lista_resultados = nav.find_elements('class name', 'SearchCard_ProductCard_Inner__7JhKb')

    for resultado in lista_resultados:
        preco = resultado.find_element('class name', 'Text_MobileHeadingS__Zxam2').text
        nome = resultado.find_element('class name', 'SearchCard_ProductCard_Name__ZaO5o').text
        nome = nome.lower()
        link = resultado.get_attribute('href')

        #analisar termos banidos
        tem_termos_banidos = verificar_tem_termos_banidos(lista_termos_banidos, nome)
                
        #analisar se tem TODOS os termos obrigatorios do nome
        tem_todos_termos_produtos = verificar_tem_todos_termos(lista_termos_nome_produto, nome)

        #analisar se o preço está entre minimo e máximo
        if not tem_termos_banidos and tem_todos_termos_produtos:
            #tratar o preço
            preco = preco.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            preco = float(preco)
            if preco_minimo <= preco <= preco_maximo:
                lista_ofertas.append((nome, preco, link))
    
    return lista_ofertas
    

#CONSTRUINDO A LISTA DE OFERTAS E MONTANDO UM DATAFRAME
tabela_ofertas = pd.DataFrame()
for linha in tabela_produtos.index:
    #pegar infos do produto
    produto = tabela_produtos.loc[linha, "Nome"]
    termos_banidos = tabela_produtos.loc[linha, "Termos banidos"]
    preco_minimo = tabela_produtos.loc[linha, "Preço mínimo"]
    preco_maximo = tabela_produtos.loc[linha, "Preço máximo"]

    #executando função do google shopping
    lista_ofertas_google_shopping = busca_google_shopping(nav, produto, termos_banidos, preco_minimo, preco_maximo)
    if lista_ofertas_google_shopping:
        tabela_google_shopping = pd.DataFrame(lista_ofertas_google_shopping, columns=['Produto', 'Preço', 'link'])
        tabela_ofertas = pd.concat([tabela_ofertas, tabela_google_shopping])
    else:
        tabela_google_shopping = None
        
    #executando função do buscapé
    lista_ofertas_buscape = busca_buscape(nav, produto, termos_banidos, preco_minimo, preco_maximo)
    if lista_ofertas_buscape:
        tabela_buscape = pd.DataFrame(lista_ofertas_buscape, columns=['Produto', 'Preço', 'link'])
        tabela_ofertas = pd.concat([tabela_ofertas, tabela_buscape])
    else:
        tabela_buscape = None

tabela_ofertas = tabela_ofertas.sort_values(by='Preço')    
#EXPORTANDO PARA O EXCEL
tabela_ofertas.to_excel("Ofertas.xlsx", index=False)