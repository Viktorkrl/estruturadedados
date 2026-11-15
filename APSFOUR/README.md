# API de Gestao de Eventos Academicos: Autenticacao e Seguranca RESTful

Avaliacao Parcial 04 (APS 4) referente a evolucao da API de gestao de eventos academicos com foco em autenticacao, autorizacao baseada em perfis (RBAC), hash seguro de credenciais e protecao de rotas via tokens JWT (JSON Web Token).

## 1. Descricao do Projeto

Esta aplicacao fornece uma solucao robusta para o gerenciamento de eventos academicos, participantes e inscricoes de uma instituicao de ensino superior.

A evolucao desenvolvida na APS 4 introduz camada de seguranca com os seguintes pilares tecnicos:

* Criptografia de senhas: Uso da biblioteca `pwdlib` com o algoritmo `Argon2id`, garantindo que nenhuma senha em texto puro seja persistida no banco de dados.
* Autenticacao centralizada: Emissao de tokens padrao JWT no endpoint `POST /auth/login`.
* Validacao de sessao no servidor: Identificacao de usuario ativo por meio da rota `GET /auth/me` a partir da assinatura do token Bearer.
* Controle de acesso baseado em perfis (RBAC): Distincao estrita entre privilegios de `administrador` e `usuario` comum.
* Preservacao das regras de negocio e relatorios consolidados: Manutencao de integridade sobre capacidade de eventos, unicidade de inscricoes e geracao de relatorios analiticos.

## 2. Estrutura Arquitetural do Projeto

O projeto adota o padrao arquitetural MVC (Model, View/Schema, Controller) associado a camadas de Servico e Seguranca, garantindo separacao clara de responsabilidades:

```text
aps4-sistema-eventos/
├── .env
├── .env.example
├── .gitignore
├── database.py
├── main.py
├── requirements.txt
├── README.md
├── seed_dados.py
├── executar_demonstracao.py
│
├── controller/
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── evento_controller.py
│   ├── inscricao_controller.py
│   ├── participante_controller.py
│   ├── relatorio_controller.py
│   └── usuario_controller.py
│
├── model/
│   ├── __init__.py
│   ├── evento.py
│   ├── inscricao.py
│   ├── participante.py
│   └── usuario.py
│
├── schema/
│   ├── __init__.py
│   ├── evento_schema.py
│   ├── inscricao_schema.py
│   ├── participante_schema.py
│   ├── relatorio_schema.py
│   └── usuario_schema.py
│
├── service/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── evento_service.py
│   ├── inscricao_service.py
│   ├── participante_service.py
│   ├── relatorio_service.py
│   └── usuario_service.py
│
├── security/
│   ├── __init__.py
│   └── security.py
│
└── tests/
    ├── __init__.py
    └── test_api.py
```

### Detalhamento das Camadas

* Controller: Responsavel pelo roteamento HTTP, validacao de parametros de entrada e despacho para os servicos correspondentes.
* Model: Entidades ORM gerenciadas pelo SQLAlchemy, mapeando as tabelas `usuarios`, `eventos`, `participantes` e `inscricoes`.
* Schema: Modelos Pydantic para serializacao, desserializacao, validacao de formatos e protecao contra vazamento de dados sensiveis.
* Service: Regras de negocio da aplicacao, controle de duplicidades, regras de capacidade e analise de metricas consolidadas.
* Security: Modulo centralizado para hashing de senhas com Argon2, assinatura e inspecao de tokens JWT, e injecao de dependencias do FastAPI para validacao de escopo e credenciais.
* Database: Configuracao da conexao com SQLite e sessao do SQLAlchemy (`SessionLocal`).

## 3. Instrucoes para Instalacao e Execucao

### Pre-requisitos

* Python versao 3.10 ou superior instalada no ambiente.
* Gerenciador de pacotes `pip`.

### Passo a Passo de Instalacao

1. Clone ou acesse o diretorio do projeto:
```bash
cd aps4-sistema-eventos
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
```
No Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```
No Linux ou macOS:
```bash
source .venv/bin/activate
```

3. Instale as dependencias necessarias:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo de variaveis de ambiente:
Copie o modelo de configuracao:
```bash
cp .env.example .env
```

5. Execute a aplicacao:
```bash
uvicorn main:app --reload --port 8000
```

A API ficara acessivel em `http://localhost:8000`.
A documentacao interativa do Swagger estara disponivel em `http://localhost:8000/docs`.

## 4. Configuracao da Chave Secreta e Seguranca

Conforme as boas praticas de seguranca de software, nenhuma chave criptografica privada real deve ser exposta no repositorio de codigo fonte.

No arquivo `.env`, ajuste as variaveis conforme o exemplo:

