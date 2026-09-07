
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
from email.message import EmailMessage
from dotenv import load_dotenv
import pandas as pd
import logging
import requests
import os
import smtplib



load_dotenv()
destinatario = os.getenv("EMAIL_DESTINATARIO")
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")


## 2. Busca, extração e paginação
 
# Função que busca vagas para um cargo, navega automaticamente por todas as páginas de resultado e extrai os dados de cada vaga encontrada.

def buscar_vagas(driver: WebDriver, termo: str) -> list:
    """
    Realiza a busca e coleta de vagas remotas no Portal Gupy para um termo informado.

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

    # Monta a URL de busca já com o cargo e o filtro de modelo de trabalho
    nome_vaga = quote(termo)

    # Filtra apenas vagas com modelo de trabalho remoto; "remote"
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
                logging.warning(f"Para o cargo '{termo}' não foram encontradas vagas ou a página falhou.")
                logging.warning(f"Aviso: Tempo limite atingido para o cargo {termo}.")
                return lista_vagas

            vagas = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/job/"]')

            for vaga in vagas:
                
                titulo = vaga.find_element(By.TAG_NAME, "h3").text

                empresas = vaga.find_elements(By.TAG_NAME, "p")

                nome_empresa = None
                data_vaga_publicada = None

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


def enviar_email(destinatario: str, assunto: str, corpo_email: str, corpo_email_html: str) -> bool:
    """
    Envia uma notificação por e-mail utilizando SMTP com autenticação e TLS.

    A mensagem contém uma versão em texto simples e, quando fornecida, uma
    alternativa em HTML. As credenciais do remetente são obtidas por meio
    das variáveis de ambiente configuradas no arquivo .env.

    Args:
        destinatario (str): Endereço de e-mail que receberá a notificação.
        assunto (str): Assunto da mensagem.
        corpo_email (str): Conteúdo da mensagem em texto simples.
        corpo_email_html (str): Conteúdo alternativo da mensagem em HTML.

    Returns:
        bool: True se o e-mail for enviado com sucesso e False se houver
        falha de configuração ou erro durante o envio.
    """
    remetente = os.getenv("EMAIL_REMETENTE")
    senha = os.getenv("EMAIL_SENHA_APP")

    if not remetente or not senha or not destinatario:
        logging.error("Erro: remetente, senha ou destinatário não configurado.")
        return False
    
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    msg.set_content(corpo_email)

    if corpo_email_html:
        msg.add_alternative(corpo_email_html, subtype="html")

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    try:

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Criptografa a conexão
            server.login(remetente, senha)
            server.send_message(msg)
        logging.info("E-mail enviado com sucesso!")    

    except Exception as e:
        logging.error(f"Falha ao enviar notificação por e-mail: {e}")
        return False

    return True


if __name__ == "__main__":

    # Configura os logs da execução para saída padrão, permitindo visualização no terminal e captura pelo Cloud Logging.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Separador visual no log, facilitando identificar onde cada execução começa
    logging.info("=" * 60)
    logging.info("Início da execução")

    ## 3. Iniciar o navegador

    # Criação da instância do navegador e acesso à página inicial do Gupy.
  
    driver = None
    
    try:
        if API_URL is None or API_URL == "":
            raise RuntimeError("A 'API_URL' não está definida. A aplicação não pode ser iniciada sem a configuração da API.")
        
        if API_KEY is None or API_KEY == "":
            raise RuntimeError("A 'API_KEY' não está definida. A aplicação não pode ser iniciada sem as credenciais de autenticação.")

        headers = {"X-API-Key": API_KEY}

        # Abre o navegador e acessa a página inicial do Gupy
        

        # Roda sem interface visível (headless) e fixa o tamanho de renderização,
        # já que o site é responsivo e sem isso poderia carregar em layout mobile,
        # quebrando os seletores validados no layout desktop
        opcoes = Options()
        opcoes.add_argument("--lang=pt-BR")
        opcoes.add_experimental_option("prefs", {"intl.accept_languages": "pt-BR,pt"})

        if os.path.exists("/usr/bin/chromium"):
            opcoes.binary_location = "/usr/bin/chromium"
            opcoes.add_argument("--no-sandbox")
            opcoes.add_argument("--disable-dev-shm-usage")
            servico = Service("/usr/bin/chromedriver")
        else:
            servico = Service(ChromeDriverManager().install())

        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(service=servico, options=opcoes)
        
        driver.get("https://portal.gupy.io/job-search")

        ## 4. Execução para múltiplos cargos

        # Executa a busca para uma lista de cargos, juntando os resultados de todos em uma única lista.

        cargos = [
            "Estágio TI",
            "Analista de Dados Júnior",
            "Desenvolvedor Júnior",
            "Python Junior",
            "Analista de Sistema Júnior",
            "Analista de Suporte Júnior"
        ]

        logging.info(f"Buscando {len(cargos)} cargos: {', '.join(cargos)}")

        vagas_encontradas = []

        for cargo in cargos:
            # extend (e não append) porque cada chamada já devolve uma lista de vagas,
            # mantendo tudo em uma única lista de dicionários, sem aninhamento
            vagas_encontradas.extend(buscar_vagas(driver, cargo))

        ## 5. Organização e tratamento dos dados

        # Transforma os resultados em DataFrame e prepara os dados para envio à API.

        # Colunas esperadas no DataFrame
        colunas = [
            "Cargo Buscado",
            "Titulo",
            "Empresa",
            "Local",
            "Modelo",
            "Tipo da Vaga",
            "Afirmativa para PcD",
            "Data",
            "Link"
        ]

        # Transformar os resultados em DataFrame
        df_vagas = pd.DataFrame(vagas_encontradas, columns=colunas)

        if df_vagas.empty:
            logging.info("Nenhuma vaga foi encontrada nesta execução.")
        else:
            # Remove o texto fixo da data
            df_vagas["Data"] = df_vagas["Data"].str.replace("Publicada em:", "", regex=False).str.strip()

        # Converte para datetime
        # Datas ausentes ou inválidas serão convertidas para NaT
        df_vagas["Data"] = pd.to_datetime(df_vagas["Data"], format="%d/%m/%Y", errors="coerce")

        # Preenche os campos opcionais
        # Mantém a coluna Data como datetime
        colunas_nulos = [col for col in df_vagas.columns if col != "Data"]

        for coluna in colunas_nulos:
            df_vagas[coluna] = df_vagas[coluna].fillna("Não informado")
       
        df_api = df_vagas.rename(columns={
            "Cargo Buscado": "cargo_buscado",
            "Titulo": "titulo",
            "Empresa": "empresa",
            "Local": "localizacao",
            "Modelo": "modelo",
            "Tipo da Vaga": "tipo_vaga",
            "Afirmativa para PcD": "afirmativa_pcd",
            "Data": "data",
            "Link": "link"
        })

        df_api["data"] = df_api["data"].dt.strftime("%Y-%m-%d")

        MAX_TENTATIVAS_CONSECUTIVAS = 3
        vagas_novas_api = 0
        vagas_duplicadas = 0
        erros_validacao = 0
        erros_conexao = 0
        status_inesperados = 0
        erros_timeout = 0
        falhas_consecutivas = 0
        falhas_autenticacao = 0
        datas_invalidas = 0


        for index, dados_da_linha in df_api.iterrows():
            if pd.isna(dados_da_linha["data"]):
                datas_invalidas += 1
                logging.warning(f"Vaga ignorada por possuir data inválida: {dados_da_linha['titulo']} - {dados_da_linha['link']}")
                continue
            dados = {
                "cargo_buscado": dados_da_linha["cargo_buscado"],
                "titulo": dados_da_linha["titulo"],
                "empresa": dados_da_linha["empresa"],
                "localizacao": dados_da_linha["localizacao"],
                "modelo": dados_da_linha["modelo"],
                "tipo_vaga": dados_da_linha["tipo_vaga"],
                "afirmativa_pcd": dados_da_linha["afirmativa_pcd"],
                "data": dados_da_linha["data"],
                "link": dados_da_linha["link"],
            }

            try:
                requisicao = requests.post(API_URL, json=dados, timeout=(2, 15), headers=headers)
                falhas_consecutivas = 0
            except requests.exceptions.ConnectionError as e:
                erros_conexao += 1
                falhas_consecutivas += 1
                logging.error(f"Erro ao processar a linha {index} - {dados_da_linha['link']}: {e}")
                if falhas_consecutivas < MAX_TENTATIVAS_CONSECUTIVAS:                                      
                    continue
                else:
                    logging.warning("Limite de falhas consecutivas atingido. Envio de vagas para a API interrompido.")
                    break
            except requests.exceptions.ReadTimeout as e:
                logging.error(f"Erro de timeout na linha {index} - {dados_da_linha['link']}: {e}")
                erros_timeout += 1
                falhas_consecutivas += 1
                if falhas_consecutivas < MAX_TENTATIVAS_CONSECUTIVAS:                                      
                    continue
                else:
                    logging.warning("Limite de falhas consecutivas atingido. Envio de vagas para a API interrompido.")
                    break

            status = requisicao.status_code

            if status == 200:
                vagas_novas_api += 1
            elif status == 409:
                vagas_duplicadas += 1
                logging.info(f"Vaga duplicada: {dados_da_linha['link']}")
            elif status == 422:
                erros_validacao += 1
                logging.error(f"Erro de validação: {requisicao.json()}")
            elif status == 401:
                falhas_autenticacao += 1
                logging.error("Falha de autenticação na API")
                break
            else:
                logging.warning(f"Status inesperado ({status}) para o link {dados_da_linha['link']}: {requisicao.text}")
                status_inesperados += 1
            
        logging.info(f"Vagas coletadas nesta execução: {len(df_vagas)}")   
        logging.info(f"Vagas novas cadastradas pela API: {vagas_novas_api}")
        logging.info(f"Total de vagas duplicadas na API: {vagas_duplicadas}")
        logging.info(f"Total de erros de validação: {erros_validacao}")
        logging.info(f"Total de datas inválidas: {datas_invalidas}")
        logging.info(f"Total de erros de conexão: {erros_conexao}")
        logging.info(f"Total de status HTTP inesperados: {status_inesperados}")
        logging.info(f"Total de erros de timeout: {erros_timeout}")
        logging.info(f"Total de falhas de autenticação na API: {falhas_autenticacao}")

        contadores = [
            erros_validacao,
            erros_conexao,
            status_inesperados,
            erros_timeout,
            falhas_autenticacao,
            datas_invalidas
        ]

        if any(contadores):            

            assunto = "Monitoramento de vagas concluído com ocorrências!"
            corpo = f"""
                O monitoramento de vagas chegou ao final, porém foram registradas ocorrências durante a execução.
                Resumo da execução:
                Vagas coletadas nesta execução: {len(df_vagas)}
                Vagas novas cadastradas pela API: {vagas_novas_api}
                Vagas duplicadas na API: {vagas_duplicadas}
                Erros de conexão: {erros_conexao}
                Erros de validação: {erros_validacao}
                Datas inválidas: {datas_invalidas}
                Erros de timeout: {erros_timeout}
                Status HTTP inesperados: {status_inesperados}
                Falhas de autenticação: {falhas_autenticacao}
                O processamento principal foi concluído, mas recomenda-se consultar os logs da execução para mais detalhes.
            """
            corpo_html = f"""
                <html>
                    <body>
                        <h2>O monitoramento de vagas chegou ao final, porém foram registradas ocorrências durante a execução.</h2>
                        <p>Resumo da execução:</p>
                        <p>Vagas coletadas nesta execução: {len(df_vagas)}</p>
                        <p>Vagas novas cadastradas pela API: {vagas_novas_api}</p>
                        <p>Vagas duplicadas na API: {vagas_duplicadas}</p>
                        <p>Erros de conexão: {erros_conexao}</p>
                        <p>Erros de validação: {erros_validacao}</p>
                        <p>Datas inválidas: {datas_invalidas}</p>
                        <p>Erros de timeout: {erros_timeout}</p>
                        <p>Status HTTP inesperados: {status_inesperados}</p>
                        <p>Falhas de autenticação: {falhas_autenticacao}</p>
                        <strong>O processamento principal foi concluído, mas recomenda-se consultar os logs da execução para mais detalhes.</strong>
                    </body>
                </html>    
            """

            logging.warning("Execução Concluída com ocorrências")

        else:

            assunto = "Monitoramento de vagas concluído com sucesso!"
            corpo = f"""
                O monitoramento de vagas foi concluído com sucesso.
                Resumo da execução:
                Vagas coletadas nesta execução: {len(df_vagas)}
                Vagas novas cadastradas pela API: {vagas_novas_api}
                Vagas duplicadas na API: {vagas_duplicadas}
                Erros de conexão: {erros_conexao}
                Erros de validação: {erros_validacao}
                Datas inválidas: {datas_invalidas}
                Erros de timeout: {erros_timeout}
                Status HTTP inesperados: {status_inesperados}
                Falhas de autenticação: {falhas_autenticacao}
                A execução foi finalizada normalmente.
            """
            corpo_html = f"""
                <html>
                    <body>
                        <h2>O monitoramento de vagas foi concluído com sucesso.</h2>
                        <p>Resumo da execução:</p>
                        <p>Vagas coletadas nesta execução: {len(df_vagas)}</p>
                        <p>Vagas novas cadastradas pela API: {vagas_novas_api}</p>
                        <p>Vagas duplicadas na API: {vagas_duplicadas}</p>
                        <p>Erros de conexão: {erros_conexao}</p>
                        <p>Erros de validação: {erros_validacao}</p>
                        <p>Datas inválidas: {datas_invalidas}</p>
                        <p>Erros de timeout: {erros_timeout}</p>
                        <p>Status HTTP inesperados: {status_inesperados}</p>
                        <p>Falhas de autenticação: {falhas_autenticacao}</p>
                        <strong>A execução foi finalizada normalmente.</strong>
                    </body>
                </html>
            """

            logging.info("Execução finalizada com sucesso")

        enviar_email(
            destinatario=destinatario,
            assunto=assunto,
            corpo_email=corpo,
            corpo_email_html=corpo_html
        )

        logging.info("=" * 60)

    except Exception as e:
        logging.error(f"Execução falhou: {e}")

        assunto = "Falha no monitoramento de vagas"
        corpo = f"""
            A execução do monitoramento de vagas foi interrompida antes da conclusão.
            Motivo registrado: {e}
            Consulte o arquivo de log para obter mais detalhes sobre a falha.
        """
        corpo_html = f"""
            <html>
                <body>
                    <strong>A execução do monitoramento de vagas foi interrompida antes da conclusão.</strong>
                    <p>Motivo registrado: {e}</p>
                    <p>Consulte o arquivo de log para obter mais detalhes sobre a falha.</p>
                </body>
            </html>
        """

        enviar_email(
            destinatario=destinatario,
            assunto=assunto,
            corpo_email=corpo,
            corpo_email_html=corpo_html
        )
    
    finally:
        if driver is not None:
            driver.quit()
