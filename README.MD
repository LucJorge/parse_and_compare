# HAR Extractor

1. Na primeira execução, pede a pasta do projeto PLL Core Platform e guarda esse caminho em config.json.
2. Detecta a branch atual do PLL Core Platform.
3. Pede o nome do ficheiro .har que está na pasta `hars`.
4. Extrai as entradas para a pasta `processed_hars`

Como usar:
- Coloca o ficheiro .har na pasta do script.
- Executa: python main.py
- Insere o nome do ficheiro todo: xyz.har
- Outputs salvos na pasta xyz dentro de`processed_hars`

