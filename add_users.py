from db_connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Kullanıcılar tablosunu oluştur
cursor.execute("""
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Kullanicilar' and xtype='U')
CREATE TABLE Kullanicilar (
    KullaniciID INT IDENTITY(1,1) PRIMARY KEY,
    KullaniciAdi VARCHAR(50) UNIQUE NOT NULL,
    Sifre VARCHAR(50) NOT NULL,
    Yetki VARCHAR(20) NOT NULL -- 'Yönetici' veya 'Operatör'
)
""")

# Örnek Kullanıcıları Ekle (Eğer tablo boşsa)
cursor.execute("""
IF NOT EXISTS (SELECT 1 FROM Kullanicilar)
BEGIN
    INSERT INTO Kullanicilar (KullaniciAdi, Sifre, Yetki) VALUES 
    ('admin', '1234', 'Yönetici'),
    ('saha_isci', '0000', 'Operatör')
END
""")

conn.commit()
conn.close()
print("Kullanıcılar tablosu ve örnek roller başarıyla eklendi!")
