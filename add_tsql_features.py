from db_connection import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    # 1. TRIGGER (Tetikleyici): Kasa kapasitesi (30 m2) dolduğunda otomatik kapatır
    cursor.execute("""
    CREATE OR ALTER TRIGGER trg_KasaKapasiteKontrol
    ON Kasalar
    AFTER UPDATE
    AS
    BEGIN
        IF UPDATE(ToplamAlan_m2)
        BEGIN
            UPDATE Kasalar
            SET Durum = 'Kapalı'
            FROM Kasalar k
            INNER JOIN inserted i ON k.KasaID = i.KasaID
            WHERE i.ToplamAlan_m2 >= 30.0 AND i.Durum = 'Açık'
        END
    END
    """)
    print("✅ T-SQL Trigger: 'trg_KasaKapasiteKontrol' başarıyla oluşturuldu.")

      # 2. VIEW (Görünüm): Blok ve Plaka Üretim/Stok Raporu
    cursor.execute("""
    CREATE OR ALTER VIEW vw_UretimVerimlilikRaporu AS
    SELECT 
        b.BlokKod,
        b.MermerTuru,
        b.Agirlik_Ton,
        COUNT(p.PlakaID) AS ToplamKesilenPlaka,
        SUM(CASE WHEN p.Durum = 'Stokta' THEN 1 ELSE 0 END) AS StoktakiPlakaSayisi
    FROM Bloklar b
    LEFT JOIN Plakalar p ON b.BlokID = p.BlokID
    GROUP BY b.BlokKod, b.MermerTuru, b.Agirlik_Ton
    """)
    print("✅ T-SQL View: 'vw_UretimVerimlilikRaporu' başarıyla oluşturuldu.")

    conn.commit()
except Exception as e:
    print(f"Hata oluştu: {e}")
finally:
    conn.close()
