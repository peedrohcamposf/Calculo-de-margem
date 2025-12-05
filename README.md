# Cálculo de Margem

Sistema para cálculo de margem de contribuição na venda de máquinas, com autenticação e integração com banco de dados para consulta dos valores de compra dos equipamentos.

---

## Objetivos do sistema

- Calcular a margem de contribuição de forma padronizada.
- Centralizar regras de negócio que hoje estão em planilhas (ex.: "Planilha MARGEM de CONTRIBUIÇÃO - VALTER ROMAGNOLI").
- Utilizar os valores de compra das máquinas diretamente do banco de dados.
- Permitir que apenas usuários autenticados (Azure AD) acessem o sistema.
- Preparar o terreno para futuras integrações (SAP e etc.).

---

## Estrutura geral do projeto

Estrutura sugerida (exemplo):

```text
app/
  __init__.py
  domain/
    __init__.py
    base.py
    usuario.py
    maquina.py
  routes/
    ...
  services/
    ...
  forms/
    ...
  templates/
    ...
  static/
    ...
```

* `app/domain/`: modelos de domínio (camada de acesso ao banco e entidades de negócio).
* `routes/`: blueprints / rotas Flask.
* `services/`: camada de regras de negócio (cálculos, validações, orquestração).
* `forms/`: formulários do WTForms.
* `templates/`: páginas HTML com Jinja2.
* `static/`: CSS, JS, imagens etc.

---

## Modelos de domínio

### `Base` e `TimestampMixin`

Arquivo: `app/domain/base.py`

* `Base`: classe base do SQLAlchemy usada por todos os models.
* `TimestampMixin`: adiciona colunas padrão:

  * `created_at`: preenchida pelo banco com `SYSUTCDATETIME()` na inserção.
  * `updated_at`: preenchida pelo banco na inserção e atualizada automaticamente em updates.

Isso garante rastreabilidade de criação/atualização de todos os registros.

### `UsuarioModel`

Arquivo: `app/domain/usuario.py`

Model para o usuário autenticado via Azure AD:

* Tabela: `dbo.tb_cm_usuario`
* Campos principais:
  * `id_usuario`: chave primária.
  * `azure_oid`: OID do usuário no Azure AD (único).
  * `email_login`: e-mail utilizado no login (único).
  * `nome`: nome do usuário.
  * `cargo`: cargo do usuário.
  * `ativo`: flag booleana indicando se o usuário está ativo.

* Herda:
  * `TimestampMixin` (campos de auditoria).
  * `UserMixin` (Flask-Login).
  
* Implementa `get_id()` para integração com o Flask-Login.

### `MaquinaModel`

Arquivo: `app/domain/maquina.py`

Model para cadastro das máquinas utilizadas no cálculo de margem:

* Tabela: `dbo.tb_cm_maquinas`
* Campos principais:

  * `id_maquina`: chave primária.
  * `marca`: marca da máquina.
  * `tipo`: tipo / família da máquina.
  * `modelo`: descrição do modelo.
  * `codigo`: código único da máquina.
  * `valor_compra`: valor de compra da máquina (base para cálculo de margem).

Esse model é a base para buscar o custo de aquisição no banco de dados e alimentar os cálculos (CMV, impostos de compra, etc.).

---

## Regras gerais de cálculo de margem

De forma simplificada, o fluxo envolve:

1. **Valor de venda**

   * Inserido pelo usuário ou calculado a partir de uma reserva/proposta.

2. **Impostos sobre venda**

   * ICMS e PIS/COFINS aplicados sobre o valor de venda.
   * Exemplo genérico:
     `Impostos Venda = (ICMS * Valor de Venda) + (PIS/COFINS * Valor de Venda)`

3. **Impostos sobre compra**

   * Calculados sobre o **valor de compra** da máquina (campo `valor_compra` de `tb_cm_maquinas`).
   * Exemplo genérico:
     `Impostos Compra = (ICMS + PIS/COFINS * Valor da Máquina) + (PIS/COFINS * Valor da Máquina)`

4. **Lucro Bruto**

   * Considera valor de venda, valor de compra, impostos e opcionais.

5. **Comissão do vendedor**

   * Comissão bruta (percentual sobre valor de venda).
   * DSR (percentual sobre comissão bruta).
   * Encargos comissão (percentual sobre [comissão bruta + DSR]).
   * Comissão total em R$ = soma de todos esses componentes.

6. **Outros custos**

   * Frete de venda (Brasif → cliente).
   * Custo financeiro.
   * Carta fiança bancária (percentual ou valor aplicado sobre a venda).
   * Cortesia.

7. **Margem de Contribuição**

   * Fórmula conceitual:

     ```text
     Margem de Contribuição = 
       Lucro Bruto
       - Frete Venda
       + Crédito de Impostos
       - Custo Financeiro
       - Carta Fiança Bancária
       - Cortesia
       - Comissão Total do Vendedor (R$)
     ```

8. **%RB (Percentual da Margem)**

   * `%RB = Margem de Contribuição / Valor de Venda`

O sistema organiza essas etapas, garantindo que os campos inseridos pelo usuário sejam tratados com validação, e que os cálculos sejam consistentes com a planilha de referência.

---

## Configuração do ambiente

### 1. Clonar o repositório

```bash
git clone https://github.com/sua-org/seu-repo-calculo-margem.git
cd seu-repo-calculo-margem
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Variáveis de ambiente

Defina as variáveis de ambiente usadas pelo projeto, preencha de acordo com o .env.example.

---

## Executando o projeto

Com o ambiente configurado e o banco pronto:

```bash
python main.py
```

A aplicação ficará disponível em:

```text
http://localhost:5000
```

---

## Autenticação

* Usuários são autenticados via **Azure AD**.
* Após o login, os dados principais são armazenados em `tb_cm_usuario`:

  * `azure_oid` como identificador único do usuário.
  * `email_login` como login principal.
* O model `UsuarioModel` implementa `UserMixin` e fornece o `get_id()` para integração transparente com o Flask-Login.