```env
SECRET_KEY=sua_chave_criptografica_privada_com_mais_de_32_bytes_de_comprimento
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./eventos.db
DEFAULT_ADMIN_NAME=Administrador Inicial
DEFAULT_ADMIN_EMAIL=admin@sistema.com
DEFAULT_ADMIN_PASSWORD=Admin@123456
```

### Politica de Seguranca Implementada

* O algoritmo utilizado para geracao de hashes de senha e o Argon2id por meio da biblioteca `pwdlib`. Nao sao utilizados algoritmos obsoletos como MD5 ou SHA1.
* A chave secreta e carregada estritamente via variaveis de ambiente (`python-dotenv` / `os.getenv`).
* O token JWT contem validade configuravel (padrao de 60 minutos), data de emissao (`iat`) e identificadores do usuario autenticado (`sub`, `usuario_id`, `email`, `perfil`).

## 5. Estrategia de Inicializacao do Administrador

Para evitar a exposicao de brechas em que qualquer usuario pudesse se autoatribuir o perfil de administrador:

1. A rota de criacao publica de usuarios (`POST /usuarios`) forca invariavelmente o perfil `usuario`.
2. O sistema possui rotina automatica durante o ciclo de vida inicial (`lifespan` do FastAPI) que detecta a existencia de contas administrativas. Caso nao haja administrador no banco de dados, a conta definida em `.env` e provisionada de forma segura com senha criptografada.
3. E disponibilizado tambem o script `seed_dados.py` para recriacao controlada de massa de dados e administrador inicial.

## 6. Descricao dos Perfis e Regras de Permissao

A aplicacao possui dois niveis de perfil:

1. Perfil `administrador`:
* Cadastrar eventos (`POST /eventos`)
* Atualizar eventos (`PUT /eventos/{id}`)
* Excluir eventos (`DELETE /eventos/{id}`)
* Atualizar e excluir participantes (`PUT/DELETE /participantes/{id}`)
* Cancelar inscricoes (`DELETE /inscricoes/{id}`)
* Consultar lista completa de usuarios do sistema (`GET /usuarios`)
* Consultar todos os relatorios consolidados analiticos (`GET /relatorios/*`)

2. Perfil `usuario`:
* Consultar eventos disponiveis (`GET /eventos`, `GET /eventos/{id}`)
* Consultar participantes (`GET /participantes`, `GET /participantes/{id}`)
* Cadastrar participantes (`POST /participantes`)
* Realizar inscricoes em eventos (`POST /inscricoes`)
* Consultar suas proprias inscricoes (`GET /inscricoes`)
* Consultar seus proprios dados autenticados (`GET /auth/me`)

Tentativas de usuarios comuns executarem rotas restritas sao barradas no servidor com codigo HTTP `403 Forbidden`.

## 7. Mapeamento das Rotas da API

### Rotas Publicas

* `POST /usuarios`: Cadastra um novo usuario no sistema com perfil `usuario`.
* `POST /auth/login`: Autentica com email e senha, retornando token JWT do tipo Bearer.
* `GET /docs`: Interface interativa Swagger UI.
* `GET /openapi.json`: Especificacao OpenAPI em formato JSON.

### Rotas Protegidas (Exigem Token Bearer Valido)

* `GET /auth/me`: Retorna os dados do usuario vinculado ao token enviado.
* `GET /eventos`: Lista os eventos cadastrados.
* `GET /eventos/{id}`: Detalhes de um evento especifico.
* `GET /participantes`: Lista de participantes.
* `GET /participantes/{id}`: Detalhes de um participante.
* `POST /participantes`: Cadastra um novo participante.
* `POST /inscricoes`: Realiza a inscricao de um participante em um evento.
* `GET /inscricoes`: Lista as inscricoes efetuadas.
* `GET /inscricoes/{id}`: Consulta dados de uma inscricao.

### Rotas Restritas ao Administrador (Exigem Perfil `administrador`)

* `POST /eventos`: Criacao de novos eventos academicos.
* `PUT /eventos/{id}`: Atualizacao de dados ou capacidade do evento.
* `DELETE /eventos/{id}`: Exclusao de evento e remocao de suas inscricoes vinculadas.
* `PUT /participantes/{id}`: Atualizacao cadastral de participante.
* `DELETE /participantes/{id}`: Exclusao de participante.
* `DELETE /inscricoes/{id}`: Cancelamento de inscricao.
* `GET /usuarios`: Listagem de usuarios do sistema.
* `GET /relatorios/ocupacao-eventos`: Relatorio consolidado de ocupacao e vagas.
* `GET /relatorios/eventos-por-categoria`: Relatorio quantitativo agrupado por categoria.
* `GET /relatorios/participacao-por-curso`: Relatorio de participacao agrupado por curso.

