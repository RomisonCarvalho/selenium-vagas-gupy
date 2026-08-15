# Automação de Busca de Vagas com Selenium

Projeto de automação desenvolvido em Python com Selenium para pesquisar e coletar vagas de emprego publicadas na plataforma [Gupy](https://www.gupy.io/), filtrando por cargo/palavra-chave e pelo modelo de trabalho remoto.

O projeto nasceu de uma necessidade real: automatizar parte do processo de busca de vagas durante minha transição de carreira para a área de tecnologia. A automação coleta as vagas encontradas, organiza os dados em um DataFrame, mantém um histórico em CSV e pode ser executada periodicamente pelo Agendador de Tarefas do Windows.

## Objetivo

Automatizar a busca de oportunidades de emprego no Gupy para diferentes cargos de interesse, priorizando vagas com modelo de trabalho remoto e mantendo um histórico das oportunidades encontradas ao longo das execuções.

## Tecnologias

- Python
- Selenium
- Pandas
- WebDriver Manager
- Jupyter Notebook (utilizado durante a prototipagem)
- `pathlib` e `logging` (bibliotecas padrão do Python)

## Funcionalidades

- [x] Buscar vagas por cargo/palavra-chave no Gupy por meio de URL parametrizada
- [x] Filtrar apenas vagas com modelo de trabalho remoto
- [x] Buscar múltiplos cargos em uma única execução
- [x] Extrair informações das vagas:
  - Cargo pesquisado
  - Título
  - Empresa
  - Local
  - Modelo de trabalho
  - Tipo da vaga
  - Afirmativa para PcD
  - Data de publicação
  - Link
- [x] Navegar automaticamente por todas as páginas de resultados
- [x] Utilizar esperas explícitas com `WebDriverWait`
- [x] Tratar timeouts e buscas sem resultados
- [x] Tratar valores ausentes e datas inválidas sem interromper a execução
- [x] Organizar os resultados em um DataFrame
- [x] Acumular resultados entre diferentes execuções
- [x] Remover vagas duplicadas utilizando o link como identificador
- [x] Exportar os resultados para CSV
- [x] Registrar as execuções em arquivo de log
- [x] Executar o navegador em modo headless
- [x] Fechar o navegador com segurança utilizando `try/finally`
- [x] Permitir execução periódica pelo Agendador de Tarefas do Windows

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
|---|---|
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

A automação utiliza o `Link` como identificador único para evitar que a mesma vaga seja armazenada mais de uma vez.

A quantidade de vagas novas é calculada após a deduplicação, permitindo identificar quantas oportunidades foram realmente adicionadas ao histórico naquela execução.

## Estrutura de saída

O projeto cria automaticamente as pastas de armazenamento quando necessário:

```text
reports/
└── vagas_encontradas.csv

logs/
└── execucao.log
```

O arquivo CSV mantém o histórico acumulado das vagas encontradas.

O arquivo de log registra as execuções com data e hora, incluindo informações como início da execução, quantidade de cargos pesquisados, vagas novas e total acumulado.

## Como executar

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
```

Entre na pasta do projeto:

```bash
cd <PASTA_DO_PROJETO>
```

### 2. Crie um ambiente virtual

Opcional, mas recomendado:

```bash
python -m venv venv
```

Ative o ambiente virtual no Windows:

```bash
venv\\Scripts\\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o script

```bash
python projeto_vagas_gupy.py
```

As pastas `reports/` e `logs/` serão criadas automaticamente caso não existam.

## Execução automática

A automação pode ser configurada para execução periódica utilizando o **Agendador de Tarefas do Windows**.

A tarefa deve apontar para o executável `python.exe` do ambiente utilizado e passar o caminho completo do arquivo `projeto_vagas_gupy.py` como argumento.

No meu ambiente, a execução foi configurada para ocorrer semanalmente.

## Tratamento de exceções e estabilidade

O projeto utiliza recursos do Selenium para tornar a automação mais resistente a variações no carregamento das páginas, incluindo:

- `WebDriverWait` para aguardar elementos necessários;
- `staleness_of` para confirmar a atualização da página após a paginação;
- tratamento de `TimeoutException`;
- tratamento de `NoSuchElementException`;
- conversão de datas com `errors="coerce"` para evitar interrupções causadas por valores inválidos;
- `try/finally` para garantir o encerramento do navegador.

## Status

✅ Projeto concluído e testado.

O projeto foi desenvolvido como prática de automação web, manipulação de dados e construção de uma solução aplicada a uma necessidade real de busca de oportunidades profissionais.

## Autor

**Rômison de Jesus Carvalho**
