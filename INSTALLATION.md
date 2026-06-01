# Guia de Instalação e Uso - Smart Coworking

## 🚀 Início Rápido

### Pré-requisitos
- Docker e Docker Compose instalados
- Portas disponíveis: 80, 3000, 5432, 6379, 8086, 1883, 1139, 1445

### Passo 1: Iniciar os Serviços

```bash
cd src
docker-compose up --build
```

### Passo 2: Acessar o Sistema

**Dashboard Principal (Admin)**
- URL: http://localhost
- Usuário: admin
- Senha: admin123

**Grafana (Relatórios Avançados)**
- URL: http://localhost:3000
- Usuário: admin
- Senha: admin123

## 📋 Funcionalidades do Dashboard

### 1. Página de Login
- Design minimalista e profissional
- Validação frontend de campos
- Feedback visual de erros
- Sugestão de credenciais demo

### 2. Dashboard Principal
- **Sidebar**: Navegação entre seções (Dashboard, Relatórios)
- **Métricas em Cards**: 
  - ⏱️ Tempo Total de Uso
  - ⚡ Energia Total Gasta
  - 💰 Total Pago
- **Gráficos Interativos**:
  - Gráfico de Barras: Consumo por tomada
  - Gráfico de Donut: Distribuição de energia
- **Tabela Detalhada**: Lista todas as tomadas com percentual

### 3. Página de Relatórios
- Integração com Grafana embedado
- Link direto para Grafana completo
- Possibilidade de criar dashboards personalizados

## 🎨 Design & Tecnologias

### Paleta de Cores (AWS-like)
- **Azul Corporativo**: #0066cc
- **Laranja Destaque**: #ff9900
- **Verde Sucesso**: #1abc9c
- **Vermelho Alerta**: #e74c3c
- **Preto Background**: #0f1419

### Responsividade
- Desktop: Layout em sidebar + main content
- Tablet (768px): Sidebar transforma em menu
- Mobile (480px): Otimizado para telas pequenas

## 🔐 Autenticação & Segurança

- JWT (JSON Web Tokens) para sessões
- Hash PBKDF2 para senhas
- Cookies HttpOnly para tokens
- Validação em cada rota protegida

## 📊 Integração de Dados

### PostgreSQL
- Armazena: Usuários, Sessões, Créditos
- Tabelas: users, sessions, outlets, credits

### InfluxDB
- Armazena: Métricas de consumo (Watts/segundo)
- Queries InfluxQL para agregações
- Range: Últimos 30 dias

### Mosquitto (MQTT)
- Recebe dados das tomadas inteligentes
- Porta: 1883

## 🛠️ Estrutura do Projeto

```
src/
├── apache/
│   └── httpd.conf              # Proxy reverso
├── routers/
│   ├── auth.py                 # Login, logout, JWT
│   └── dashboard.py            # Dashboard, relatórios
├── static/
│   └── style.css               # Estilos corporativos
├── templates/
│   ├── login.html              # Página de login
│   ├── dashboard.html          # Painel principal
│   └── reports.html            # Relatórios com Grafana
├── grafana/
│   └── datasources.yml         # Provisioning
├── database.py                 # Conexão PostgreSQL
├── models.py                   # Tabelas SQLAlchemy
├── main.py                     # App FastAPI
├── requirements.txt            # Dependências Python
└── docker-compose.yml          # Orquestração
```

## 🚀 Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /login | Página de login |
| POST | /login | Autenticação |
| GET | /dashboard | Dashboard (requer JWT) |
| GET | /reports | Relatórios com Grafana (requer JWT) |
| GET | /logout | Faz logout |
| POST | /users | Criar usuário (requer JWT) |

## 📈 Próximos Passos

1. **Adicionar dados de exemplo** ao InfluxDB via MQTT
2. **Configurar tomadas inteligentes** para enviar dados reais
3. **Criar dashboards personalizados** no Grafana
4. **Expandir permissões** de usuários
5. **Implementar API** para aplicativos mobile

## 🆘 Troubleshooting

### Erro de conexão com InfluxDB
```bash
docker-compose logs influxdb
```

### Resetar banco de dados
```bash
docker-compose down
docker volume rm src_postgres_data src_influxdb_data
docker-compose up --build
```

### Acessar terminal do container
```bash
docker exec -it backend_api bash
```

## 📞 Suporte

Para bugs ou sugestões, entre em contato com a equipe de desenvolvimento.

---

**Versão**: 1.0  
**Data**: Março 2026  
**Time**: Eduardo, Gabriel, João, Leonardo, Mauricio
