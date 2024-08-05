from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime

# Configurar o webdriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Acessar a página do Google Finance
driver.get('https://www.google.com/finance/markets/currencies')

try:
    # Esperar até que a <div> com class 'Vd323d' esteja presente
    wait = WebDriverWait(driver, 15)  # Espera até 15 segundos
    main_div = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Vd323d[role="main"]'))
    )

    # Extrair todas as informações dentro da <div> com classes 'ZvmM7' e 'YMlKec'
    zvm_elements = main_div.find_elements(By.CSS_SELECTOR, 'div.ZvmM7')
    yml_elements = main_div.find_elements(By.CSS_SELECTOR, 'div.YMlKec')

    # Coletar dados das moedas
    data = []
    for zvm, yml in zip(zvm_elements, yml_elements):
        try:
            currency_name = zvm.text
            currency_value = yml.text
            data.append({
                'Currency Pair': currency_name,
                'Currency Value': currency_value
            })
        except Exception as e:
            print(f"Erro ao extrair informações de um elemento: {e}")

    # Criar DataFrame a partir dos dados
    df = pd.DataFrame(data)

    # Separar a coluna 'Currency Pair' em duas colunas: 'From Currency' e 'To Currency'
    df[['From Currency', 'To Currency']] = df['Currency Pair'].str.split(' / ', expand=True)

    # Remover a coluna original 'Currency Pair'
    df.drop(columns=['Currency Pair'], inplace=True)

    # Obter a data e hora atuais
    today_date = datetime.today().strftime('%Y-%m-%d')
    current_time = datetime.today().strftime('%H:%M:%S')

    # Adicionar colunas de data e hora ao DataFrame
    df['Date'] = today_date
    df['Time'] = current_time

    # Nome do arquivo com a data de hoje
    filename = f'google_finance_currencies_{today_date}.xlsx'

    # Salvar os dados em um arquivo Excel
    df.to_excel(filename, index=False)

    print(f'Dados salvos em {filename}')

finally:
    # Fechar o navegador
    driver.quit()
