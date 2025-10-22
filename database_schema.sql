-- =====================================================
-- SISTEMA DE COMPRAS - SCRIPT DE CRIAÇÃO DO BANCO
-- Database: purchase_system
-- PostgreSQL 12+
-- =====================================================

-- Criar banco de dados (executar como superuser)
-- CREATE DATABASE purchase_system WITH ENCODING 'UTF8' LC_COLLATE='pt_BR.UTF-8' LC_CTYPE='pt_BR.UTF-8';

-- Conectar ao banco: \c purchase_system

-- =====================================================
-- EXTENSÕES
-- =====================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- TABELA: departments
-- =====================================================
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'INATIVO')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_departments_status ON departments(status);

-- =====================================================
-- TABELA: users
-- =====================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'MANAGER', 'USER', 'PURCHASER', 'FINANCE')),
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'INATIVO')),
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_department ON users(department_id);

-- =====================================================
-- TABELA: products
-- =====================================================
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    average_unit_value DECIMAL(15, 2) DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'INATIVO')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_name ON products(product_name);

-- =====================================================
-- TABELA: purchase_requests
-- =====================================================
CREATE TABLE purchase_requests (
    id SERIAL PRIMARY KEY,
    request_number VARCHAR(20) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    estimated_total DECIMAL(15, 2),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING' CHECK (status IN (
        'PENDING', 'APPROVED', 'REJECTED', 'IN_QUOTATION', 
        'QUOTED', 'VENDOR_APPROVED', 'PURCHASED', 
        'INVOICE_RECEIVED', 'PAYMENT_RELEASED', 'PAID', 'CANCELLED'
    )),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP,
    rejected_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    rejected_at TIMESTAMP,
    rejected_reason TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_purchase_requests_user ON purchase_requests(user_id);
CREATE INDEX idx_purchase_requests_product ON purchase_requests(product_id);
CREATE INDEX idx_purchase_requests_status ON purchase_requests(status);
CREATE INDEX idx_purchase_requests_created ON purchase_requests(created_at);
CREATE INDEX idx_purchase_requests_number ON purchase_requests(request_number);

-- =====================================================
-- TABELA: quotations
-- =====================================================
CREATE TABLE quotations (
    id SERIAL PRIMARY KEY,
    purchase_request_id INTEGER NOT NULL REFERENCES purchase_requests(id) ON DELETE CASCADE,
    purchaser_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'RELEASED', 'APPROVED', 'CANCELLED')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    released_at TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quotations_request ON quotations(purchase_request_id);
CREATE INDEX idx_quotations_purchaser ON quotations(purchaser_id);
CREATE INDEX idx_quotations_status ON quotations(status);

-- =====================================================
-- TABELA: quotation_items
-- =====================================================
CREATE TABLE quotation_items (
    id SERIAL PRIMARY KEY,
    quotation_id INTEGER NOT NULL REFERENCES quotations(id) ON DELETE CASCADE,
    vendor_name VARCHAR(200) NOT NULL,
    vendor_cnpj VARCHAR(18),
    description TEXT,
    unit_value DECIMAL(15, 2) NOT NULL CHECK (unit_value >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    total_value DECIMAL(15, 2) NOT NULL CHECK (total_value >= 0),
    is_selected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quotation_items_quotation ON quotation_items(quotation_id);
CREATE INDEX idx_quotation_items_selected ON quotation_items(is_selected);

-- =====================================================
-- TABELA: purchase_orders
-- =====================================================
CREATE TABLE purchase_orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(20) NOT NULL UNIQUE,
    purchase_request_id INTEGER NOT NULL REFERENCES purchase_requests(id) ON DELETE CASCADE,
    quotation_item_id INTEGER NOT NULL REFERENCES quotation_items(id) ON DELETE CASCADE,
    purchaser_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pdf_path VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'CREATED' CHECK (status IN ('CREATED', 'SENT', 'CONFIRMED', 'CANCELLED')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_purchase_orders_request ON purchase_orders(purchase_request_id);
CREATE INDEX idx_purchase_orders_purchaser ON purchase_orders(purchaser_id);
CREATE INDEX idx_purchase_orders_number ON purchase_orders(order_number);

-- =====================================================
-- TABELA: invoices
-- =====================================================
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    purchase_order_id INTEGER NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50) NOT NULL,
    vendor_cnpj VARCHAR(18) NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL CHECK (total_value >= 0),
    informed_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    informed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(invoice_number, vendor_cnpj)
);

CREATE INDEX idx_invoices_order ON invoices(purchase_order_id);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);

