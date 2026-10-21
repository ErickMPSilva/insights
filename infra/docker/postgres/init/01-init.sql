-- =========================================================
-- Usuários (roles)
-- =========================================================
-- migrator: dono das tabelas; usado pelo Alembic e pelo dbt
CREATE ROLE migrator LOGIN PASSWORD 'migrator';

-- app: usado pela API e pelos jobs; NÃO pode ignorar o RLS
CREATE ROLE app LOGIN PASSWORD 'app' NOBYPASSRLS;

-- =========================================================
-- Bancos
-- =========================================================
CREATE DATABASE app OWNER migrator;
CREATE DATABASE warehouse OWNER migrator;

-- =========================================================
-- Permissões no banco app
-- =========================================================
\connect app

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO app;

-- Toda tabela que o migrator criar no futuro já nasce acessível ao app
ALTER DEFAULT PRIVILEGES FOR ROLE migrator IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app;
ALTER DEFAULT PRIVILEGES FOR ROLE migrator IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO app;