-- Cliente (mestre SAP)
CREATE TABLE dbo.tb_cm_margem_cliente (
    id_cliente        BIGINT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_cliente PRIMARY KEY,
    codigo_sap        NVARCHAR(20)  NOT NULL,
    razao_social      NVARCHAR(200) NOT NULL,
    razao_social_ci   AS UPPER(razao_social) COLLATE Latin1_General_CI_AI PERSISTED,
    cnpj              NVARCHAR(20)  NULL,
    inscricao_estadual NVARCHAR(30) NULL,
    email             NVARCHAR(254) NULL,
    telefone          NVARCHAR(30)  NULL,
    ativo             BIT           NOT NULL DEFAULT (1),
    created_at        DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at        DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_tb_cm_margem_cliente_codigo_sap UNIQUE (codigo_sap)
);
GO

CREATE INDEX IX_tb_cm_margem_cliente_razao_ci  ON dbo.tb_cm_margem_cliente (razao_social_ci);
CREATE INDEX IX_tb_cm_margem_cliente_email_low ON dbo.tb_cm_margem_cliente (email);
GO

-- Filial (mestre SAP)
CREATE TABLE dbo.tb_cm_margem_filial (
    id_filial    INT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_filial PRIMARY KEY,
    codigo_sap   NVARCHAR(10)  NOT NULL,
    nome         NVARCHAR(120) NOT NULL,
    nome_ci      AS UPPER(nome) COLLATE Latin1_General_CI_AI PERSISTED,
    uf           CHAR(2)       NULL,
    cidade       NVARCHAR(100) NULL,
    ativo        BIT           NOT NULL DEFAULT (1),
    created_at   DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at   DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_tb_cm_margem_filial_codigo_sap UNIQUE (codigo_sap)
);
GO

CREATE INDEX IX_tb_cm_margem_filial_nome_ci ON dbo.tb_cm_margem_filial (nome_ci);
GO

-- Produto / Modelo (mestre SAP)
CREATE TABLE dbo.tb_cm_margem_produto (
    id_produto    BIGINT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_produto PRIMARY KEY,
    codigo_sap    NVARCHAR(40)  NOT NULL,
    descricao     NVARCHAR(200) NOT NULL,
    descricao_ci  AS UPPER(descricao) COLLATE Latin1_General_CI_AI PERSISTED,
    sigla_modelo  NVARCHAR(50)  NULL,
    familia       NVARCHAR(80)  NULL,
    tipo_produto  NVARCHAR(50)  NULL,
    ativo         BIT           NOT NULL DEFAULT (1),
    created_at    DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at    DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_tb_cm_margem_produto_codigo_sap UNIQUE (codigo_sap)
);
GO

CREATE INDEX IX_tb_cm_margem_produto_desc_ci ON dbo.tb_cm_margem_produto (descricao_ci);
GO

-- Vendedor (mestre SAP / força de vendas)
CREATE TABLE dbo.tb_cm_margem_vendedor (
    id_vendedor   INT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_vendedor PRIMARY KEY,
    codigo_sap    NVARCHAR(20)  NOT NULL,
    nome          NVARCHAR(150) NOT NULL,
    nome_ci       AS UPPER(nome) COLLATE Latin1_General_CI_AI PERSISTED,
    email         NVARCHAR(254) NULL,
    id_filial     INT           NULL,
    ativo         BIT           NOT NULL DEFAULT (1),
    created_at    DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at    DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_tb_cm_margem_vendedor_codigo_sap UNIQUE (codigo_sap),
    CONSTRAINT FK_tb_cm_margem_vendedor_filial
        FOREIGN KEY (id_filial) REFERENCES dbo.tb_cm_margem_filial (id_filial)
);
GO

CREATE INDEX IX_tb_cm_margem_vendedor_nome_ci   ON dbo.tb_cm_margem_vendedor (nome_ci);
CREATE INDEX IX_tb_cm_margem_vendedor_email_low ON dbo.tb_cm_margem_vendedor (email);
GO

-- Usuário (Azure AD)
CREATE TABLE dbo.tb_cm_margem_usuario (
    id_usuario          INT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_usuario PRIMARY KEY,
    azure_oid           NVARCHAR(64)  NOT NULL,
    email_login         NVARCHAR(254) NOT NULL,
    nome                NVARCHAR(150) NULL,
    id_vendedor         INT           NULL,
    cargo               NVARCHAR(30)  NOT NULL,
    ativo               BIT           NOT NULL DEFAULT (1),
    created_at          DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at          DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_tb_cm_margem_usuario_azure_oid       UNIQUE (azure_oid),
    CONSTRAINT UQ_tb_cm_margem_usuario_email_login_low UNIQUE (email_login),
    CONSTRAINT FK_tb_cm_margem_usuario_vendedor
        FOREIGN KEY (id_vendedor) REFERENCES dbo.tb_cm_margem_vendedor (id_vendedor)
);
GO

