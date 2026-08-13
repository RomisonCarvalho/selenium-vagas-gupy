# Automação de Busca de Vagas com Selenium

🚀 Núcleo funcional concluído — em fase de polimento

## Objetivo

Projeto de automação desenvolvido para pesquisar e coletar vagas de emprego publicadas na plataforma [Gupy](https://www.gupy.io/), filtrando por cargo/palavra-chave e organizando os resultados em um dataset estruturado.

O projeto nasceu de uma necessidade real: automatizar parte do processo de busca de vagas durante minha própria transição de carreira para a área de tecnologia.

## Tecnologias

- Python
- Selenium
- Pandas
- Jupyter Notebook

## Funcionalidades

- [x] Buscar vagas por cargo/palavra-chave no Gupy (via URL parametrizada, com filtro de localização)
- [x] Extrair informações de cada vaga (título, empresa, local, modelo de trabalho, tipo de vaga, afirmativa para PcD, data de publicação e link)
- [x] Coletar todas as vagas da página de resultados
- [x] Navegar automaticamente por todas as páginas de resultados (paginação)
- [x] Buscar múltiplos cargos numa única execução
- [x] Tratar erros de carregamento (timeout) e buscas sem nenhuma vaga encontrada
- [x] Organizar os dados em um DataFrame, tratar datas e valores nulos, e exportar para CSV
- [ ] (Futuro) Evitar duplicidade de vagas entre buscas por cargos diferentes
- [ ] (Futuro) Automatizar a execução periódica

## Status

O núcleo do projeto (busca, extração, paginação e exportação) está funcional e testado de ponta a ponta. Etapa atual: polimento — remoção de código não utilizado, revisão das esperas do navegador e organização final do notebook.

## Como rodar

_Em breve, assim que a estrutura final do notebook estiver definida._

## Autor

Rômison de Jesus Carvalho
