# 📁 Estrutura do Projeto Mercadim

Este documento explica a organização da estrutura de pastas do projeto, facilitando o entendimento e colaboração de todos os desenvolvedores.

## 🎯 Visão Geral

O projeto está organizado em uma estrutura modular e didática, separando claramente:
- **Infraestrutura** (core)
- **Componentes compartilhados** (common)
- **Funcionalidades de negócio** (features)

## 📂 Estrutura de Pastas

```
Mercadim/
├── app.py                  # Entrada principal da aplicação Flask
├── config.py               # Configurações da aplicação
├── requirements.txt        # Dependências Python
├── Procfile               # Configuração para deploy (Railway, Heroku, etc.)
├── README.md              # Documentação principal
├── ESTRUTURA.md           # Este arquivo
│
├── src/                   # Código-fonte principal
│   ├── __init__.py
│   │
│   ├── core/              # 🔧 INFRAESTRUTURA BASE
│   │   ├── __init__.py
│   │   └── database.py    # Cliente Supabase (inicialização e acesso)
│   │
│   ├── common/            # 🔄 COMPONENTES COMPARTILHADOS
│   │   ├── __init__.py
│   │   ├── utils.py       # Funções utilitárias (validações, helpers)
│   │   └── interface/     # Componentes de interface
│   │       ├── __init__.py
│   │       ├── context.py # Contexto global da interface (menus, sidebar)
│   │       └── menu.py    # Definição de menus e itens
│   │
│   └── features/          # 🎯 MÓDULOS DE NEGÓCIO
│       ├── __init__.py
│       │
│       ├── auth/          # Módulo de Autenticação
│       │   ├── __init__.py        # Exporta blueprint e decorators
│       │   ├── auth_routes.py     # Rotas de autenticação (login, logout, etc.)
│       │   ├── auth_service.py    # Lógica de negócio de autenticação
│       │   └── auth_decorators.py # Decorators (@login_required, @admin_required, etc.)
│       │
│       ├── profile/       # Módulo de Perfil
│       │   ├── __init__.py        # Blueprint e rotas de perfil
│       │   └── profile_service.py # Lógica de negócio de perfil
│       │
│       └── user/          # Módulo de Usuários
│           ├── __init__.py
│           └── user_service.py   # Lógica de negócio de usuários
│
├── templates/             # Templates HTML (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── auth/
│   │   └── login.html
│   ├── profile/
│   │   └── profile.html
│   └── components/
│       ├── sidebar.html
│       └── topbar.html
│
└── static/                # Arquivos estáticos
    ├── css/
    │   └── global.css
    └── img/
        └── logo_mercadim.png
```

## 📚 Descrição Detalhada

### 🔧 `src/core/` - Infraestrutura Base

Contém serviços fundamentais da aplicação que são usados por todos os módulos.

**Responsabilidades:**
- Inicialização de serviços externos (Supabase, etc.)
- Configurações de infraestrutura
- Clientes de banco de dados

**Exemplo de uso:**
```python
from src.core import supabase_client

# Obter cliente Supabase
client = supabase_client()
```

### 🔄 `src/common/` - Componentes Compartilhados

Contém utilitários e componentes reutilizáveis em toda a aplicação.

**Responsabilidades:**
- Funções utilitárias (validações, formatação, etc.)
- Componentes de interface (menus, contexto)
- Helpers genéricos

**Exemplo de uso:**
```python
from src.common.utils import is_valid_email, is_strong_password
from src.common.interface import get_interface_context
```

### 🎯 `src/features/` - Módulos de Negócio

Cada feature representa uma funcionalidade completa do sistema, organizada de forma independente.

#### Estrutura de uma Feature

Cada feature segue um padrão consistente:

```
feature/
├── __init__.py          # Exporta blueprint e principais componentes
├── [feature]_routes.py  # Rotas HTTP (blueprints Flask)
├── [feature]_service.py # Lógica de negócio
└── [feature]_decorators.py # Decorators específicos (se necessário)
```

**Exemplo:** O módulo `auth` tem:
- `auth_routes.py` (não apenas `routes.py`)
- `auth_service.py` (não apenas `service.py`)
- `auth_decorators.py` (não apenas `decorators.py`)

