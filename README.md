# Automação de Busca de Vagas com Selenium

Projeto de automação desenvolvido em Python com Selenium para pesquisar e coletar vagas de emprego publicadas na plataforma [Gupy](https://www.gupy.io/), filtrando por cargo/palavra-chave e pelo modelo de trabalho remoto.

O projeto nasceu de uma necessidade real: automatizar parte do processo de busca de vagas durante minha transição de carreira para a área de tecnologia. A automação coleta as vagas, organiza e trata os dados com Pandas, envia os resultados para uma API hospedada em nuvem e notifica por e-mail o status final de cada execução.

A versão atual é executada de forma automatizada em container no Google Cloud Run Jobs, com disparos programados pelo Cloud Scheduler. A API integrada é a fonte de verdade para persistência e controle de duplicidade das vagas.

## Objetivo

Automatizar a busca de oportunidades de emprego no Gupy para diferentes cargos de interesse, priorizando vagas remotas e mantendo o processo independente da execução manual no computador local.

Além da coleta, o projeto busca praticar conceitos de automação web, tratamento de dados, integração via API, autenticação, containers, execução agendada em nuvem, gerenciamento de secrets, logs e notificações.

## Arquitetura atual

```text
Cloud Scheduler
      ↓
Cloud Run Job
(Docker + Python + Selenium + Chromium)
      ↓
     Gupy
      ↓
Pandas / tratamento dos dados
      ├──→ HTTPS + X-API-Key
      │          ↓
      │       FastAPI
      │          ↓
      │   Cloud Run Service
      │          ↓
      │    Neon PostgreSQL
      │
      └──→ Gmail SMTP + TLS
                 ↓
          Notificação por e-mail
```

Serviços de apoio utilizados na infraestrutura:

```text
Artifact Registry → armazena a imagem Docker da automação
Secret Manager    → disponibiliza secrets ao Cloud Run Job
Cloud Logging     → captura os logs enviados para stdout/stderr
```

A automação pode continuar sendo executada localmente para desenvolvimento e testes, mas a execução de produção não depende do computador do usuário.

## Tecnologias

- Python
- Selenium
- Chromium / Google Chrome
- Pandas
- Requests
- WebDriver Manager
- python-dotenv
- Docker
- FastAPI (API externa integrada ao projeto)
- Google Cloud Run Jobs
- Google Cloud Run
- Google Cloud Scheduler
- Google Artifact Registry
- Google Secret Manager
- Google Cloud Logging
- Neon PostgreSQL
- SMTP com TLS para envio das notificações
- Git e GitHub

## Funcionalidades

- [X] Buscar vagas por cargo/palavra-chave no Gupy por URL parametrizada
- [X] Filtrar vagas pelo modelo de trabalho remoto
- [X] Buscar múltiplos cargos em uma única execução
- [X] Extrair cargo pesquisado, título, empresa, local, modelo, tipo da vaga, indicação PcD, data e link
- [X] Navegar automaticamente pelas páginas de resultados
- [X] Utilizar esperas explícitas com `WebDriverWait`
- [X] Tratar buscas sem resultados e timeouts durante a coleta
- [X] Tratar o banner de cookies para evitar interceptação dos controles de paginação
- [X] Organizar os resultados em um DataFrame
- [X] Converter datas para o formato esperado pela API
- [X] Preencher somente campos opcionais ausentes com `Não informado`
- [X] Ignorar vagas com data inválida sem derrubar toda a execução
- [X] Enviar as vagas coletadas para uma API via HTTP
- [X] Autenticar requisições utilizando o header `X-API-Key`
- [X] Tratar cadastro, duplicidade, validação, autenticação e status HTTP inesperados
- [X] Configurar timeout nas requisições HTTP
- [X] Interromper o envio para a API após um limite de falhas consecutivas
- [X] Persistir as vagas remotamente em PostgreSQL por meio da API
- [X] Diferenciar execução concluída com sucesso, concluída com ocorrências e execução com falha
- [X] Enviar notificação por e-mail em texto simples e HTML
- [X] Registrar falha no envio da notificação sem invalidar um processamento principal já concluído
- [X] Relançar falhas do fluxo principal para preservar o status correto da execução no Cloud Run
- [X] Executar o navegador em modo headless
- [X] Executar em ambiente local Windows ou em container Linux
- [X] Forçar o navegador para `pt-BR` para manter consistência nos textos tratados
- [X] Encerrar o navegador com segurança utilizando `try/finally`
- [X] Registrar logs em stdout/stderr para captura pelo Cloud Logging
- [X] Empacotar a automação em imagem Docker
- [X] Executar a automação no Google Cloud Run Jobs
- [X] Agendar execuções com Google Cloud Scheduler
- [X] Utilizar Secret Manager para credenciais sensíveis em produção

## Cargos pesquisados

Atualmente, a automação pesquisa:

- Estágio TI
- Analista de Dados Júnior
- Desenvolvedor Júnior
- Python Junior
- Analista de Sistema Júnior
- Analista de Suporte Júnior

Os cargos podem ser alterados diretamente na lista `cargos` do script.

## Dados coletados

| Campo                   | Descrição                                 |
| ----------------------- | ------------------------------------------- |
| `Cargo Buscado`       | Termo utilizado na pesquisa                 |
| `Titulo`              | Título da vaga                             |
| `Empresa`             | Empresa responsável pela vaga              |
| `Local`               | Localização informada                     |
| `Modelo`              | Modelo de trabalho                          |
| `Tipo da Vaga`        | Tipo de contratação/oportunidade          |
| `Afirmativa para PcD` | Indicação de vaga também destinada a PcD |
| `Data`                | Data de publicação                        |
| `Link`                | Link da vaga no Gupy                        |

Os campos `Local`, `Modelo`, `Tipo da Vaga` e `Afirmativa para PcD` são opcionais e recebem `Não informado` quando ausentes.

A data é convertida para o formato ISO `YYYY-MM-DD` antes do envio. Caso uma vaga não possua uma data válida, ela é ignorada e a ocorrência é registrada nos logs.

## Organização e persistência dos dados

As vagas encontradas em cada execução são organizadas em um DataFrame e preparadas para o esquema esperado pela API.

A versão atual não mantém mais um histórico local em CSV. Essa estratégia foi utilizada nas primeiras versões do projeto, mas foi removida após a API e o PostgreSQL passarem a assumir a persistência dos dados.

Cada vaga da execução atual é enviada para a API. O backend utiliza o link da vaga para controlar duplicidades e mantém o banco de dados como fonte de verdade da aplicação.

## Integração com a API

A biblioteca `requests` é utilizada para enviar cada vaga ao endpoint definido na variável de ambiente `API_URL`.

As requisições incluem:

```http
X-API-Key: <chave_da_api>
```

A chave é obtida da variável de ambiente `API_KEY` e não fica gravada diretamente no código.

Os principais retornos tratados são:

- `200`: vaga cadastrada com sucesso;
- `401`: falha de autenticação; novos envios são interrompidos;
- `409`: vaga já cadastrada;
- `422`: erro de validação;
- outros status: registrados como resposta HTTP inesperada.

Erros de conexão e `ReadTimeout` também são tratados. Após o limite configurado de falhas consecutivas, o envio de novas vagas para a API é interrompido para evitar tentativas desnecessárias.

A API utilizada em produção é executada no Google Cloud Run e persiste as vagas em PostgreSQL hospedado no Neon.

## Notificações por e-mail

Ao final do processamento, a automação tenta enviar uma notificação pelo SMTP do Gmail na porta `587`, utilizando TLS.

Cada mensagem possui uma versão em texto simples e uma alternativa em HTML.

Os principais estados informados são:

- **Execução finalizada com sucesso:** processamento concluído sem ocorrências contabilizadas;
- **Execução concluída com ocorrências:** processamento chegou ao final, mas houve erros tratados;
- **Execução falhou:** uma exceção interrompeu o fluxo principal.

Se o processamento principal terminar corretamente, mas a notificação por e-mail falhar, a falha do e-mail é registrada em log sem transformar o Job inteiro em falha.

Em caso de falha no fluxo principal, a automação envia a notificação possível e relança a exceção para que o ambiente de execução registre o Job como falho.

## Logs e estabilidade

Os logs são enviados para a saída padrão da aplicação.

Na execução local, eles podem ser acompanhados diretamente no terminal. No Cloud Run Jobs, stdout e stderr são capturados pelo Google Cloud Logging.

Entre as informações registradas estão:

- início e fim da execução;
- cargos pesquisados;
- ocorrências durante a coleta;
- tratamento do banner de cookies;
- vagas duplicadas;
- vagas novas cadastradas pela API;
- datas inválidas;
- erros de conexão e timeout HTTP;
- erros de validação;
- falhas de autenticação;
- status HTTP inesperados;
- resultado do envio de e-mail;
- falhas não tratadas do fluxo principal.

Timeouts ocorridos durante determinadas buscas no Gupy são registrados como warnings e, nesta versão, não alteram sozinhos o status final da execução.

## Execução local

### 1. Clone o repositório

```bash
git clone https://github.com/RomisonCarvalho/selenium-vagas-gupy.git
cd selenium-vagas-gupy
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
```

No Windows:

```powershell
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie uma cópia do `.env.example`:

```powershell
Copy-Item .env.example .env
```

Preencha o `.env` sem versionar credenciais reais:

```env
EMAIL_REMETENTE=seu_email@gmail.com
EMAIL_SENHA_APP=sua_senha_de_app
EMAIL_DESTINATARIO=email_que_recebera_as_notificacoes

API_URL=https://seu-servico.run.app/vagas/
API_KEY=sua_chave_da_api
```

`EMAIL_SENHA_APP` deve receber uma senha de app válida da conta Gmail utilizada no envio.

### 5. Execute

```bash
python projeto_vagas_gupy.py
```

A API configurada em `API_URL` precisa estar acessível. Ela pode estar em execução local ou hospedada em nuvem.

## Execução com Docker

A imagem utiliza Python 3.12 Slim, Chromium e ChromeDriver.

Para construir a imagem localmente:

```bash
docker build -t selenium-vagas-gupy:local .
```

Para executar utilizando as variáveis do arquivo `.env` sem incorporá-las à imagem:

```bash
docker run --rm --env-file .env selenium-vagas-gupy:local
```

O `.dockerignore` impede que arquivos sensíveis, ambientes virtuais, caches e artefatos locais sejam enviados para o contexto final da imagem.

## Execução em nuvem

Na versão atual, a imagem Docker é armazenada no Google Artifact Registry e utilizada por um Cloud Run Job.

O Job utiliza Chromium em modo headless e foi configurado com memória suficiente para manter o navegador estável durante a execução.

As credenciais sensíveis são fornecidas ao container por meio do Google Secret Manager, enquanto configurações não sensíveis podem ser definidas como variáveis de ambiente do Job.

A automação é disparada pelo Google Cloud Scheduler:

```text
Segunda-feira às 12:00
Quinta-feira às 12:00
Fuso: America/Sao_Paulo
```

Expressão cron:

```text
0 12 * * 1,4
```

Assim, a execução de produção não depende do computador local permanecer ligado.

## Evolução do projeto

O projeto começou como uma automação local executada no Windows, com persistência em CSV e agendamento pelo Agendador de Tarefas.

Com a evolução do projeto:

```text
CSV local
    ↓
API FastAPI
    ↓
PostgreSQL no Neon
    ↓
API no Cloud Run
    ↓
Automação em Docker
    ↓
Cloud Run Jobs
    ↓
Cloud Scheduler
```

A persistência local em CSV e os arquivos locais de log deixaram de ser necessários. A API passou a centralizar os dados e o Cloud Logging passou a concentrar os registros das execuções em nuvem.

Essa evolução foi mantida em dois repositórios separados: um dedicado à automação Selenium e outro dedicado à API.

## Estrutura principal

```text
selenium-vagas-gupy/
├── projeto_vagas_gupy.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
├── .gitignore
├── .gitattributes
└── README.md
```

## Status

✅ **Versão atual concluída e executando em produção na nuvem.**

O fluxo principal está containerizado, integrado à API, protegido por autenticação, executado pelo Cloud Run Jobs e agendado pelo Cloud Scheduler.

Possíveis evoluções futuras incluem testes automatizados, CI/CD e mecanismos de acompanhamento do ciclo de vida das vagas.

## Autor

**Rômison de Jesus Carvalho**