-- Tipo de venda
CREATE TABLE dbo.tb_cm_margem_tipo_venda (
    id_tipo_venda  SMALLINT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_tipo_venda PRIMARY KEY,
    nome           NVARCHAR(80) NOT NULL,
    codigo_interno NVARCHAR(20) NULL,
    flag_financiado   BIT       NOT NULL DEFAULT (0),
    flag_orgao_publico BIT      NOT NULL DEFAULT (0),
    ativo          BIT          NOT NULL DEFAULT (1),
    created_at     DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at     DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_tb_cm_margem_tipo_venda_nome UNIQUE (nome)
);
GO

-- Modalidade de financiamento
CREATE TABLE dbo.tb_cm_margem_modalidade_financiamento (
    id_modalidade_fin SMALLINT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_modalidade_fin PRIMARY KEY,
    nome              NVARCHAR(80) NOT NULL,
    codigo_interno    NVARCHAR(20) NULL,
    ativo             BIT          NOT NULL DEFAULT (1),
    created_at        DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at        DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_tb_cm_margem_modalidade_fin_nome UNIQUE (nome)
);
GO

-- Banco financiador
CREATE TABLE dbo.tb_cm_margem_banco_financiador (
    id_banco_financiador INT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_banco_financiador PRIMARY KEY,
    codigo_sap           NVARCHAR(10)  NULL,
    nome                 NVARCHAR(120) NOT NULL,
    ativo                BIT           NOT NULL DEFAULT (1),
    created_at           DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at           DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE UNIQUE INDEX UQ_tb_cm_margem_banco_financiador_nome
    ON dbo.tb_cm_margem_banco_financiador (nome);
GO

-- Configuração de Desconto Negociado (DE PARA)
CREATE TABLE dbo.tb_cm_margem_config_dn (
    id_dn                  BIGINT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_config_dn PRIMARY KEY,
    id_produto             BIGINT      NOT NULL,
    id_filial              INT         NOT NULL,
    id_tipo_venda          SMALLINT    NOT NULL,
    id_modalidade_fin      SMALLINT    NULL,
    possui_af              BIT         NOT NULL DEFAULT (0),
    ano                    SMALLINT    NOT NULL,
    mes                    TINYINT     NULL, -- 1-12 ou NULL se usar conceito "ano cheio"
    data_referencia        DATE        NULL,
    valor_dn               DECIMAL(18,2) NOT NULL,
    origem_dado            NVARCHAR(30)   NOT NULL DEFAULT ('PLANILHA'), -- PLANILHA, SAP, e etc
    id_modalidade_fin_zero AS ISNULL(CONVERT(INT, id_modalidade_fin), 0) PERSISTED,
    mes_zero               AS ISNULL(mes, 0) PERSISTED,
    created_at             DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at             DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_tb_cm_margem_config_dn_produto
        FOREIGN KEY (id_produto)        REFERENCES dbo.tb_cm_margem_produto (id_produto),
    CONSTRAINT FK_tb_cm_margem_config_dn_filial
        FOREIGN KEY (id_filial)         REFERENCES dbo.tb_cm_margem_filial (id_filial),
    CONSTRAINT FK_tb_cm_margem_config_dn_tipo_venda
        FOREIGN KEY (id_tipo_venda)     REFERENCES dbo.tb_cm_margem_tipo_venda (id_tipo_venda),
    CONSTRAINT FK_tb_cm_margem_config_dn_modalidade
        FOREIGN KEY (id_modalidade_fin) REFERENCES dbo.tb_cm_margem_modalidade_financiamento (id_modalidade_fin),
    CONSTRAINT CK_tb_cm_margem_config_dn_mes CHECK (mes IS NULL OR (mes BETWEEN 1 AND 12)),
    CONSTRAINT CK_tb_cm_margem_config_dn_ano CHECK (ano BETWEEN 2000 AND 2100)
);
GO

CREATE UNIQUE INDEX UQ_tb_cm_margem_config_dn_chave
    ON dbo.tb_cm_margem_config_dn (
        id_produto,
        id_filial,
        id_tipo_venda,
        id_modalidade_fin_zero,
        possui_af,
        ano,
        mes_zero
    );
GO

-- Parâmetros Gerais (impostos, comissões, taxa, etc)
CREATE TABLE dbo.tb_cm_margem_parametro_geral (
    id_parametro      INT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_parametro_geral PRIMARY KEY,
    codigo            NVARCHAR(50)  NOT NULL, -- Exemplo: ICMS_PIS_COFINS_COMPRA
    descricao         NVARCHAR(200) NULL,
    valor_decimal     DECIMAL(18,6) NULL,
    valor_texto       NVARCHAR(200) NULL,
    id_filial         INT           NULL,
    id_tipo_venda     SMALLINT      NULL,
    id_modalidade_fin SMALLINT      NULL,
    data_inicio       DATE          NOT NULL,
    data_fim          DATE          NULL,
    ativo             BIT           NOT NULL DEFAULT (1),
    created_at        DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at        DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_tb_cm_margem_param_geral_filial
        FOREIGN KEY (id_filial)         REFERENCES dbo.tb_cm_margem_filial (id_filial),
    CONSTRAINT FK_tb_cm_margem_param_geral_tipo_venda
        FOREIGN KEY (id_tipo_venda)     REFERENCES dbo.tb_cm_margem_tipo_venda (id_tipo_venda),
    CONSTRAINT FK_tb_cm_margem_param_geral_modalidade
        FOREIGN KEY (id_modalidade_fin) REFERENCES dbo.tb_cm_margem_modalidade_financiamento (id_modalidade_fin)
);
GO

CREATE INDEX IX_tb_cm_margem_param_geral_codigo
    ON dbo.tb_cm_margem_parametro_geral (codigo, id_filial, id_tipo_venda, id_modalidade_fin, data_inicio);
GO

-- Cabeçalho da reserva
CREATE TABLE dbo.tb_cm_margem_reserva (
    id_reserva             BIGINT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_reserva PRIMARY KEY,
    codigo_reserva         NVARCHAR(30)   NULL,
    id_cliente             BIGINT         NOT NULL,
    id_filial              INT            NOT NULL,
    id_vendedor            INT            NULL,
    id_tipo_venda          SMALLINT       NOT NULL,
    id_modalidade_fin      SMALLINT       NULL,
    id_banco_financiador   INT            NULL,
    possui_af              BIT            NOT NULL DEFAULT (0),
    data_reserva           DATETIME2(0)   NOT NULL,
    previsao_entrega       DATE           NULL,
    taxa_juros_mensal_padrao DECIMAL(9,6) NULL, -- J26 da planilha (1,72% = 0,0172)
    observacoes            NVARCHAR(1000) NULL,
    status_reserva         TINYINT        NOT NULL DEFAULT (1), -- 1=rascunho, 2=calculada, 3=aprovada, 4=cancelada
    criado_por             INT            NULL,
    atualizado_por         INT            NULL,
    created_at             DATETIME2(0)   NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at             DATETIME2(0)   NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_tb_cm_margem_reserva_cliente
        FOREIGN KEY (id_cliente)           REFERENCES dbo.tb_cm_margem_cliente (id_cliente),
    CONSTRAINT FK_tb_cm_margem_reserva_filial
        FOREIGN KEY (id_filial)            REFERENCES dbo.tb_cm_margem_filial (id_filial),
    CONSTRAINT FK_tb_cm_margem_reserva_vendedor
        FOREIGN KEY (id_vendedor)          REFERENCES dbo.tb_cm_margem_vendedor (id_vendedor),
    CONSTRAINT FK_tb_cm_margem_reserva_tipo_venda
        FOREIGN KEY (id_tipo_venda)        REFERENCES dbo.tb_cm_margem_tipo_venda (id_tipo_venda),
    CONSTRAINT FK_tb_cm_margem_reserva_modalidade
        FOREIGN KEY (id_modalidade_fin)    REFERENCES dbo.tb_cm_margem_modalidade_financiamento (id_modalidade_fin),
    CONSTRAINT FK_tb_cm_margem_reserva_banco_fin
        FOREIGN KEY (id_banco_financiador) REFERENCES dbo.tb_cm_margem_banco_financiador (id_banco_financiador),
    CONSTRAINT FK_tb_cm_margem_reserva_criado_por
        FOREIGN KEY (criado_por)           REFERENCES dbo.tb_cm_margem_usuario (id_usuario),
    CONSTRAINT FK_tb_cm_margem_reserva_atualizado_por
        FOREIGN KEY (atualizado_por)       REFERENCES dbo.tb_cm_margem_usuario (id_usuario)
);
GO

CREATE INDEX IX_tb_cm_margem_reserva_cliente  ON dbo.tb_cm_margem_reserva (id_cliente, data_reserva);
CREATE INDEX IX_tb_cm_margem_reserva_filial   ON dbo.tb_cm_margem_reserva (id_filial, data_reserva);
GO

-- Item da reserva (uma máquina / modelo)
CREATE TABLE dbo.tb_cm_margem_reserva_item (
    id_reserva_item                 BIGINT IDENTITY(1,1) CONSTRAINT PK_tb_cm_margem_reserva_item PRIMARY KEY,
    id_reserva                      BIGINT         NOT NULL,
    id_produto                      BIGINT         NOT NULL,
    id_dn                           BIGINT         NULL,  -- Referência da config de DN
    quantidade                      INT            NOT NULL DEFAULT (1),
    valor_venda_unitario            DECIMAL(18,2)  NOT NULL,
    valor_venda_total               AS (valor_venda_unitario * quantidade) PERSISTED,
    valor_dn_unitario               DECIMAL(18,2)  NOT NULL,
    valor_dn_total                  AS (valor_dn_unitario * quantidade) PERSISTED,
    impostos_venda_percent          DECIMAL(9,6)   NOT NULL DEFAULT (0),
    impostos_venda_valor            DECIMAL(18,2)  NOT NULL DEFAULT (0),
    impostos_compra_percent_icms_piscofins DECIMAL(9,6)  NOT NULL DEFAULT (0),
    impostos_compra_percent_piscofins      DECIMAL(9,6)  NOT NULL DEFAULT (0),
    impostos_compra_valor_total     DECIMAL(18,2)  NOT NULL DEFAULT (0),
    valor_opcionais                 DECIMAL(18,2)  NOT NULL DEFAULT (0),
    valor_mao_obra                  DECIMAL(18,2)  NOT NULL DEFAULT (0),
    custo_frete_compra              DECIMAL(18,2)  NOT NULL DEFAULT (0),
    perc_credito_impostos_frete     DECIMAL(9,6)   NOT NULL DEFAULT (0),
    valor_credito_impostos_frete    DECIMAL(18,2)  NOT NULL DEFAULT (0),
    custo_contrato_manutencao       DECIMAL(18,2)  NOT NULL DEFAULT (0),
    perc_pdi_garantia               DECIMAL(9,6)   NOT NULL DEFAULT (0),
    valor_pdi_garantia              DECIMAL(18,2)  NOT NULL DEFAULT (0),
    frete_venda                     DECIMAL(18,2)  NOT NULL DEFAULT (0),
    custo_financeiro_total          DECIMAL(18,2)  NOT NULL DEFAULT (0),
    valor_carta_fianca              DECIMAL(18,2)  NOT NULL DEFAULT (0),
    valor_cortesia                  DECIMAL(18,2)  NOT NULL DEFAULT (0),
    comissao_total                  DECIMAL(18,2)  NOT NULL DEFAULT (0),
    margem_bruta_valor              DECIMAL(18,2)  NOT NULL DEFAULT (0),
    margem_bruta_percent            DECIMAL(9,6)   NOT NULL DEFAULT (0),
    margem_contrib_valor            DECIMAL(18,2)  NOT NULL DEFAULT (0),
    margem_contrib_percent          DECIMAL(9,6)   NOT NULL DEFAULT (0),
    created_at                      DATETIME2(0)   NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at                      DATETIME2(0)   NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_tb_cm_margem_reserva_item_reserva
        FOREIGN KEY (id_reserva) REFERENCES dbo.tb_cm_margem_reserva (id_reserva),
    CONSTRAINT FK_tb_cm_margem_reserva_item_produto
        FOREIGN KEY (id_produto) REFERENCES dbo.tb_cm_margem_produto (id_produto),
    CONSTRAINT FK_tb_cm_margem_reserva_item_dn
        FOREIGN KEY (id_dn)      REFERENCES dbo.tb_cm_margem_config_dn (id_dn),
    CONSTRAINT CK_tb_cm_margem_reserva_item_qtd CHECK (quantidade > 0),
    CONSTRAINT CK_tb_cm_margem_reserva_item_perc CHECK (
        impostos_venda_percent          BETWEEN 0 AND 1 AND
        impostos_compra_percent_icms_piscofins BETWEEN 0 AND 1 AND
        impostos_compra_percent_piscofins      BETWEEN 0 AND 1 AND
        perc_credito_impostos_frete     BETWEEN 0 AND 1 AND
        perc_pdi_garantia               BETWEEN 0 AND 1 AND
        margem_bruta_percent           BETWEEN -1 AND 5 AND
        margem_contrib_percent         BETWEEN -1 AND 5
    )
);
GO

CREATE INDEX IX_tb_cm_margem_reserva_item_reserva ON dbo.tb_cm_margem_reserva_item (id_reserva);
GO

-- Opcionais / Agrega / Desagrega
CREATE TABLE dbo.tb_cm_margem_reserva_item_opcional (
    id_reserva_item_opcional BIGINT IDENTITY(1,1)
        CONSTRAINT PK_tb_cm_margem_reserva_item_opcional PRIMARY KEY,
    id_reserva_item          BIGINT        NOT NULL,
    descricao                NVARCHAR(200) NOT NULL,
    horas                    DECIMAL(9,2)  NULL,
    quantidade               INT           NOT NULL DEFAULT (1),
    custo_unitario           DECIMAL(18,2) NOT NULL,
    valor_total              AS (custo_unitario * quantidade) PERSISTED,
    created_at               DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at               DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_tb_cm_margem_reserva_item_opc_item
        FOREIGN KEY (id_reserva_item) REFERENCES dbo.tb_cm_margem_reserva_item (id_reserva_item)
);
GO

CREATE INDEX IX_tb_cm_margem_reserva_item_opc_item
    ON dbo.tb_cm_margem_reserva_item_opcional (id_reserva_item);
GO

-- Fluxo de pagamento (entrada + parcelas)
CREATE TABLE dbo.tb_cm_margem_reserva_item_fluxo (
    id_reserva_item_fluxo BIGINT IDENTITY(1,1)
        CONSTRAINT PK_tb_cm_margem_reserva_item_fluxo PRIMARY KEY,
    id_reserva_item       BIGINT        NOT NULL,
    tipo_parcela          TINYINT       NOT NULL, -- 1=entrada e 2=parcela
    numero_parcela        SMALLINT      NOT NULL, -- 0 para entrada
    prazo_dias            INT           NOT NULL,
    percentual_base       DECIMAL(9,6)  NOT NULL,
    valor_nominal         DECIMAL(18,2) NOT NULL,
    taxa_efetiva          DECIMAL(9,6)  NOT NULL,
    valor_presente        DECIMAL(18,2) NOT NULL,
    custo_financeiro      DECIMAL(18,2) NOT NULL,
    created_at            DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at            DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_tb_cm_margem_fluxo_item
        FOREIGN KEY (id_reserva_item) REFERENCES dbo.tb_cm_margem_reserva_item (id_reserva_item),
    CONSTRAINT CK_tb_cm_margem_fluxo_tipo_parcela CHECK (tipo_parcela IN (1,2)),
    CONSTRAINT CK_tb_cm_margem_fluxo_percentual_base CHECK (percentual_base BETWEEN 0 AND 1)
);
GO

CREATE INDEX IX_tb_cm_margem_fluxo_item
    ON dbo.tb_cm_margem_reserva_item_fluxo (id_reserva_item, numero_parcela);
GO

-- Detalhe da comissão do vendedor
CREATE TABLE dbo.tb_cm_margem_reserva_item_comissao (
    id_reserva_item_comissao BIGINT IDENTITY(1,1)
        CONSTRAINT PK_tb_cm_margem_reserva_item_comissao PRIMARY KEY,
    id_reserva_item          BIGINT        NOT NULL,
    tipo_comissao            NVARCHAR(20)  NOT NULL, -- BRUTA, DSR, ENCARGO
    percentual               DECIMAL(9,6)  NOT NULL,
    valor                    DECIMAL(18,2) NOT NULL,
    created_at               DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at               DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_tb_cm_margem_item_comissao_item
        FOREIGN KEY (id_reserva_item) REFERENCES dbo.tb_cm_margem_reserva_item (id_reserva_item),
    CONSTRAINT CK_tb_cm_margem_item_comissao_tipo
        CHECK (tipo_comissao IN ('BRUTA','DSR','ENCARGO')),
    CONSTRAINT CK_tb_cm_margem_item_comissao_perc
        CHECK (percentual BETWEEN 0 AND 5)
);
GO

CREATE INDEX IX_tb_cm_margem_item_comissao_item
    ON dbo.tb_cm_margem_reserva_item_comissao (id_reserva_item);
GO

-- Log de integração com SAP
CREATE TABLE dbo.tb_cm_margem_log_integracao_sap (
    id_log_integracao BIGINT IDENTITY(1,1)
        CONSTRAINT PK_tb_cm_margem_log_integracao_sap PRIMARY KEY,
    sistema_origem    NVARCHAR(50)  NOT NULL,
    tipo_registro     NVARCHAR(50)  NOT NULL,
    chave_externa     NVARCHAR(100) NOT NULL,
    data_execucao     DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME(),
    sucesso           BIT           NOT NULL,
    mensagem_erro     NVARCHAR(MAX) NULL
);
GO
