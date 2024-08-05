from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

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

    # Extrair todas as informações dentro da <div>
    currency_elements = main_div.find_elements(By.CSS_SELECTOR, 'div.Vd323d div')

    # Coletar dados das moedas
    data = []
    for element in currency_elements:
        try:
            currency_name = element.find_element(By.CSS_SELECTOR, 'span').text
            currency_value = element.find_element(By.CSS_SELECTOR, 'div div').text
            data.append({
                'Currency Name': currency_name,
                'Currency Value': currency_value
            })
        except Exception as e:
            print(f"Erro ao extrair informações de um elemento: {e}")

    # Salvar os dados em um arquivo Excel
    df = pd.DataFrame(data)
    df.to_excel('google_finance_currencies.xlsx', index=False)

    print('Dados salvos em google_finance_currencies.xlsx')

finally:
    # Fechar o navegador
    driver.quit()
