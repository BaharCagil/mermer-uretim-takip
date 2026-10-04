-- =======================================================
-- Proje: Mermer Üretim & Stok Takip Sistemi
-- Modül: Veritabanı Şeması, Tablolar ve Saklı Yordamlar
-- Yazarlar: Bahar Çağıl
-- =======================================================

-- 1. Veritabanı Oluşturma (Eğer Yoksa)
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'MermerUretimVT')
BEGIN
    CREATE DATABASE MermerUretimVT;
END
GO

USE MermerUretimVT;
GO

-- 2. Mermer Blokları Tablosu (Ham Madde)
IF OBJECT_ID('dbo.Bloklar', 'U') IS NULL
CREATE TABLE Bloklar (
    BlokID INT IDENTITY(1,1) PRIMARY KEY,
    BlokKod VARCHAR(50) NOT NULL UNIQUE,
    MermerTuru VARCHAR(50) NOT NULL, -- Örn: Elazığ Vişne, Afyon Beyazı
    OcaktanGelisTarihi DATE DEFAULT GETDATE(),
    En_cm DECIMAL(10,2),
    Boy_cm DECIMAL(10,2),
    Yukseklik_cm DECIMAL(10,2),
    Agirlik_Ton DECIMAL(10,2),
    Durum VARCHAR(20) DEFAULT 'Ham' -- Ham, Kesildi, Isleniyor
);
GO

-- 3. Kesilen Plakalar Tablosu (İşlenmiş Ürün)
IF OBJECT_ID('dbo.Plakalar', 'U') IS NULL
CREATE TABLE Plakalar (
    PlakaID INT IDENTITY(1,1) PRIMARY KEY,
    BlokID INT FOREIGN KEY REFERENCES Bloklar(BlokID),
    PlakaKod VARCHAR(50) NOT NULL UNIQUE,
    Kalinlik_cm DECIMAL(5,2),
    En_cm DECIMAL(10,2),
    Boy_cm DECIMAL(10,2),
    YuzeyIslemi VARCHAR(50) DEFAULT 'Cilali', -- Cilali, Honlu, Fircali
    Durum VARCHAR(20) DEFAULT 'Stokta' -- Stokta, Kasalandi, Satildi
);
GO

-- 4. Ahşap Kasalar Tablosu (Paketleme/Lojistik)
IF OBJECT_ID('dbo.Kasalar', 'U') IS NULL
CREATE TABLE Kasalar (
    KasaID INT IDENTITY(1,1) PRIMARY KEY,
    KasaKod VARCHAR(50) NOT NULL UNIQUE,
    KasaTipi VARCHAR(50) DEFAULT 'Ahsap Standart',
    OlusturmaTarihi DATETIME DEFAULT GETDATE(),
    ToplamPlakaSayisi INT DEFAULT 0,
    ToplamAlan_m2 DECIMAL(10,2) DEFAULT 0,
    Durum VARCHAR(20) DEFAULT 'Acik' -- Acik, Kapandi, Sevkedildi
);
GO

-- 5. Kasa Detay Tablosu (Çoktan Çoka Eşleme)
IF OBJECT_ID('dbo.KasaDetay', 'U') IS NULL
CREATE TABLE KasaDetay (
    KasaDetayID INT IDENTITY(1,1) PRIMARY KEY,
    KasaID INT FOREIGN KEY REFERENCES Kasalar(KasaID),
    PlakaID INT FOREIGN KEY REFERENCES Plakalar(PlakaID),
    EklemeTarihi DATETIME DEFAULT GETDATE()
);
GO

-- 6. Otomatik Kasalama ve m2 Hesaplama Saklı Yordamı (Stored Procedure)
CREATE OR ALTER PROCEDURE sp_PlakaKasala
    @PlakaID INT,
    @KasaID INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Plaka durumunu güncelle
    UPDATE Plakalar 
    SET Durum = 'Kasalandi' 
    WHERE PlakaID = @PlakaID;

    -- KasaDetay tablosuna ekle
    INSERT INTO KasaDetay (KasaID, PlakaID)
    VALUES (@KasaID, @PlakaID);

    -- Kasa toplam metrekare ve adet bilgilerini otomatik güncelle
    UPDATE Kasalar
    SET ToplamPlakaSayisi = ToplamPlakaSayisi + 1,
        ToplamAlan_m2 = ToplamAlan_m2 + (
            SELECT (En_cm * Boy_cm / 10000.0) 
            FROM Plakalar WHERE PlakaID = @PlakaID
        )
    WHERE KasaID = @KasaID;
END;
GO
