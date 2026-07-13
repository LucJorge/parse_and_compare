# HAR Runner

Este projeto implementa um runner manual de HAR que:

- carrega um arquivo HAR;
- seleciona um único request;
- executa o request contra um backend Aspire local;
- compara a resposta real com a resposta armazenada no HAR;
- gera um relatório de validação.

## Arquitetura

- `main.py`
  - orquestra o fluxo principal
  - lê configuração e branch Git
  - carrega o HAR
  - permite a seleção manual de uma entrada
  - dispara o request local
  - compara resultados e salva relatório

- `har_extractor.py`
  - lê e parseia o arquivo HAR
  - extrai método, path, query, headers e body
  - fornece seleção de entrada manual

- `request_runner.py`
  - monta a URL local do Aspire
  - preserva path, query string, body e método HTTP
  - envia o request ao backend local
  - suporta espera opcional pelo backend

- `response_comparator.py`
  - compara status, headers relevantes e corpo
  - ignora headers voláteis como `Date`, `Server`, `Content-Length` e IDs de correlação
  - compara JSON estruturalmente quando possível
  - gera diff legível para divergências

- `reporter.py`
  - constrói e persiste o relatório final
  - documenta branch, HAR usado, endpoint, status esperado/obtido e diff

- `config.py`
  - gerencia persistência do caminho do projeto PPL Core Platform

## Fluxo de execução

1. Coloque um arquivo HAR em `Compare/hars/`.
2. Execute `python main.py` dentro de `Compare/`.
3. Informe o nome do arquivo HAR.
4. Selecione a entrada que deseja testar.
5. Informe a URL local do Aspire (por exemplo `http://localhost:5046`).
6. O runner espera o backend, executa o request, compara a resposta e salva o relatório em `Compare/reports/`.

## Resultado esperado

- se o status, headers relevantes e corpo coincidirem, o relatório marca `Ready for Testing`;
- se houver divergências relevantes, o relatório marca `Code Review Needed`.

## Observações

- o HAR é a fonte principal de verdade para o request;
- o host do request é substituído apenas pela URL local do Aspire;
- path, query string e body permanecem inalterados.