-- =====================================================
-- TABELA: payments
-- =====================================================
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'RELEASED', 'PAID', 'CANCELLED')),
    released_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    released_at TIMESTAMP,
    paid_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    paid_at TIMESTAMP,
    payment_notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_invoice ON payments(invoice_id);
CREATE INDEX idx_payments_status ON payments(status);

-- =====================================================
-- TABELA: audit_log
-- =====================================================
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);

-- =====================================================
-- TABELA: system_parameters
-- =====================================================
CREATE TABLE system_parameters (
    id SERIAL PRIMARY KEY,
    param_key VARCHAR(100) NOT NULL UNIQUE,
    param_value TEXT,
    description TEXT,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- FUNÇÕES E TRIGGERS
-- =====================================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_purchase_requests_updated_at BEFORE UPDATE ON purchase_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quotations_updated_at BEFORE UPDATE ON quotations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quotation_items_updated_at BEFORE UPDATE ON quotation_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_purchase_orders_updated_at BEFORE UPDATE ON purchase_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_parameters_updated_at BEFORE UPDATE ON system_parameters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Função para gerar número de requisição
CREATE OR REPLACE FUNCTION generate_request_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.request_number = 'REQ-' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') || '-' || LPAD(NEW.id::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Função para gerar número de pedido
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.order_number = 'PO-' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDD') || '-' || LPAD(NEW.id::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para gerar números automaticamente
CREATE TRIGGER set_request_number BEFORE INSERT ON purchase_requests
    FOR EACH ROW EXECUTE FUNCTION generate_request_number();

CREATE TRIGGER set_order_number BEFORE INSERT ON purchase_orders
    FOR EACH ROW EXECUTE FUNCTION generate_order_number();

-- Função para atualizar average_unit_value do produto
CREATE OR REPLACE FUNCTION update_product_average_price()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products 
    SET average_unit_value = (
        SELECT AVG(qi.unit_value)
        FROM quotation_items qi
        JOIN quotations q ON qi.quotation_id = q.id
        JOIN purchase_requests pr ON q.purchase_request_id = pr.id
        WHERE pr.product_id = NEW.id 
        AND qi.is_selected = TRUE
        AND pr.status IN ('PURCHASED', 'INVOICE_RECEIVED', 'PAYMENT_RELEASED', 'PAID')
    )
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- DADOS INICIAIS
-- =====================================================

-- Inserir departamentos padrão
INSERT INTO departments (name, status) VALUES
    ('Tecnologia da Informação', 'ATIVO'),
    ('Recursos Humanos', 'ATIVO'),
    ('Financeiro', 'ATIVO'),
    ('Operações', 'ATIVO'),
    ('Comercial', 'ATIVO'),
    ('Marketing', 'ATIVO');

-- Inserir usuário admin padrão (senha: admin123)
-- Hash gerado com bcrypt para 'admin123'
INSERT INTO users (username, email, password_hash, role, department_id, status) VALUES
    ('admin', 'admin@empresa.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6', 'ADMIN', 1, 'ATIVO');

-- Inserir parâmetros do sistema
INSERT INTO system_parameters (param_key, param_value, description) VALUES
    ('company_name', 'Empresa XYZ Ltda', 'Nome da empresa'),
    ('company_cnpj', '00.000.000/0001-00', 'CNPJ da empresa'),
    ('min_quotations', '3', 'Número mínimo de cotações obrigatórias'),
    ('auto_approve_limit', '1000.00', 'Valor limite para aprovação automática'),
    ('currency', 'BRL', 'Moeda padrão do sistema');

-- Inserir produtos de exemplo
INSERT INTO products (sku, product_name, description, average_unit_value, status) VALUES
    ('SKU-001', 'Mouse USB', 'Mouse óptico USB com fio', 25.00, 'ATIVO'),
    ('SKU-002', 'Teclado USB', 'Teclado padrão ABNT2 USB', 45.00, 'ATIVO'),
    ('SKU-003', 'Monitor 24"', 'Monitor LED 24 polegadas Full HD', 650.00, 'ATIVO'),
    ('SKU-004', 'Cadeira Escritório', 'Cadeira giratória com apoio lombar', 450.00, 'ATIVO'),
    ('SKU-005', 'Notebook', 'Notebook i5 8GB RAM 256GB SSD', 3200.00, 'ATIVO'),
    ('SKU-006', 'Impressora Laser', 'Impressora laser monocromática', 850.00, 'ATIVO'),
    ('SKU-007', 'Papel A4', 'Resma papel sulfite A4 com 500 folhas', 22.00, 'ATIVO'),
    ('SKU-008', 'Caneta Esferográfica', 'Caneta esferográfica azul', 1.50, 'ATIVO'),
    ('SKU-009', 'Grampeador', 'Grampeador de mesa', 15.00, 'ATIVO'),
    ('SKU-010', 'HD Externo 1TB', 'HD externo portátil 1TB USB 3.0', 320.00, 'ATIVO');

-- =====================================================
-- VIEWS ÚTEIS
-- =====================================================

-- View: Requisições com informações completas
CREATE OR REPLACE VIEW vw_purchase_requests_full AS
SELECT 
    pr.id,
    pr.request_number,
    pr.status,
    pr.quantity,
    pr.estimated_total,
    pr.notes,
    pr.created_at,
    pr.approved_at,
    pr.rejected_at,
    pr.rejected_reason,
    u.username as requester_username,
    u.email as requester_email,
    d.name as requester_department,
    p.sku,
    p.product_name,
    p.description as product_description,
    p.average_unit_value,
    approver.username as approver_username,
    rejector.username as rejector_username,
    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - pr.created_at)) as days_since_request
