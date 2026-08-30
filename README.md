# Automação de Busca de Vagas com Selenium

Projeto de automação desenvolvido em Python com Selenium para pesquisar e coletar vagas de emprego publicadas na plataforma [Gupy](https://www.gupy.io/), filtrando por cargo/palavra-chave e pelo modelo de trabalho remoto.

O projeto nasceu de uma necessidade real: automatizar parte do processo de busca de vagas durante minha transição de carreira para a área de tecnologia. A automação coleta as vagas encontradas, organiza os dados em um DataFrame, mantém um histórico em CSV, envia as vagas coletadas para uma API por meio de requisições HTTP e notifica por e-mail o status final de cada execução.

## Objetivo

Automatizar a busca de oportunidades de emprego no Gupy para diferentes cargos de interesse, priorizando vagas com modelo de trabalho remoto, mantendo um histórico local das oportunidades encontradas, integrando a automação a uma API responsável pela persistência dos dados e enviando notificações por e-mail com o resumo da execução.

## Arquitetura atual

```text
Gupy
  ↓
Selenium
  ↓
Pandas / tratamento dos dados
  ├──→ Histórico em CSV
  ├──→ Requisições HTTP
  │       ↓
  │     API FastAPI
  │       ↓
  │     Banco de dados
  └──→ Notificação por e-mail
          ↓
        SMTP com TLS
```

O CSV continua sendo mantido como histórico local da automação, enquanto a integração HTTP permite que as vagas da execução atual sejam encaminhadas para a API. Ao final do processamento, uma notificação por e-mail informa se a execução terminou com sucesso, com ocorrências ou com falha.

## Tecnologias

- Python
- Selenium
- Pandas
- Requests
- WebDriver Manager
- python-dotenv
- FastAPI (API externa integrada ao projeto)
- SMTP com TLS para envio das notificações
- Jupyter Notebook (utilizado durante a prototipagem)
- `pathlib`, `logging`, `os`, `smtplib` e `email` (bibliotecas padrão do Python)

## Funcionalidades

- [X] Buscar vagas por cargo/palavra-chave no Gupy por meio de URL parametrizada
- [X] Filtrar apenas vagas com modelo de trabalho remoto
- [X] Buscar múltiplos cargos em uma única execução
- [X] Extrair informações das vagas:
  - Cargo pesquisado
  - Título
  - Empresa
  - Local
  - Modelo de trabalho
  - Tipo da vaga
  - Afirmativa para PcD
  - Data de publicação
  - Link
- [X] Navegar automaticamente por todas as páginas de resultados
- [X] Utilizar esperas explícitas com `WebDriverWait`
- [X] Tratar timeouts e buscas sem resultados
- [X] Tratar valores ausentes e datas inválidas sem interromper a execução
- [X] Organizar os resultados em um DataFrame
- [X] Acumular resultados entre diferentes execuções
- [X] Remover vagas duplicadas no CSV utilizando o link como identificador
- [X] Exportar os resultados para CSV
- [X] Enviar as vagas da execução atual para uma API via HTTP
- [X] Tratar respostas HTTP de vaga cadastrada, duplicidade, erro de validação e status inesperados
- [X] Configurar timeout para as requisições HTTP
- [X] Interromper os envios para a API após o limite de falhas consecutivas
- [X] Registrar as execuções e ocorrências em arquivo de log
- [X] Diferenciar execução concluída com sucesso, concluída com ocorrências e execução com falha
- [X] Enviar uma notificação por e-mail conforme o status final da execução
- [X] Incluir no mesmo e-mail uma versão em texto simples e uma alternativa em HTML
- [X] Proteger as credenciais de e-mail por meio de variáveis de ambiente
- [X] Executar o navegador em modo headless
- [X] Fechar o navegador com segurança utilizando `try/finally`
- [X] Permitir execução periódica pelo Agendador de Tarefas do Windows

## Cargos pesquisados

Atualmente, a automação pesquisa os seguintes cargos:

- Estágio TI
- Analista de Dados Júnior
- Desenvolvedor Júnior
- Python Junior
- Analista de Sistema Júnior
- Analista de Suporte Júnior

Os cargos podem ser alterados diretamente na lista `cargos` do script.

## Dados coletados

Os resultados são armazenados nas seguintes colunas:

| Coluna | Descrição |
| --- | --- |
| `Cargo Buscado` | Termo utilizado na busca |
| `Titulo` | Título da vaga |
| `Empresa` | Empresa responsável pela vaga |
| `Local` | Localização informada pela vaga |
| `Modelo` | Modelo de trabalho |
| `Tipo da Vaga` | Tipo de contratação/oportunidade |
| `Afirmativa para PcD` | Indicação de vaga também destinada a PcD |
| `Data` | Data de publicação da vaga |
| `Link` | Link da vaga no Gupy |

## Organização dos dados

As vagas encontradas durante cada execução são transformadas em um DataFrame e comparadas com o histórico existente no arquivo CSV.

A automação utiliza o `Link` como identificador único para evitar que a mesma vaga seja armazenada mais de uma vez no histórico local.

A quantidade de vagas novas é calculada após a deduplicação, permitindo identificar quantas oportunidades foram realmente adicionadas ao CSV naquela execução.

Para a integração com a API, somente as vagas coletadas na execução atual são enviadas. A API realiza sua própria validação e controle de duplicidade.

## Integração com a API

A automação utiliza a biblioteca `requests` para enviar cada vaga coletada para o endpoint configurado no script.

As respostas são tratadas de acordo com o status HTTP retornado:

- `200`: vaga cadastrada com sucesso;
- `409`: vaga já cadastrada;
- `422`: erro de validação dos dados enviados;
- outros status: registrados como status HTTP inesperados.

Também são tratados erros de conexão e timeout. Após atingir o limite configurado de falhas consecutivas, somente o envio para a API é interrompido; o restante da automação continua normalmente.

## Notificações por e-mail

Ao final da execução, a automação envia uma notificação com o resultado do monitoramento. A mensagem reúne duas representações do mesmo conteúdo:

- texto simples, utilizado como fallback por clientes que não exibem HTML;
- HTML, utilizado como versão formatada pelos clientes compatíveis.

As duas versões fazem parte de um único e-mail. O envio utiliza o servidor SMTP do Gmail na porta `587`, com autenticação e conexão protegida por TLS.

As credenciais e o destinatário não ficam gravados no código. Eles são carregados do arquivo `.env` pela biblioteca `python-dotenv`, a partir das seguintes variáveis:

```env
EMAIL_REMETENTE=
EMAIL_SENHA_APP=
EMAIL_DESTINATARIO=
```

O repositório fornece o arquivo `.env.example` como modelo, sem credenciais reais. O arquivo `.env` local deve permanecer fora do versionamento.

As notificações representam três estados:

- **Execução finalizada com sucesso:** apresenta o resumo da execução sem ocorrências registradas na integração;
- **Execução concluída com ocorrências:** apresenta os contadores de erros tratados e recomenda consultar o log;
- **Execução falhou:** informa que o fluxo principal foi interrompido, registra o motivo disponível e recomenda consultar o log.

## Logs e estabilidade

O projeto registra as execuções em arquivo de log, incluindo:

- início da execução;
- cargos pesquisados;
- timeouts e ocorrências durante a coleta;
- erros de conexão com a API;
- erros de validação;
- status HTTP inesperados;
- quantidade de vagas novas;
- quantidade de vagas cadastradas e duplicadas na API;
- total acumulado de vagas no CSV;
- resultado do envio da notificação por e-mail;
- status final da execução.

O status final pode ser:

- **Execução finalizada com sucesso:** o fluxo principal chegou ao fim sem ocorrências registradas na integração;
- **Execução concluída com ocorrências:** o fluxo chegou ao fim, mas houve problemas tratados durante o processamento;
- **Execução falhou:** uma exceção não tratada interrompeu o fluxo principal antes da conclusão.

> Observação: o tratamento de timeout ocorrido dentro da função de busca do Selenium ainda será refinado para participar também da classificação do status final da execução.

## Estrutura de saída

O projeto cria automaticamente as pastas de armazenamento quando necessário:

```text
reports/
└── vagas_encontradas.csv

logs/
└── execucao.log
```

O arquivo CSV mantém o histórico acumulado das vagas encontradas.

O arquivo de log registra as execuções com data e hora e o resumo de cada processamento.

## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/RomisonCarvalho/selenium-vagas-gupy.git
```

Entre na pasta do projeto:

```bash
cd selenium-vagas-gupy
```

### 2. Crie um ambiente virtual

Opcional, mas recomendado:

```bash
python -m venv venv
```

Ative o ambiente virtual no Windows:

```bash
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

A dependência `python-dotenv` é responsável por carregar as configurações de e-mail do arquivo `.env`.

### 4. Configure as variáveis de ambiente

Crie uma cópia do arquivo `.env.example` com o nome `.env`:

```powershell
Copy-Item .env.example .env
```

Depois, preencha o arquivo `.env`:

```env
EMAIL_REMETENTE=seu_email@gmail.com
EMAIL_SENHA_APP=sua_senha_de_app
EMAIL_DESTINATARIO=email_que_recebera_as_notificacoes
```

Como o envio utiliza o SMTP do Gmail, `EMAIL_SENHA_APP` deve receber uma senha de app da conta remetente, e não a senha comum da conta. Não versione o arquivo `.env` nem compartilhe suas credenciais.

### 5. Execute a API

Para utilizar a integração HTTP completa, a API configurada no script deve estar em execução e acessível.

Caso a API esteja indisponível, a automação mantém o processamento local, registra as falhas, interrompe novas tentativas de envio após atingir o limite configurado e informa as ocorrências na notificação final.

### 6. Execute a automação

```bash
python projeto_vagas_gupy.py
```

As pastas `reports/` e `logs/` serão criadas automaticamente caso não existam. Ao final do processamento, a automação tentará enviar a notificação para o endereço definido em `EMAIL_DESTINATARIO`.

## Execução automática

A automação pode ser configurada para execução periódica utilizando o **Agendador de Tarefas do Windows**.

A tarefa deve apontar para o executável `python.exe` do ambiente utilizado e passar o caminho completo do arquivo `projeto_vagas_gupy.py` como argumento.

No meu ambiente, a execução foi configurada para ocorrer semanalmente.

## Status

🚧 Projeto em evolução.

A versão original da automação já realiza busca, coleta, tratamento, histórico em CSV e execução agendada. A evolução atual adiciona integração HTTP com uma API, tratamento de falhas de comunicação e notificações por e-mail com resumo operacional, mantendo a proposta de transformar o projeto em uma solução de monitoramento de vagas mais completa.

## Autor

**Rômison de Jesus Carvalho**
