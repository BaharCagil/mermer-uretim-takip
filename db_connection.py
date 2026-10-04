import pyodbc
import pandas as pd

# Docker üzerindeki SQL Server bağlantı bilgileri
DB_CONFIG = {
    'server': 'localhost,1433',
    'database': 'MermerUretimVT',
    'username': 'sa',
    'password': 'Bahar_Sql_2026!',
    'driver': '{ODBC Driver 18 for SQL Server}'
}

def get_connection():
    """SQL Server veritabanı bağlantısı oluşturur."""
    try:
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

def run_query(query, params=None):
    """SQL SELECT sorgularını çalıştırıp Pandas DataFrame olarak döner."""
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            print(f"Sorgu çalıştırma hatası: {e}")
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

def execute_sp(sp_name, params):
    """Saklı Yordamları (Stored Procedure) çalıştırır."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"EXEC {sp_name} " + ", ".join(["?"] * len(params)), params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Stored Procedure çalıştırma hatası: {e}")
            conn.close()
            return False
    return False

# Bağlantıyı test et
if __name__ == '__main__':
    print("Veritabanı bağlantısı test ediliyor...")
    test_df = run_query("SELECT * FROM Bloklar")
    print("Bağlantı Başarılı! Bloklar Tablosu:")
    print(test_df)
