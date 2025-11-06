# Mercadim - Projeto Flask

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🚀 Como Iniciar o Projeto

### 1. Instalar as Dependências

Primeiro, instale todas as dependências necessárias:

```bash
pip install -r requirements.txt
```

Ou se estiver usando um ambiente virtual (recomendado):

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo `.env-exemplo` para `.env`:

```bash
cp .env-exemplo .env
```

Edite o arquivo `.env` e configure as variáveis necessárias:
- `SECRET_KEY`: Chave secreta para sessões Flask
- `SUPABASE_URL`: URL do seu projeto Supabase
- `SUPABASE_KEY`: Chave de API do Supabase

**Nota:** O arquivo `.env` já existe no projeto, mas certifique-se de que contém os valores corretos.

### 3. Iniciar o Servidor Flask

Execute o comando:

```bash
python app.py
```

Ou usando o comando Flask:

```bash
flask run
```

O servidor será iniciado em modo de desenvolvimento (debug=True) e estará disponível em:
- **URL:** http://127.0.0.1:5000 ou http://localhost:5000

### 4. Acessar a Aplicação

Abra seu navegador e acesse:
- http://localhost:5000

A aplicação redirecionará automaticamente para a página de login se você não estiver autenticado.

## 🔧 Estrutura do Projeto

```
Mercadim/
├── app.py                 # Arquivo principal da aplicação Flask
├── config.py              # Configurações da aplicação
├── requirements.txt       # Dependências do projeto
├── .env                   # Variáveis de ambiente (não versionado)
├── .env-exemplo           # Exemplo de variáveis de ambiente
├── src/
│   ├── auth/             # Módulo de autenticação
│   ├── profile/          # Módulo de perfil
│   ├── supabase.py       # Cliente Supabase
│   └── utils/            # Utilitários
├── templates/            # Templates HTML
└── static/               # Arquivos estáticos (CSS, JS, etc.)
```

## 📝 Notas Importantes

- O projeto está configurado para usar sessões do Flask com armazenamento em arquivos
- A autenticação é gerenciada através do Supabase
- O modo debug está ativado por padrão (apenas para desenvolvimento)

## 🐛 Solução de Problemas

Se encontrar erros ao iniciar:

1. **Erro de importação:** Verifique se todas as dependências foram instaladas
2. **Erro de configuração Supabase:** Verifique se as variáveis `SUPABASE_URL` e `SUPABASE_KEY` estão corretas no arquivo `.env`
3. **Erro de porta em uso:** Se a porta 5000 estiver em uso, você pode alterar no `app.py` ou usar `flask run --port 5001`

