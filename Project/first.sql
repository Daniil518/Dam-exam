CREATE DATABASE IF NOT EXISTS altunin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE altunin;

DROP TABLE IF EXISTS Material_products_import;
DROP TABLE IF EXISTS Product_import;
DROP TABLE IF EXISTS Product_type_import;
DROP TABLE IF EXISTS Materials_import;
DROP TABLE IF EXISTS Material_type_import;

CREATE TABLE Material_type_import (
    MaterialTypeID INT AUTO_INCREMENT PRIMARY KEY,
    TypeName VARCHAR(100) NOT NULL UNIQUE,
    LossPercent DECIMAL(5,4) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

INSERT INTO Material_type_import (TypeName, LossPercent) VALUES
('Дерево', 0.0055),
('Древесно-стружечная плита', 0.0030),
('Текстиль', 0.0015),
('Стекло', 0.0045),
('Металл', 0.0010),
('Пластик', 0.0005),
('Другой', 0.0000);

CREATE TABLE Materials_import (
    MaterialID INT AUTO_INCREMENT PRIMARY KEY,
    MaterialTypeID INT NOT NULL,
    Name VARCHAR(150) NOT NULL UNIQUE,
    Description TEXT,
    UnitPrice DECIMAL(10,2) NOT NULL CHECK (UnitPrice >= 0),
    Quantity INT NOT NULL CHECK (Quantity >= 0),
    MinQuantity INT NOT NULL CHECK (MinQuantity >= 0),
    PackageQuantity INT NOT NULL CHECK (PackageQuantity > 0),
    Unit VARCHAR(20) NOT NULL,
    FOREIGN KEY (MaterialTypeID) REFERENCES Material_type_import(MaterialTypeID) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Product_type_import (
    ProductTypeID INT AUTO_INCREMENT PRIMARY KEY,
    TypeName VARCHAR(100) NOT NULL UNIQUE,
    Coefficient DECIMAL(5,2) NOT NULL DEFAULT 1.00
) ENGINE=InnoDB;

INSERT INTO Product_type_import (TypeName, Coefficient) VALUES
('Кресла', 1.95),
('Полки', 2.50),
('Стеллажи', 4.35),
('Столы', 5.50),
('Тумбы', 7.60),
('Шкафы', 6.72),
('Другой', 1.00);

CREATE TABLE Product_import (
    ProductID INT AUTO_INCREMENT PRIMARY KEY,
    ProductTypeID INT NOT NULL,
    Name VARCHAR(150) NOT NULL UNIQUE,
    SKU VARCHAR(50) NOT NULL UNIQUE,
    MinPartnerPrice DECIMAL(10,2) NOT NULL CHECK (MinPartnerPrice >= 0),
    Description TEXT,
    FOREIGN KEY (ProductTypeID) REFERENCES Product_type_import(ProductTypeID) ON DELETE RESTRICT
) ENGINE=InnoDB;

INSERT INTO Product_import (ProductTypeID, Name, SKU, MinPartnerPrice, Description) VALUES
(1, 'Кресло офисное', 'SKU001', 4500.00, 'Удобное офисное кресло'),
(1, 'Кресло руководителя', 'SKU002', 7500.00, 'Кресло с кожаной отделкой'),
(2, 'Полка настенная', 'SKU003', 1200.00, 'Полка из дерева'),
(2, 'Полка угловая', 'SKU004', 1500.00, 'Угловая полка для хранения'),
(3, 'Стеллаж металлический', 'SKU005', 3500.00, 'Прочный металлический стеллаж'),
(3, 'Стеллаж деревянный', 'SKU006', 4000.00, 'Стеллаж из массива дерева'),
(4, 'Стол офисный', 'SKU007', 5000.00, 'Стол для офиса'),
(4, 'Стол переговорный', 'SKU008', 12000.00, 'Большой переговорный стол'),
(5, 'Тумба под офисный стол', 'SKU009', 2500.00, 'Тумба с ящиками'),
(5, 'Тумба мобильная', 'SKU010', 2700.00, 'Тумба на колесах'),
(6, 'Шкаф для документов', 'SKU011', 8000.00, 'Шкаф с замком'),
(6, 'Шкаф офисный', 'SKU012', 9000.00, 'Большой офисный шкаф'),
(1, 'Кресло посетителя', 'SKU013', 3200.00, 'Кресло для посетителей'),
(2, 'Полка для книг', 'SKU014', 1300.00, 'Полка для хранения книг'),
(3, 'Стеллаж для архивов', 'SKU015', 4500.00, 'Стеллаж для документов'),
(4, 'Стол компьютерный', 'SKU016', 4800.00, 'Стол для компьютера'),
(5, 'Тумба приставная', 'SKU017', 2600.00, 'Тумба приставная к столу'),
(6, 'Шкаф для одежды', 'SKU018', 8500.00, 'Шкаф для верхней одежды'),
(1, 'Кресло геймерское', 'SKU019', 10000.00, 'Кресло для геймеров'),
(2, 'Полка декоративная', 'SKU020', 1100.00, 'Декоративная полка'),
(3, 'Стеллаж для выставки', 'SKU021', 5000.00, 'Стеллаж для экспозиции');

CREATE TABLE Material_products_import (
    ProductID INT NOT NULL,
    MaterialID INT NOT NULL,
    QuantityRequired INT NOT NULL CHECK (QuantityRequired > 0),
    PRIMARY KEY (ProductID, MaterialID),
    FOREIGN KEY (ProductID) REFERENCES Product_import(ProductID) ON DELETE CASCADE,
    FOREIGN KEY (MaterialID) REFERENCES Materials_import(MaterialID) ON DELETE CASCADE
) ENGINE=InnoDB;
