Sistema Integrado de Captura e Triagem em Rede Local para Ordens de Serviço

Este repositório contém o código-fonte do Trabalho de Conclusão de Curso (TCC) em Engenharia de Computação. O sistema propõe uma arquitetura de rede local (on-premise) para automatizar a triagem, validação de integridade e roteamento de evidências multimídia (fotos e vídeos) em laboratórios de manutenção de hardware.

🎯 O Problema

Em laboratórios com alto volume de reparos, o tráfego e a alocação de evidências visuais (necessárias para resguardo jurídico e técnico) consomem horas operacionais. Métodos tradicionais (protocolo SMB via File Explorer) apresentam lentidão em redes sem fio, e transferências em massa frequentemente resultam em arquivos corrompidos ou salvos em pastas erradas.

🚀 A Solução (Arquitetura)

O sistema abandona o uso de pastas partilhadas legadas e plataformas de nuvem, adotando uma abordagem 100% local e assíncrona focada em desempenho e segurança Zero-Trust:

Frontend (Aplicação Web): Interface responsiva acedida via navegador móvel. Utiliza a biblioteca hash-wasm (via WebAssembly) para calcular progressivamente o hash SHA-256 do arquivo no dispositivo do técnico antes do envio.

Receptor Node.js (Servidor Local): Recebe as mídias via requisições HTTP e roteia os pacotes (streams) diretamente para o disco rígido, eliminando o consumo excessivo de memória RAM e burlando limites tradicionais de timeout.

Validador e Motor Python: Motor de retaguarda que utiliza travas atômicas a nível de sistema operacional (os.mkdir) para evitar concorrência. Valida a integridade criptográfica recalculando o hash, corrige framerates de vídeos via FFMPEG e realiza o roteamento final para as pastas das Ordens de Serviço.

🛡️ Principais Funcionalidades

Criptografia de Ponta a Ponta: Deteção de corrupção (bit-flip) com isolamento automático de mídias comprometidas (Quarentena).

Stream Contínuo: Capacidade de transferir vídeos pesados (Ex: 2GB+) sem travar o navegador cliente.

Mutex Atômico: Imunidade a condições de corrida (race conditions) e deadlocks.

Otimização de Vídeo: Conversão automática de vídeos acima de 30fps utilizando FFMPEG.

⚙️ Como Instalar e Executar (Para a Banca Avaliadora)

Pré-requisitos

Node.js instalado.

Python 3.x instalado.

FFMPEG instalado e configurado nas variáveis de ambiente do Windows.

1. Preparando o Servidor Node.js

No terminal, navegue até à pasta raiz do projeto e instale o framework Express:

npm install express


Inicie o servidor receptor (ele escutará na porta 8081):

node servidor.js


2. Iniciando o Motor Python

Abra uma nova janela de terminal na mesma pasta e inicie o motor de validação e roteamento:

python main.py


3. Acedendo pelo Dispositivo Móvel

Descubra o IP local do servidor (Ex: 192.168.1.15).

Conecte o smartphone na mesma rede Wi-Fi.

Abra o navegador (Recomenda-se utilizar "Guia Anônima" para evitar cache) e aceda: http://SEU_IP:8081

Preencha o número da OS e inicie a captura das mídias. O processo de validação ocorrerá em tempo real nos terminais do Node.js e Python.

📚 Autoria e Licença

Desenvolvido por Vitor Guilherme Lobo de Almeida como requisito para a obtenção do título de Bacharel em Engenharia de Computação pelo Centro Universitário Jorge Amado (UJ).