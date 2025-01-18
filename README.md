# API Evolution Bet

## Visão Geral
Este projeto consiste em uma API RESTful para gerenciamento de dados de roletas e um serviço WebSocket para coleta de dados em tempo real. O sistema é composto por dois componentes principais:

1. **API REST**: Desenvolvida em Flask, fornece endpoints para consulta de dados
2. **WebSocket Client**: Conecta-se a provedores de dados e armazena informações no banco de dados SQLite

## Estrutura de Arquivos
```
.
├── api.py               # Implementação da API REST
├── roletawebsocket.py   # Cliente WebSocket
├── roletas.db           # Banco de dados SQLite
├── requirements.txt     # Dependências do projeto
├── Dockerfile           # Configuração do container Docker
├── supervisord.conf     # Configuração do gerenciador de processos
├── .env                 # Variáveis de ambiente
└── logs/                # Diretório de logs
```

## Dependências
- Flask (API REST)
- Flask-Swagger-UI (Documentação da API)
- websocket-client (Conexão WebSocket)
- supabase (Integração com banco de dados)
- python-dotenv (Gerenciamento de variáveis de ambiente)

## Configuração do Ambiente

### Variáveis de Ambiente
Crie um arquivo `.env` com as seguintes variáveis:
```bash
SUPABASE_URL=<url_do_supabase>
SUPABASE_KEY=<chave_do_supabase>
```

## Execução Local

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute os serviços:
```bash
# Em terminais separados
python api.py
python roletawebsocket.py
```

## Execução via Docker Compose

O projeto utiliza Docker Compose para gerenciamento de containers. O arquivo `docker-compose.yml` contém toda a configuração necessária e utiliza automaticamente o Dockerfile para construir a imagem.

### Fluxo de Construção

1. Docker Compose lê o arquivo docker-compose.yml
2. Identifica a necessidade de construir uma nova imagem
3. Utiliza o Dockerfile para construir a imagem
4. Cria e inicia os containers com as configurações especificadas

### Comandos Básicos

1. Iniciar o container:
```bash
docker-compose up -d --build
```

2. Parar o container:
```bash
docker-compose down
```

3. Verificar logs:
```bash
docker-compose logs -f
```

4. Acessar terminal do container:
```bash
docker-compose exec apievolutionbet bash
```

### Monitoramento de Logs no Portainer

Siga este passo a passo detalhado para monitorar os logs:

1. **Acesse o Portainer**
   - Abra o navegador e acesse a interface do Portainer (geralmente http://localhost:9000)
   - Faça login com suas credenciais

2. **Localize o Container**
   - No menu lateral esquerdo, clique em "Containers"
   - Na lista de containers, localize "apievolutionbet"

3. **Visualize Logs Gerais**
   - Clique no nome do container "apievolutionbet"
   - No painel que abrir, clique na aba "Logs"
   - Aqui você verá todos os logs do container em tempo real

4. **Acesse Logs Específicos**
   - No mesmo painel do container, clique em "Console"
   - Selecione a opção "/bin/bash" e clique em "Connect"
   - No terminal que abrir, execute:
     ```bash
     cd /var/log/supervisor
     ls
     ```
   - Você verá os arquivos de log:
     - api.out.log
     - api.err.log
     - websocket.out.log
     - websocket.err.log
   - Para acompanhar um log específico em tempo real, use:
     ```bash
     tail -f nome_do_arquivo.log
     ```
     Exemplo:
     ```bash
     tail -f api.out.log
     ```

5. **Dicas Úteis**
   - Use `Ctrl+C` para parar o acompanhamento de logs
   - Para limpar a tela do terminal, use `clear`
   - Para sair do terminal, digite `exit`

## Componentes Principais

### API REST (`api.py`)
- Endpoints:
  - `GET /api/roletas`: Lista todas as roletas
  - `GET /api/roletas/<game_token>`: Obtém dados de uma roleta específica
  - `GET /static/swagger.json`: Especificação OpenAPI

### WebSocket Client (`roletawebsocket.py`)
- Conecta-se a provedores de dados via WebSocket
- Coleta e armazena resultados de roletas
- Implementa reconexão automática em caso de falhas

## Monitoramento de Logs

O container gera logs em dois níveis:

1. Logs do container (stdout/stderr)
2. Logs de aplicação (arquivos em /var/log/supervisor)

### Acompanhando via Portainer

1. Acesse o Portainer
2. Navegue até o container "apievolutionbet"
3. Clique em "Logs" para ver os logs em tempo real
4. Para acessar os arquivos de log:
   - Clique em "Console"
   - Selecione "/bin/bash"
   - Navegue até /var/log/supervisor
   - Use `tail -f` para acompanhar os logs em tempo real

### Comandos Úteis

### Docker
- Verificar logs:
```bash
docker logs apievolutionbet
```

- Parar container:
```bash
docker stop apievolutionbet
```

- Iniciar container:
```bash
docker start apievolutionbet
```

- Remover container:
```bash
docker rm -f apievolutionbet
```

### Desenvolvimento
- Atualizar dependências:
```bash
pip freeze > requirements.txt
```

- Rodar testes:
```bash
# Adicionar testes aqui no futuro
```
