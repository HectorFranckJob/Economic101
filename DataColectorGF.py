from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime

# Configura as opções do Chrome para execução em contêiner
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executa o Chrome em modo headless (sem interface gráfica)
chrome_options.add_argument("--no-sandbox") # Desativa a sandbox, necessário ao rodar como root
chrome_options.add_argument("--disable-dev-shm-usage") # Supera limitações de recursos de memória compartilhada em contêineres

# Configurar o webdriver
service = Service() # Assumindo que o chromedriver está no PATH
driver = webdriver.Chrome(service=service, options=chrome_options)

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
    current_hour = datetime.today().strftime('%H-%M')

    # Adicionar colunas de data e hora ao DataFrame
    df['Date'] = today_date
    df['Time'] = current_time

    # Nome do arquivo com a data de hoje
    filename = f'google_finance_currencies_{today_date}_{current_hour}.xlsx' # O arquivo será salvo no diretório de trabalho /home/appuser/app

    # Salvar os dados em um arquivo Excel
    df.to_excel(filename, index=False)
    
    print(f'Dados salvos em {filename}')

finally:
    # Fechar o navegador
    driver.quit()
