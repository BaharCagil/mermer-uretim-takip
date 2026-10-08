import pymssql
import pandas as pd

# Docker SQL Server Bağlantı Bilgileri
SERVER = '127.0.0.1'
PORT = 1433
USER = 'sa'
PASSWORD = 'Bahar_Sql_2026!'
DATABASE = 'MermerUretimVT'  # Veritabanı adı doğrulandı

def get_connection():
    try:
        conn = pymssql.connect(
            server=SERVER,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

def run_query(query):
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Sorgu çalıştırma hatası: {e}")
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

def execute_sp(sp_name, params):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            placeholders = ", ".join(["%s"] * len(params))
            query = f"EXEC {sp_name} {placeholders}"
            cursor.execute(query, tuple(params))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Stored Procedure çalıştırma hatası: {e}")
            conn.close()
            return False
    return False

if __name__ == '__main__':
    print("MermerUretimVT veritabanına bağlanılıyor...")
    test_df = run_query("SELECT * FROM Bloklar")
    print("\n--- Bloklar Tablosu ---")
    print(test_df)
