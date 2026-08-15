
# Automação de Busca de Vagas - Gupy

# Projeto de automação com Selenium para busca e coleta de vagas no Gupy.


## 1. Configuração inicial
 
# Importação de bibliotecas e configuração do navegador.

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote
from pathlib import Path
import pandas as pd
import logging



## 2. Busca, extração e paginação
 
# Função que busca vagas para um cargo, navega automaticamente por todas as páginas de resultado e extrai os dados de cada vaga encontrada.

def buscar_vagas(driver: WebDriver, termo: str) -> list:
    """
    Realiza a raspagem de vagas no Portal Gupy para uma localidade específica.

    Navega pelas páginas de resultados coletando informações detalhadas de cada 
    vaga disponível e trata possíveis instabilidades de carregamento ou fim de paginação.

    Args:
        driver (WebDriver): Instância ativa do navegador controlada pelo Selenium.
        termo (str): O cargo ou palavra-chave que será pesquisado.

    Returns:
        list[dict]: Uma lista de dicionários, onde cada dicionário contém as 
        informações de uma vaga (Título, Empresa, Local, Modelo, Tipo, Data, Link).
        Retorna uma lista vazia se nenhuma vaga for encontrada ou houver timeout.
    """
    # Monta a URL de busca já com o cargo e o filtro de localização codificados
    nome_vaga = quote(termo)

    # Filtra apenas vagas com modelo de trabalho remoto; "remote" não precisa
    # de quote() por não ter espaço nem acento
    filtro_modelo = "remote"

    link_vaga = f"https://portal.gupy.io/job-search/term={nome_vaga}&workplaceTypes[]={filtro_modelo}"

    driver.get(link_vaga)

    lista_vagas = []

    # Percorre todas as páginas de resultado até não existir mais próxima página
    while True:
        try:
        
            try:
                # Espera os cards de vaga aparecerem; se nenhum aparecer a tempo, considera
                # que o cargo não teve resultado e devolve o que já foi coletado até aqui
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/job/"]')))
            except TimeoutException:
                logging.info(f"Para o cargo '{termo}' não foram encontradas vagas ou a página falhou.")
                logging.info(f"Aviso: Tempo limite atingido para o cargo {termo}.")
                return lista_vagas

            vagas = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/job/"]')

            for vaga in vagas:
                
                titulo = vaga.find_element(By.TAG_NAME, "h3").text

                empresas = vaga.find_elements(By.TAG_NAME, "p")

                # O card tem dois <p>: um é a empresa, o outro é a data de publicação
                # (identificados pelo prefixo fixo "Publicada em:")
                for empresa in empresas:
                    if not empresa.text.startswith("Publicada em:"):
                        nome_empresa = empresa.text
                    else:
                        data_vaga_publicada = empresa.text

                # Local é um campo opcional: pode não vir preenchido em algumas vagas
                local = vaga.find_elements(By.CSS_SELECTOR, 'span[data-testid="job-location"]')

                if len(local) == 0:
                    local_vaga = None
                else:
                    local_vaga = local[0].text

                # Modelo de trabalho, tipo de vaga e PcD não têm atributo próprio e são
                # opcionais, então são classificados pelo conteúdo do texto de cada span
                modelos_trabalho = [
                    "Presencial",
                    "Híbrido",
                    "Remoto"
                    ]

                tipos_vaga = [
                    "Estágio",
                    "Efetivo",
                    "Associado",
                    "Autônomo",
                    "Temporário",
                    "Pessoa Jurídica",
                    "Trainee",
                    "Sócio"
                    ]

                elementos_span = vaga.find_elements(By.TAG_NAME, "span")

                modelo_encontrado = None
                tipo_vaga_encontrada = None
                pcd_encontrado = None

                for el_span in elementos_span:
                    if el_span.text in modelos_trabalho:
                        modelo_encontrado = el_span.text

                    elif el_span.text in tipos_vaga:
                        tipo_vaga_encontrada = el_span.text

                    elif el_span.text == "Também p/ PcD":
                        pcd_encontrado = el_span.text
                        
                link = vaga.get_attribute("href")

                dic_vagas = {
                    "Cargo Buscado": termo,
                    "Titulo": titulo,
                    "Empresa": nome_empresa,
                    "Local": local_vaga,
                    "Modelo": modelo_encontrado,
                    "Tipo da Vaga": tipo_vaga_encontrada,
                    "Afirmativa para PcD": pcd_encontrado,
                    "Data": data_vaga_publicada,
                    "Link": link
                    }

                lista_vagas.append(dic_vagas)

            # Verifica se existe próxima página habilitada antes de tentar avançar
            proxima_pagina = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Próxima página"]')
            
            if proxima_pagina.is_enabled():
                proxima_pagina.click()
                try:
                    # Espera o conteúdo antigo sumir do DOM antes de considerar a página
                    # seguinte carregada, evitando StaleElementReferenceException
                    WebDriverWait(driver, 10).until(EC.staleness_of(vagas[0]))
                except TimeoutException:
                    logging.info(f"Timeout ao carregar a próxima página para '{termo}'. Retornando o que foi coletado até aqui.")
                    return lista_vagas
            else:
                break

        except NoSuchElementException:
            logging.info(f"Botão não encontrado. Fim das páginas para {termo}.")
            break           
            
    return lista_vagas



