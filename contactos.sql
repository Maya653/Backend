-- Crear la tabla de contactos
CREATE TABLE  IF NOT EXISTS contactos (
    email TEXT PRIMARY KEY,
    nombre TEXT,
    telefono TEXT
);

-- Insertar datos de ejemplo
INSERT INTO contactos (email, nombre, telefono)
VALUES ('juan@example.com', 'Juan Pérez', '555-123-4567');

INSERT INTO contactos (email, nombre, telefono)
VALUES ('maria@example.com', 'María García', '555-678-9012');



-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    username VARCHAR(50) PRIMARY KEY,
    hashed_password TEXT NOT NULL,
    token TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de ejemplo
INSERT INTO usuarios (username, hashed_password, token) VALUES ('maya@gmail.com', 'hashed_password_here', 'baOOpU8D-2ulZClC3KkZYgrCKeQwpanCnak4FKKXGis');
INSERT INTO usuarios (username, hashed_password, token) VALUES ('obed@gmail.com', 'hashed_password_here', '96hZm1G-1sG_TKGjRp3_yRrrFx-afhXXgSakGBvBPoc');
