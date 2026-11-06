# Sistema Integrado de Captura e Triagem de Mídias (TCC)

Sistema híbrido de automação e triagem de mídias para Ordens de Serviço (OS), desenvolvido como Trabalho de Conclusão de Curso em Engenharia de Computação. 

A arquitetura integra um frontend móvel serverless (Google Apps Script) com compressão client-side a um motor backend robusto em Python. O projeto garante 100% de integridade estrutural no tráfego de arquivos através de validação criptográfica de ponta a ponta (SHA-256 via Web Crypto API e hashlib), além de implementar controle de concorrência com travas atômicas.

## Estrutura do Projeto
- `/backend`: Scripts em Python para rodar no servidor local da assistência técnica.
  - `main.py`: Motor central que valida hashes, padroniza nomes e roteia ficheiros.
  - `test_runner.py`: Testes automatizados (gabarito) de validação criptográfica e Regex.
  - `teste_carga.py`: Script de stress-test para simulação de carga pesada.
- `/frontend`: Códigos para colocar no editor web do Google Apps Script.
  - `Code.gs`: Middleware que recebe os ficheiros particionados e cria o arquivo sidecar (.sha256).
  - `index.html`: Interface visual móvel do técnico com cálculo de Hash client-side.

## Como usar
1. O técnico acede à interface HTML pelo telemóvel, insere o número da OS e tira a foto.
2. O sistema comprime (SSIM > 0.90) e envia o ficheiro juntamente com a assinatura SHA-256 (.sha256) para o Google Drive.
3. O servidor local, com o Google Drive Desktop sincronizado, executa o `main.py`.
4. O `main.py` valida o hash local contra o hash de origem e organiza automaticamente na pasta correspondente.
