# Automação de Busca de Vagas com Selenium

✅ Projeto concluído — em polimento final

## Objetivo

Projeto de automação desenvolvido para pesquisar e coletar vagas de emprego publicadas na plataforma [Gupy](https://www.gupy.io/), filtrando por cargo/palavra-chave e organizando os resultados em um dataset estruturado.

O projeto nasceu de uma necessidade real: automatizar parte do processo de busca de vagas durante minha própria transição de carreira para a área de tecnologia. O script busca vagas remotas para os cargos de interesse e roda automaticamente uma vez por semana, acumulando os resultados ao longo do tempo.

## Tecnologias

- Python
- Selenium
- Pandas
- Jupyter Notebook (prototipagem) + script `.py` (execução automática)
- `pathlib`, `logging` (bibliotecas padrão do Python)

## Funcionalidades

- [x] Buscar vagas por cargo/palavra-chave no Gupy (via URL parametrizada)
- [x] Filtrar apenas vagas com modelo de trabalho remoto
- [x] Extrair informações de cada vaga (título, empresa, local, modelo de trabalho, tipo de vaga, afirmativa para PcD, data de publicação e link)
- [x] Coletar todas as vagas da página de resultados
- [x] Navegar automaticamente por todas as páginas de resultado (paginação)
- [x] Buscar múltiplos cargos numa única execução
- [x] Tratar erros de carregamento (timeout) e buscas sem nenhuma vaga encontrada
- [x] Organizar os dados em um DataFrame, tratar datas e valores nulos
- [x] Acumular resultados entre execuções, evitando duplicidade de vagas (deduplicação pelo link)
- [x] Exportar os dados para CSV
- [x] Executar automaticamente de forma periódica (Agendador de Tarefas do Windows, semanal)
- [x] Registrar cada execução em arquivo de log, com data/hora
- [x] Rodar em modo headless (sem interface gráfica do navegador)

## Como rodar

1. Clone o repositório e crie um ambiente virtual (opcional, mas recomendado)
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Execute o script:
   ```
   python projeto_vagas_gupy.py
   ```
   As pastas `reports/` (dados) e `logs/` (execuções) são criadas automaticamente, caso não existam.
4. Para rodar automaticamente todo período, configure uma tarefa agendada (por exemplo, o Agendador de Tarefas do Windows) apontando para o `python.exe` do seu ambiente e passando o caminho completo do script como argumento.

## Status

Todas as funcionalidades planejadas foram implementadas e testadas. Etapa atual: revisão final do código e organização do repositório.

## Autor

Rômison de Jesus Carvalho
