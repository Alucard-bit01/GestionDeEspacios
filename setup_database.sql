/* 
   SCRIPT DE CONFIGURACIÓN DE BASE DE DATOS PARA "PROYECTO INTEGRADORA"
   Este script debe ser ejecutado en SQL Server Management Studio (SSMS).
   Crea la base de datos, configura la seguridad y define las tablas del proyecto.
*/

USE master;
GO

-- 1. CREACIÓN DE LA BASE DE DATOS
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'Integradora')
BEGIN
    CREATE DATABASE Integradora;
    PRINT 'Base de datos [Integradora] creada.';
END
ELSE
BEGIN
    PRINT 'La base de datos [Integradora] ya existe.';
END
GO

USE Integradora;
GO

-- 2. CONFIGURACIÓN DE SEGURIDAD (USER: ALEXIS\jajas)
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'ALEXIS\jajas')
BEGIN
    CREATE LOGIN [ALEXIS\jajas] FROM WINDOWS;
    PRINT 'Login [ALEXIS\jajas] creado.';
END

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'ALEXIS\jajas')
BEGIN
    CREATE USER [ALEXIS\jajas] FOR LOGIN [ALEXIS\jajas];
    PRINT 'Usuario de base de datos creado.';
END

ALTER ROLE db_owner ADD MEMBER [ALEXIS\jajas];
PRINT 'Permisos de db_owner asignados a [ALEXIS\jajas].';
GO

-- 3. CREACIÓN DE TABLAS (SCHEMA)

-- Tabla: Users
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[users]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[users] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [username] NVARCHAR(150) NOT NULL UNIQUE,
        [password] NVARCHAR(512) NOT NULL,
        [profile_picture] NVARCHAR(255) DEFAULT 'default.svg'
    );
    PRINT 'Tabla [users] creada.';
END
GO

-- Tabla: Classrooms
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[classrooms]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[classrooms] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [name] NVARCHAR(50) NOT NULL
    );
    PRINT 'Tabla [classrooms] creada.';
END
GO

-- Tabla: Reservations
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[reservations]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[reservations] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [user_id] INT NOT NULL,
        [classroom_id] INT NOT NULL,
        [start_time] DATETIME NOT NULL,
        [end_time] DATETIME NOT NULL,
        CONSTRAINT FK_Reservation_User FOREIGN KEY (user_id) REFERENCES [users](id),
        CONSTRAINT FK_Reservation_Classroom FOREIGN KEY (classroom_id) REFERENCES [classrooms](id)
    );
    PRINT 'Tabla [reservations] creada.';
END
GO

-- Tabla: Messages
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[messages]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[messages] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [sender_id] INT NOT NULL,
        [recipient_id] INT NOT NULL,
        [body] NVARCHAR(MAX) NOT NULL,
        [timestamp] DATETIME DEFAULT GETDATE(),
        [is_read] BIT DEFAULT 0,
        CONSTRAINT FK_Message_Sender FOREIGN KEY (sender_id) REFERENCES [users](id),
        CONSTRAINT FK_Message_Recipient FOREIGN KEY (recipient_id) REFERENCES [users](id)
    );
    PRINT 'Tabla [messages] creada.';
END
GO

-- 4. DATOS INICIALES (OPCIONAL)
-- Agregamos algunas aulas por defecto si la tabla está vacía
IF NOT EXISTS (SELECT 1 FROM [dbo].[classrooms])
BEGIN
    INSERT INTO [dbo].[classrooms] ([name]) VALUES ('Aula 101'), ('Aula 102'), ('Laboratorio A'), ('Sala de Juntas');
    PRINT 'Datos iniciales insertados en [classrooms].';
END
GO

PRINT '--- CONFIGURACIÓN FINALIZADA CON ÉXITO ---';