Isso evita confusão quando há múltiplos arquivos abertos e facilita a identificação do módulo.

**Exemplo - Módulo Auth:**
```python
# Importar blueprint
from src.features.auth import auth_bp

# Importar decorators
from src.features.auth import login_required, admin_required

# Importar serviços (se necessário)
from src.features.auth import login, sign_out
```

**Exemplo - Módulo Profile:**
```python
# Importar blueprint
from src.features.profile import profile_bp

# Importar serviços
from src.features.profile.profile_service import get_user_profile
```

## 🎨 Princípios de Organização

### 1. **Separação de Responsabilidades**
- **Core**: Infraestrutura e serviços base
- **Common**: Utilitários e componentes genéricos
- **Features**: Funcionalidades específicas de negócio

### 2. **Modularidade**
Cada feature é independente e pode ser desenvolvida, testada e mantida separadamente.

### 3. **Consistência**
Todas as features seguem o mesmo padrão estrutural, facilitando navegação e compreensão.

### 4. **Clareza**
Nomes descritivos e organização lógica facilitam encontrar código rapidamente.

## 📝 Convenções de Nomenclatura

### Arquivos
- `[feature]_routes.py` - Rotas HTTP (blueprints) - Ex: `auth_routes.py`, `profile_routes.py`
- `[feature]_service.py` - Lógica de negócio - Ex: `auth_service.py`, `profile_service.py`
- `[feature]_decorators.py` - Decorators Flask (específico do módulo) - Ex: `auth_decorators.py`
- `utils.py` - Funções utilitárias

### Pastas
- Nomes em minúsculas
- Nomes descritivos e autoexplicativos
- Evitar abreviações desnecessárias

## 🔍 Como Encontrar Código

### Buscar uma rota de autenticação?
→ `src/features/auth/auth_routes.py`

### Buscar lógica de negócio de perfil?
→ `src/features/profile/profile_service.py`

### Buscar validação de email?
→ `src/common/utils.py`

### Buscar configuração do Supabase?
→ `src/core/database.py`

### Buscar definição de menus?
→ `src/common/interface/menu.py`

## 🚀 Adicionando uma Nova Feature

Para adicionar uma nova feature (ex: `products`):

1. **Criar estrutura básica:**
```bash
mkdir -p src/features/products
touch src/features/products/__init__.py
touch src/features/products/products_routes.py
touch src/features/products/products_service.py
```

2. **Criar blueprint em `products_routes.py`:**
```python
from flask import Blueprint

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
def list_products():
    # ...
    pass
```

3. **Exportar em `__init__.py`:**
```python
from .products_routes import products_bp

__all__ = ['products_bp']
```

4. **Registrar no `app.py`:**
```python
from src.features.products import products_bp

app.register_blueprint(products_bp)
```

## 📖 Boas Práticas

1. **Sempre use services para lógica de negócio**
   - Evite colocar lógica complexa diretamente nas rotas
   - Services facilitam testes e reutilização

2. **Mantenha rotas simples**
   - Rotas devem apenas receber requisições e chamar services
   - Validação básica pode estar nas rotas, mas lógica complexa vai para services

3. **Use decorators para controle de acesso**
   - `@login_required` para rotas protegidas
   - `@admin_required` para rotas administrativas
   - `@guest_only` para rotas públicas (login, registro)

4. **Importe de forma consistente**
   - Use imports absolutos: `from src.features.auth import ...`
   - Evite imports circulares

## 🐛 Troubleshooting

### Import Error?
Verifique se:
- O arquivo `__init__.py` existe na pasta
- Os imports estão usando os caminhos corretos da nova estrutura
- O Python está no diretório correto

### Módulo não encontrado?
Verifique se:
- O módulo está em `src/features/` (não em `src/`)
- O `__init__.py` exporta o componente necessário
- Os imports usam caminhos absolutos começando com `src.`

## 📞 Dúvidas?

Se tiver dúvidas sobre onde colocar código ou como estruturar uma nova feature, consulte:
1. Este documento (ESTRUTURA.md)
2. Features existentes como referência (auth, profile)
3. Outros colaboradores do projeto

---

**Última atualização:** Reorganização da estrutura para melhor clareza e didática.

