import streamlit as st
import pandas as pd
from db_connection import run_query, execute_sp, get_connection

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Mermer Üretim & Stok Takip ERP",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Mermer Üretim & Stok Takip Sistemi")
st.caption("T-SQL & Python (Streamlit) Tabanlı ERP Uygulaması")

# Yan Menü (Sidebar)
menu = st.sidebar.radio(
    "Modül Seçiniz",
    ["📊 Genel Bakış (Dashboard)", "🪨 Blok Yönetimi", "🔪 Plaka Kesim & Stok", "📦 Kasalama & Sevkiyat"]
)

# -------------------------------------------------------------
# 1. MODÜL: GENEL BAKIŞ (DASHBOARD)
# -------------------------------------------------------------
if menu == "📊 Genel Bakış (Dashboard)":
    st.header("📊 Fabrika Genel Durum Özeti")
    
    col1, col2, col3 = st.columns(3)
    
    df_blok = run_query("SELECT COUNT(*) AS ToplamBlok FROM Bloklar")
    df_plaka = run_query("SELECT COUNT(*) AS ToplamPlaka FROM Plakalar WHERE Durum = 'Stokta'")
    df_kasa = run_query("SELECT COUNT(*) AS ToplamKasa FROM Kasalar WHERE Durum = 'Acik'")
    
    toplam_blok = df_blok['ToplamBlok'].iloc[0] if not df_blok.empty else 0
    toplam_plaka = df_plaka['ToplamPlaka'].iloc[0] if not df_plaka.empty else 0
    toplam_kasa = df_kasa['ToplamKasa'].iloc[0] if not df_kasa.empty else 0
    
    col1.metric("Depodaki Ham Blok", f"{toplam_blok} Adet")
    col2.metric("Stoktaki İşlenmiş Plaka", f"{toplam_plaka} Adet")
    col3.metric("Açık Ahşap Kasa", f"{toplam_kasa} Adet")
    
    st.divider()
    st.subheader("📋 Son Eklenen Mermer Blokları")
    df_bloklar_all = run_query("SELECT * FROM Bloklar ORDER BY BlokID DESC")
    st.dataframe(df_bloklar_all, use_container_width=True)

# -------------------------------------------------------------
# 2. MODÜL: BLOK YÖNETİMİ
# -------------------------------------------------------------
elif menu == "🪨 Blok Yönetimi":
    st.header("🪨 Ham Mermer Blok Girişi")
    
    with st.form("blok_ekle_formu", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            blok_kod = st.text_input("Blok Kodu (Örn: BLK-2026-001)")
            mermer_turu = st.selectbox("Mermer Türü", ["Elazığ Vişne", "Afyon Beyazı", "Muğla Beyazı", "Bursa Siyahı"])
            agirlik = st.number_input("Ağırlık (Ton)", min_value=0.0, step=0.5)
            
        with col2:
            en = st.number_input("En (cm)", min_value=0.0, step=10.0)
            boy = st.number_input("Boy (cm)", min_value=0.0, step=10.0)
            yukseklik = st.number_input("Yükseklik (cm)", min_value=0.0, step=10.0)
            
        submit = st.form_submit_button("🔨 Yeni Blok Kaydet")
        
        if submit:
            if blok_kod and mermer_turu:
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO Bloklar (BlokKod, MermerTuru, En_cm, Boy_cm, Yukseklik_cm, Agirlik_Ton)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (blok_kod, mermer_turu, en, boy, yukseklik, agirlik))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ {blok_kod} kodlu blok veritabanına eklendi!")
                    st.rerun()
            else:
                st.warning("Lütfen zorunlu alanları doldurun.")
                
    st.divider()
    st.subheader("📑 Mevcut Blok Listesi")
    df_bloklar = run_query("SELECT * FROM Bloklar")
    st.dataframe(df_bloklar, use_container_width=True)

