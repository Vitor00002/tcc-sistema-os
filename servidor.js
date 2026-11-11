const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 8081;
const PASTA_RECEPCAO = "C:\\Users\\vitor_dfz2to2\\Documents\\fotos";

// TOKEN DE SEGURANÇA (Pre-Shared Key)
const TOKEN_LAB = "TCC-Sec-Auth-2026";

if (!fs.existsSync(PASTA_RECEPCAO)) {
    fs.mkdirSync(PASTA_RECEPCAO, { recursive: true });
}

app.use(express.static(path.join(__dirname, 'public')));

app.post('/upload-binario', (req, res) => {
    // 1. VALIDAÇÃO DE AUTENTICAÇÃO (Bearer Token)
    const authHeader = req.headers['authorization'];
    if (!authHeader || authHeader !== `Bearer ${TOKEN_LAB}`) {
        console.warn(`[!] Tentativa de acesso bloqueada (IP: ${req.ip})`);
        return res.status(401).send("Acesso Negado: Dispositivo não autorizado.");
    }

    const rawFileName = req.headers['x-file-name'];
    const fileHash = req.headers['x-file-hash'];

    if (!rawFileName) {
        return res.status(400).send("Cabeçalho ausente.");
    }

    let nomeDecodificado = decodeURIComponent(rawFileName);
    let nomeSeguro = path.basename(nomeDecodificado);
    nomeSeguro = nomeSeguro.replace(/[^a-zA-Z0-9.\-_ ]/g, "");

    if (!nomeSeguro || nomeSeguro.length === 0) {
        nomeSeguro = `upload_suspeito_${Date.now()}.bin`;
    }

    const caminhoDestino = path.join(PASTA_RECEPCAO, nomeSeguro);
    const caminhoHash = path.join(PASTA_RECEPCAO, `${nomeSeguro}.sha256`);
    
    const writeStream = fs.createWriteStream(caminhoDestino);
    req.pipe(writeStream);

    writeStream.on('finish', () => {
        if (fileHash) {
            fs.writeFileSync(caminhoHash, fileHash, 'utf-8');
            console.log(`[+] Mídia autenticada e salva: ${nomeSeguro}`);
        }
        res.status(200).send("Upload concluído.");
    });

    writeStream.on('error', (err) => {
        console.error(`[!] Erro de disco: ${err.message}`);
        res.status(500).send("Falha na gravação.");
    });
});

const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Servidor Seguro rodando na porta ${PORT}`);
});

// 2. MITIGAÇÃO DE DoS (Ajuste de Timeouts sem prejudicar vídeos grandes)
// Fecha a conexão APENAS se o dispositivo ficar 60 segundos sem enviar nenhum byte (Inatividade)
server.keepAliveTimeout = 60000; 
server.headersTimeout = 65000; 
// O timeout global (server.timeout) volta ao padrão (2 minutos para a resposta final). 
// Como usamos stream (req.pipe), o Node sabe que a conexão está ativa desde que os dados continuem a fluir.