if __name__ == "__main__":

    # Localiza a pasta do projeto a partir do próprio arquivo, garantindo que o
    # caminho funcione independente de onde o script for executado
    pasta_projeto = Path(__file__).parent

    # Garante que as pastas existam mesmo numa cópia nova do repositório
    # (parents=True cria pastas intermediárias; exist_ok=True evita erro se já existirem)
    pasta_reports = pasta_projeto / "reports"
    pasta_reports.mkdir(parents=True, exist_ok=True)

    pasta_logs = pasta_projeto / "logs"
    pasta_logs.mkdir(parents=True, exist_ok=True)

    caminho_csv = pasta_reports / "vagas_encontradas.csv"

    caminho_log = pasta_logs / "execucao.log"

    # Registra as execuções em arquivo (com data/hora de cada linha), já que o
    # script roda de forma automática e sem supervisão via Agendador de Tarefas
    logging.basicConfig(
    filename=caminho_log,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8-sig"
    )

    # Separador visual no log, facilitando identificar onde cada execução começa
    logging.info("=" * 60)
    logging.info("Início da execução")

    ## 3. Iniciar o navegador

    # Criação da instância do navegador e acesso à página inicial do Gupy.

    # Abre o navegador e acessa a página inicial do Gupy
    servico = Service(ChromeDriverManager().install())

    # Roda sem interface visível (headless) e fixa o tamanho de renderização,
    # já que o site é responsivo e sem isso poderia carregar em layout mobile,
    # quebrando os seletores validados no layout desktop
    opcoes = Options()
    opcoes.add_argument("--headless=new")
    opcoes.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=servico, options=opcoes)
    driver.get("https://portal.gupy.io/job-search")

    ## 4. Execução para múltiplos cargos

    # Executa a busca para uma lista de cargos, juntando os resultados de todos em uma única lista.

    cargos = [
        "Estágio TI",
        #"Analista de Dados Júnior",
        #"Desenvolvedor Júnior",
        #"Python Junior",
        #"Analista de Sistema Júnior",
        #"Analista de Suporte Júnior"
        ]

    logging.info(f"Buscando {len(cargos)} cargos: {', '.join(cargos)}")

    vagas_encontradas = []

    for cargo in cargos:
        # extend (e não append) porque cada chamada já devolve uma lista de vagas,
        # mantendo tudo em uma única lista de dicionários, sem aninhamento
        vagas_encontradas.extend(buscar_vagas(driver, cargo))

    ## 5. Organização e exportação dos dados

    # Transformar os resultados em DataFrame e exportar para CSV.

    tabela_vagas = pd.DataFrame(vagas_encontradas)

    # Remove o texto fixo da data e converte para datetime (dia primeiro,
    # formato brasileiro), permitindo ordenar/filtrar por período depois
    tabela_vagas["Data"] = tabela_vagas["Data"].str.replace("Publicada em:", "", regex=False).str.strip()

    tabela_vagas["Data"] = pd.to_datetime(tabela_vagas["Data"], format='%d/%m/%Y')

    # Preenche apenas os campos opcionais, mantendo a coluna Data intacta
    colunas_nulos = [col for col in tabela_vagas.columns if col != "Data"]

    for coluna in colunas_nulos:
        tabela_vagas[coluna] = tabela_vagas[coluna].fillna("Não informado") 

    # Lê o histórico de execuções anteriores, se existir, para acumular os
    # resultados entre execuções em vez de sobrescrever a cada rodada
    if caminho_csv.exists():
        dados_antigos = pd.read_csv(caminho_csv, sep=";", encoding="utf-8-sig", parse_dates=["Data"], date_format='%d/%m/%Y')
    else:
        dados_antigos = pd.DataFrame(columns=tabela_vagas.columns)

    # Junta o histórico já salvo com as vagas coletadas nesta execução
    dados_finais = pd.concat([dados_antigos, tabela_vagas], ignore_index=True)

    # Remove vagas repetidas entre buscas de cargos diferentes, usando o
    # link como identificador único de cada vaga
    dados_finais = dados_finais.drop_duplicates(subset=["Link"])

    dados_finais.to_csv(caminho_csv, index=False, sep=";", encoding="utf-8-sig", date_format='%d/%m/%Y')

    logging.info(f"Arquivo CSV salvo em: {caminho_csv}")
    logging.info(f"Vagas novas nesta execução: {len(dados_finais) - len(dados_antigos)}")
    logging.info(f"Total acumulado de vagas: {len(dados_finais)}")
    logging.info("Execução finalizada com sucesso")
    logging.info("=" * 60)

    driver.quit()
