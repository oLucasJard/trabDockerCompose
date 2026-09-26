# Aplicação Django Conteinerizada com Docker Compose

Aplicação Django com upload de arquivos, executada em três containers: **Nginx** como proxy reverso, **Django + Gunicorn** como aplicação e **PostgreSQL** como banco de dados. Os arquivos enviados são persistidos em volume nomeado, sobrevivendo à destruição dos containers.

> 📄 **[Documentação Técnica completa](DocumentaçãoTécnica-G1.docx)** — arquitetura, diagramas, justificativa das decisões e análise da solução.

---

## Arquitetura

```
                      +-----------+
                      | Navegador |
                      +-----------+
                            |
                            |  :8080 -> :80  (unica porta publicada)
  ==========================|=====================================
   HOST (Docker Engine)     v
   rede bridge: projeto-docker_default   (DNS interno 127.0.0.11)

        +-----------+      +------------+      +------------+
        |   nginx   |      |    web     |      |     db     |
        |  1.27-    |      |  python    |      |  postgres  |
        |  alpine   |      |  3.12-slim |      |  16-alpine |
        |           |      |  Gunicorn  |      |            |
        |   :80     |      |   :8000    |      |   :5432    |
        +-----------+      +------------+      +------------+
              |   proxy_pass      |   psycopg (TCP)   |
              +----- web:8000 --->+---- db:5432 ----->+

              |  leitura (:ro)    |  escrita          |  dados
              v                   v                   v
        +---------------------------------+   +---------------+
        |  media_volume  |  static_volume |   | postgres_data |
        |  (uploads)     |  (CSS / JS)    |   | (tabelas)     |
        +---------------------------------+   +---------------+
                     VOLUMES NOMEADOS (persistentes)
```

| Container | Porta interna | Porta no host | Responsabilidade |
|---|---|---|---|
| `nginx` | 80 | **8080** | Proxy reverso; serve `/static/` e `/media/` direto do disco |
| `web` | 8000 | — (`expose`) | Django + Gunicorn com 3 workers |
| `db` | 5432 | — | PostgreSQL; metadados dos arquivos |

Apenas o Nginx publica porta para o host. Django e PostgreSQL existem somente dentro da rede interna.

---

## Tecnologias

- Python 3.12 · Django 5 · Gunicorn
- PostgreSQL 16 (driver `psycopg` 3)
- Nginx 1.27
- Docker Engine · Docker Compose v2

---

## Como executar

**Pré-requisitos:** Docker Engine 20.10+ e Docker Compose v2.

```bash
git clone https://github.com/oLucasJard/trabDockerCompose.git
cd trabDockerCompose

cp .env.example .env      # edite as credenciais
docker compose up -d --build
```

Crie o usuário administrador:

```bash
docker compose exec web python manage.py createsuperuser
```

Acesse:

- **Aplicação (upload):** http://localhost:8080/
- **Admin:** http://localhost:8080/admin/

> A porta 8080 é usada porque a 80 costuma estar ocupada no host. Para alterá-la, edite `ports` do serviço `nginx` no `docker-compose.yml` e acrescente a nova origem em `CSRF_TRUSTED_ORIGINS` no `settings.py`.

---

## Verificar a persistência dos arquivos

```bash
# 1. envie um arquivo pela interface web, depois:
docker compose exec web ls -l /app/media/arquivos

# 2. destrua e recrie os containers
docker compose down && docker compose up -d

# 3. o arquivo continua lá:
docker compose exec web ls -l /app/media/arquivos
```

O arquivo permanece porque `MEDIA_ROOT` aponta para `/app/media`, que é o ponto de montagem do volume nomeado `media_volume` — este existe fora da camada de escrita do container.

---

## Comandos úteis

```bash
docker compose ps                # estado dos containers
docker compose logs -f web       # logs da aplicação
docker compose up -d --build     # reconstruir após alterar o código
docker compose down              # parar, MANTENDO os volumes
docker compose down -v           # parar e APAGAR os volumes
docker volume ls                 # listar volumes
```

---

## Variáveis de ambiente

Definidas em `.env` (não versionado — use `.env.example` como modelo):

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave secreta do Django |
| `DEBUG` | `0` em produção, `1` em desenvolvimento |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por espaço |
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `POSTGRES_HOST` | Nome do serviço no Compose (`db`) |
| `POSTGRES_PORT` | Porta do PostgreSQL (`5432`) |

As mesmas variáveis são lidas pela imagem oficial do Postgres (para criar o banco) e pelo Django (para conectar).

---

## Estrutura do projeto

```
trabDockerCompose/
├── docker-compose.yml     # orquestração dos 3 serviços e volumes
├── .env.example           # modelo de variáveis de ambiente
├── .gitignore
├── README.md
├── Documentacao_Tecnica_Docker.docx
├── app/
│   ├── Dockerfile         # imagem da aplicação Django
│   ├── entrypoint.sh      # espera do banco, migrate, collectstatic
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── manage.py
│   ├── core/              # settings, urls, wsgi
│   └── uploads/           # model, form, view, template do upload
└── nginx/
    ├── Dockerfile         # imagem do proxy reverso
    └── nginx.conf         # proxy e arquivos estáticos
```

---

## Autor

Lucas Jardim Rocha e João Pedro Menezes — trabalho acadêmico da disciplina de Docker e Docker Compose.