FROM purchase_requests pr
JOIN users u ON pr.user_id = u.id
LEFT JOIN departments d ON u.department_id = d.id
JOIN products p ON pr.product_id = p.id
LEFT JOIN users approver ON pr.approved_by = approver.id
LEFT JOIN users rejector ON pr.rejected_by = rejector.id;

-- View: Dashboard de compras por departamento
CREATE OR REPLACE VIEW vw_purchases_by_department AS
SELECT 
    d.id as department_id,
    d.name as department_name,
    COUNT(pr.id) as total_requests,
    COUNT(CASE WHEN pr.status = 'PAID' THEN 1 END) as completed_requests,
    SUM(CASE WHEN pr.status = 'PAID' THEN pr.estimated_total ELSE 0 END) as total_spent,
    AVG(EXTRACT(DAY FROM (pr.updated_at - pr.created_at))) as avg_days_to_complete
FROM departments d
LEFT JOIN users u ON d.id = u.department_id
LEFT JOIN purchase_requests pr ON u.id = pr.user_id
WHERE d.status = 'ATIVO'
GROUP BY d.id, d.name;

-- =====================================================
-- COMENTÁRIOS NAS TABELAS
-- =====================================================

COMMENT ON TABLE users IS 'Tabela de usuários do sistema com controle de permissões';
COMMENT ON TABLE departments IS 'Departamentos da empresa';
COMMENT ON TABLE products IS 'Catálogo de produtos disponíveis para requisição';
COMMENT ON TABLE purchase_requests IS 'Requisições de compra criadas pelos usuários';
COMMENT ON TABLE quotations IS 'Mapas de cotação criados pelos compradores';
COMMENT ON TABLE quotation_items IS 'Itens individuais de cada cotação (fornecedores)';
COMMENT ON TABLE purchase_orders IS 'Ordens de compra geradas após aprovação';
COMMENT ON TABLE invoices IS 'Notas fiscais informadas pelos solicitantes';
COMMENT ON TABLE payments IS 'Controle de pagamentos pelo financeiro';
COMMENT ON TABLE audit_log IS 'Log de auditoria de todas as ações no sistema';

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================

