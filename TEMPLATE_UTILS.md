# Utilitários para Templates Jinja2

Este documento explica como usar funções Python dentro dos templates Jinja2 do projeto.

## 📋 Índice

1. [Filtros Customizados](#filtros-customizados)
2. [Funções do Contexto](#funções-do-contexto)
3. [Exemplos Práticos](#exemplos-práticos)

---

## 🔧 Filtros Customizados

Os filtros são usados com o operador `|` (pipe) nos templates.

### `format_currency`
Formata um valor numérico como moeda brasileira.

**Sintaxe:**
```jinja2
{{ valor|format_currency }}
{{ valor|format_currency('US$') }}  {# Com símbolo customizado #}
```

**Exemplos:**
```jinja2
{{ 1234.56|format_currency }}
{# Resultado: R$ 1.234,56 #}

{{ produto.preco|format_currency }}
{# Resultado: R$ 24,90 #}

{{ 1000|format_currency('US$') }}
{# Resultado: US$ 1.000,00 #}
```

---

### `format_number`
Formata um número com separador de milhar e casas decimais.

**Sintaxe:**
```jinja2
{{ valor|format_number }}
{{ valor|format_number(decimals=0) }}  {# Sem decimais #}
```

**Exemplos:**
```jinja2
{{ 1234.567|format_number }}
{# Resultado: 1.234,57 #}

{{ 1000|format_number(0) }}
{# Resultado: 1.000 #}
```

---

### `format_date`
Formata uma data.

**Sintaxe:**
```jinja2
{{ data|format_date }}
{{ data|format_date('%d/%m/%Y %H:%M') }}  {# Formato customizado #}
```

**Exemplos:**
```jinja2
{{ produto.validade|format_date }}
{# Resultado: 31/12/2024 #}

{{ '2024-12-31'|format_date('%d de %B de %Y') }}
{# Resultado: 31 de dezembro de 2024 #}
```

---

### `format_quantity`
Formata quantidade com unidade de medida.

**Sintaxe:**
```jinja2
{{ valor|format_quantity }}
{{ valor|format_quantity('kg') }}  {# Com unidade #}
```

**Exemplos:**
```jinja2
{{ 10.5|format_quantity('kg') }}
{# Resultado: 10,50 kg #}

{{ produto.quantidade|format_quantity(produto.uni_medida) }}
{# Resultado: 5,00 un #}
```

---

## 🎯 Funções do Contexto

As funções são chamadas diretamente como funções Python normais.

### `calcular_total_itens(carrinho)`
Calcula o total de itens no carrinho.

**Sintaxe:**
```jinja2
{{ calcular_total_itens(carrinho) }}
```

**Exemplo:**
```jinja2
{% set total = calcular_total_itens(carrinho) %}
Total: {{ total|format_currency }}
```

---

### `get_produto_by_id(produtos, produto_id)`
Busca um produto na lista pelo ID.

**Sintaxe:**
```jinja2
{{ get_produto_by_id(produtos, produto_id) }}
```

**Exemplo:**
```jinja2
{% set produto = get_produto_by_id(produtos, item.produto_id) %}
{% if produto %}
    {{ produto.nome }} - {{ produto.preco|format_currency }}
{% endif %}
```

---

## 💡 Exemplos Práticos

### Exemplo 1: Formatação de Preços
```jinja2
<!-- Antes -->
R$ {{ "%.2f"|format(produto.preco) }}

<!-- Depois -->
{{ produto.preco|format_currency }}
```

### Exemplo 2: Formatação de Quantidade
```jinja2
{{ produto.quantidade|format_quantity(produto.uni_medida) }}
{# Resultado: 10,50 kg #}
```

### Exemplo 3: Cálculo Dinâmico no Template
```jinja2
{% set subtotal = item.produto.preco * item.quantidade %}
Subtotal: {{ subtotal|format_currency }}
```

### Exemplo 4: Buscar Produto por ID
```jinja2
{% set produto = get_produto_by_id(produtos, 123) %}
{% if produto %}
    <p>{{ produto.nome }} - {{ produto.preco|format_currency }}</p>
{% else %}
    <p>Produto não encontrado</p>
{% endif %}
```

### Exemplo 5: Formatação de Data
```jinja2
{% if produto.validade %}
    Validade: {{ produto.validade|format_date }}
{% endif %}
```

---

## ➕ Adicionando Novos Filtros ou Funções

### Para adicionar um novo filtro:

1. Crie a função em `src/common/template_utils.py`
2. Registre no `app.py`:
```python
app.jinja_env.filters['nome_do_filtro'] = sua_funcao
```

### Para adicionar uma nova função ao contexto:

1. Crie a função em `src/common/template_utils.py`
2. Adicione ao context processor no `app.py`:
```python
context.update({
    'nome_da_funcao': sua_funcao,
})
```

---

## 📝 Notas Importantes

- **Filtros** são usados com `|` e recebem o valor à esquerda como primeiro parâmetro
- **Funções** são chamadas diretamente e recebem todos os parâmetros explicitamente
- Todas as funções e filtros estão disponíveis em **todos os templates** automaticamente
- Use filtros para transformações simples de valores
- Use funções para lógica mais complexa que requer múltiplos parâmetros