# -------------------------------------------------------------
# 3. MODÜL: PLAKA KESİM & STOK
# -------------------------------------------------------------
elif menu == "🔪 Plaka Kesim & Stok":
    st.header("🔪 Bloktan Plaka Kesim Kaydı")
    
    df_bloklar = run_query("SELECT BlokID, BlokKod FROM Bloklar")
    
    if df_bloklar.empty:
        st.info("Henüz sisteme tanımlı blok bulunmuyor. Önce 'Blok Yönetimi' modülünden blok ekleyin.")
    else:
        blok_dict = dict(zip(df_bloklar['BlokKod'], df_bloklar['BlokID']))
        
        with st.form("plaka_ekle_formu", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                secilen_blok_kod = st.selectbox("Kesilen Blok", list(blok_dict.keys()))
                plaka_kod = st.text_input("Plaka Kodu (Örn: PLK-101)")
                yuzey = st.selectbox("Yüzey İşlemi", ["Cilalı", "Honlu", "Fırçalı", "Eskitme"])
                
            with col2:
                kalinlik = st.number_input("Kalınlık (cm)", min_value=1.0, value=2.0, step=0.5)
                en = st.number_input("En (cm)", min_value=0.0, step=10.0)
                boy = st.number_input("Boy (cm)", min_value=0.0, step=10.0)
                
            submit_plaka = st.form_submit_button("⚙️ Plaka Ekle")
            
            if submit_plaka:
                if plaka_kod:
                    conn = get_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO Plakalar (BlokID, PlakaKod, Kalinlik_cm, En_cm, Boy_cm, YuzeyIslemi)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (blok_dict[secilen_blok_kod], plaka_kod, kalinlik, en, boy, yuzey))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ {plaka_kod} plakası stoğa eklendi!")
                        st.rerun()

    st.divider()
    st.subheader("📦 Stoktaki Plakalar")
    df_plakalar = run_query("""
        SELECT p.PlakaID, p.PlakaKod, b.BlokKod, b.MermerTuru, p.Kalinlik_cm, p.En_cm, p.Boy_cm, p.YuzeyIslemi, p.Durum
        FROM Plakalar p
        JOIN Bloklar b ON p.BlokID = b.BlokID
    """)
    st.dataframe(df_plakalar, use_container_width=True)

# -------------------------------------------------------------
# 4. MODÜL: KASALAMA & SEVKİYAT (STORED PROCEDURE KULLANIMI)
# -------------------------------------------------------------
elif menu == "📦 Kasalama & Sevkiyat":
    st.header("📦 Ahşap Kasalama (T-SQL Saklı Yordamı)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Yeni Kasa Oluştur")
        with st.form("kasa_olustur_form", clear_on_submit=True):
            kasa_kod = st.text_input("Kasa Kodu (Örn: KSA-001)")
            kasa_tipi = st.selectbox("Kasa Tipi", ["Ahşap Standart", "Ahşap Güçlendirilmiş", "Export Kasa"])
            submit_kasa = st.form_submit_button("📦 Kasa Aç")
            
            if submit_kasa and kasa_kod:
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Kasalar (KasaKod, KasaTipi) VALUES (?, ?)", (kasa_kod, kasa_tipi))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ {kasa_kod} kasası oluşturuldu.")
                    st.rerun()

    with col2:
        st.subheader("2. Kasaya Plaka Yerleştir (sp_PlakaKasala)")
        
        df_acik_kasalar = run_query("SELECT KasaID, KasaKod FROM Kasalar WHERE Durum = 'Acik'")
        df_stok_plakalar = run_query("SELECT PlakaID, PlakaKod FROM Plakalar WHERE Durum = 'Stokta'")
        
        if not df_acik_kasalar.empty and not df_stok_plakalar.empty:
            kasa_opts = dict(zip(df_acik_kasalar['KasaKod'], df_acik_kasalar['KasaID']))
            plaka_opts = dict(zip(df_stok_plakalar['PlakaKod'], df_stok_plakalar['PlakaID']))
            
            secilen_kasa = st.selectbox("Hedef Kasa", list(kasa_opts.keys()))
            secilen_plaka = st.selectbox("Yerleştirilecek Plaka", list(plaka_opts.keys()))
            
            if st.button("🔄 Plakayı Kasala (T-SQL SP Çalıştır)"):
                res = execute_sp("sp_PlakaKasala", [plaka_opts[secilen_plaka], kasa_opts[secilen_kasa]])
                if res:
                    st.success(f"🎉 {secilen_plaka} plakası {secilen_kasa} kasasına yerleştirildi ve m² otomatik hesaplandı!")
                    st.rerun()
        else:
            st.info("Kasalama yapmak için en az 1 açık kasa ve 1 stokta plaka gereklidir.")

    st.divider()
    st.subheader("📑 Kasalar ve Metrekare (m²) Durumu")
    df_kasalar = run_query("SELECT * FROM Kasalar")
    st.dataframe(df_kasalar, use_container_width=True)
