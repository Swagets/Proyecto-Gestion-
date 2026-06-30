-- Crear base de datos
CREATE DATABASE IF NOT EXISTS PowerMedical;
USE PowerMedical;

-- Tabla Rol
CREATE TABLE Rol (
    idRol INT AUTO_INCREMENT PRIMARY KEY,
    nombreRol VARCHAR(50) NOT NULL
);

-- Tabla Usuario
CREATE TABLE Usuario (
    idUsuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE,
    idRol INT,
    FOREIGN KEY (idRol) REFERENCES Rol(idRol)
);

-- Tabla Proveedor
CREATE TABLE Proveedor (
    idProveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombreProveedor VARCHAR(100) NOT NULL,
    contacto VARCHAR(100)
);

-- Tabla Categoría
CREATE TABLE Categoria (
    idCategoria INT AUTO_INCREMENT PRIMARY KEY,
    nombreCategoria VARCHAR(100) NOT NULL
);

-- Tabla Producto
CREATE TABLE Producto (
    idProducto INT AUTO_INCREMENT PRIMARY KEY,
    nombreProducto VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    idProveedor INT,
    idCategoria INT,
    FOREIGN KEY (idProveedor) REFERENCES Proveedor(idProveedor),
    FOREIGN KEY (idCategoria) REFERENCES Categoria(idCategoria)
);

-- Tabla Compra
CREATE TABLE Compra (
    idCompra INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    idUsuario INT,
    idProveedor INT,
    FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario),
    FOREIGN KEY (idProveedor) REFERENCES Proveedor(idProveedor)
);

-- Tabla DetalleCompra
CREATE TABLE DetalleCompra (
    idDetalleCompra INT AUTO_INCREMENT PRIMARY KEY,
    idCompra INT,
    idProducto INT,
    cantidad INT NOT NULL,
    precioUnitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (idCompra) REFERENCES Compra(idCompra),
    FOREIGN KEY (idProducto) REFERENCES Producto(idProducto)
);

-- Tabla Cliente
CREATE TABLE Cliente (
    idCliente INT AUTO_INCREMENT PRIMARY KEY,
    nombreCliente VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE
);

-- Tabla Venta
CREATE TABLE Venta (
    idVenta INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    idUsuario INT,
    idCliente INT,
    FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario),
    FOREIGN KEY (idCliente) REFERENCES Cliente(idCliente)
);

-- Tabla DetalleVenta
CREATE TABLE DetalleVenta (
    idDetalleVenta INT AUTO_INCREMENT PRIMARY KEY,
    idVenta INT,
    idProducto INT,
    cantidad INT NOT NULL,
    precioUnitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (idVenta) REFERENCES Venta(idVenta),
    FOREIGN KEY (idProducto) REFERENCES Producto(idProducto)
);