## 8. Exemplos de Utilizacao da API

### 8.1 Cadastro de Usuario

Requisicao:
```http
POST /usuarios HTTP/1.1
Content-Type: application/json

{
  "nome": "Mariana Souza",
  "email": "mariana.souza@exemplo.com",
  "senha": "senha_segura_123"
}
```

Resposta de Sucesso (`201 Created`):
```json
{
  "id": 2,
  "nome": "Mariana Souza",
  "email": "mariana.souza@exemplo.com",
  "perfil": "usuario"
}
```

### 8.2 Autenticacao e Obtencao de Token

Requisicao:
```http
POST /auth/login HTTP/1.1
Content-Type: application/json

{
  "email": "mariana.souza@exemplo.com",
  "senha": "senha_segura_123"
}
```

Resposta de Sucesso (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 8.3 Consulta do Proprio Usuario Autenticado

Requisicao:
```http
GET /auth/me HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Resposta de Sucesso (`200 OK`):
```json
{
  "id": 2,
  "nome": "Mariana Souza",
  "email": "mariana.souza@exemplo.com",
  "perfil": "usuario"
}
```

### 8.4 Criacao de Evento por Administrador

Requisicao:
```http
POST /eventos HTTP/1.1
Authorization: Bearer <TOKEN_ADMIN>
Content-Type: application/json

{
  "nome": "Congresso de Engenharia de Software 2026",
  "descricao": "Palestras sobre arquitetura de microsservicos e seguranca",
  "categoria": "Engenharia",
  "data_evento": "2026-12-15",
  "vagas": 100
}
```

Resposta de Sucesso (`201 Created`):
```json
{
  "id": 1,
  "nome": "Congresso de Engenharia de Software 2026",
  "descricao": "Palestras sobre arquitetura de microsservicos e seguranca",
  "categoria": "Engenharia",
  "data_evento": "2026-12-15",
  "vagas": 100,
  "vagas_ocupadas": 0,
  "vagas_disponiveis": 100
}
```

### 8.5 Realizacao de Inscricao em Evento

Requisicao:
```http
POST /inscricoes HTTP/1.1
Authorization: Bearer <TOKEN_USUARIO>
Content-Type: application/json

{
  "evento_id": 1,
  "participante_id": 1
}
```

Resposta de Sucesso (`201 Created`):
```json
{
  "id": 1,
  "evento_id": 1,
  "participante_id": 1,
  "data_inscricao": "2026-11-15T20:14:12",
  "evento_nome": "Congresso de Engenharia de Software 2026",
  "participante_nome": "Lucas Mendes"
}
```

## 9. Tratamento de Erros e Codigos HTTP

A API adota codigos de status HTTP padronizados para todas as respostas:

* `401 Unauthorized`:
  * Credenciais incorretas: `{"detail": "E-mail ou senha inválidos."}`
  * Token ausente, invalido ou expirado: `{"detail": "Não foi possível validar as credenciais."}`
* `403 Forbidden`:
  * Usuario autenticado sem permissao para operacao: `{"detail": "Você não possui permissão para executar esta operação."}`
* `404 Not Found`:
  * Recurso nao localizado no banco: `{"detail": "Evento não encontrado."}` ou `{"detail": "Participante não encontrado."}`
* `409 Conflict`:
  * Duplicidade de e-mail de usuario ou participante: `{"detail": "Já existe um usuário cadastrado com este e-mail."}`
  * Inscricao repetida: `{"detail": "Participante já inscrito neste evento."}`
* `400 Bad Request`:
  * Regra de capacidade violada: `{"detail": "Evento com vagas esgotadas."}`

## 10. Instrucoes para Reproduzir os Testes

O projeto conta com suite de testes automatizados cobrindo integralmente os 12 cenarios solicitados pela avaliacao.

### Execucao com Pytest

Para rodar a bateria de testes automatizados com exibicao detalhada de cada caso:

```bash
pytest -v
```

Resultado esperado: 12 testes aprovados com status `PASSED`.

### Execucao do Script de Demonstracao Completo

Para visualizar a execucao sequencial de todos os cenarios com demonstracao de payloads, status code HTTP e retorno JSON em terminal:

```bash
python executar_demonstracao.py
```

### Teste Interativo via Swagger UI

1. Inicie a aplicacao com `uvicorn main:app --reload`.
2. Abra no navegador: `http://localhost:8000/docs`.
3. Cadastre um usuario em `POST /usuarios`.
4. Obtenha o token em `POST /auth/login`.
5. Clique no botao verde `Authorize` no topo superior direito da pagina do Swagger.
6. Cole o token no campo de autenticacao e clique em `Authorize`.
7. Realize as requisicoes diretamente pela interface web.
