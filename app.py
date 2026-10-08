import pandas as pd
import streamlit as st
from db_connection import execute_sp, get_connection, run_query

st.set_page_config(page_title="Mermer Üretim & Stok Takip ERP", layout="wide")

st.title("🪨 Mermer Üretim & Stok Takip ERP")
st.caption("Veri Tabanı Yönetim Sistemleri Projesi - T-SQL Entegre")

menu = ["Blok Yönetimi", "Plaka Kesim & Stok", "Kasalama & Sevkiyat"]
choice = st.sidebar.selectbox("Modül Seçin", menu)

# ---------------------------------------------------------
# 1. BLOK YÖNETİMİ
# ---------------------------------------------------------
if choice == "Blok Yönetimi":
  st.header("🪨 Blok Yönetimi")

  col1, col2 = st.columns(2)
  with col1:
    blok_kod = st.text_input("Blok Kodu", value="BLK-2026-001")
    mermer_turu = st.selectbox(
        "Mermer Türü",
        ["Elazığ Vişne", "Afyon Beyaz", "Muğla Beyaz", "Traverten"],
    )
    agirlik = st.number_input(
        "Ağırlık (Ton)", min_value=0.1, value=18.5, step=0.1
    )
  with col2:
    en = st.number_input("En (cm)", min_value=1, value=150)
    boy = st.number_input("Boy (cm)", min_value=1, value=280)
    yukseklik = st.number_input("Yükseklik (cm)", min_value=1, value=140)

  if st.button("➕ Yeni Blok Kaydet"):
    conn = get_connection()
    if conn:
      try:
        cursor = conn.cursor()
        cursor.execute(
            """
                    INSERT INTO Bloklar (BlokKod, MermerTuru, En_cm, Boy_cm, Yukseklik_cm, Agirlik_Ton)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
            (blok_kod, mermer_turu, en, boy, yukseklik, agirlik),
        )
        conn.commit()
        conn.close()
        st.success(
            f"✅ {blok_kod} kodlu blok veritabanına başarıyla kaydedildi!"
        )
        st.rerun()
      except Exception as e:
        st.error(f"Kayıt Hatası: {e}")
    else:
      st.error("Veritabanı bağlantısı kurulamadı!")

  st.divider()
  st.subheader("📋 Kayıtlı Bloklar")
  df_bloklar = run_query("SELECT * FROM Bloklar")
  st.dataframe(df_bloklar, width="stretch")

# ---------------------------------------------------------
# 2. PLAKA KESİM & STOK
# ---------------------------------------------------------
elif choice == "Plaka Kesim & Stok":
  st.header("🔪 Plaka Kesim & Stok")

  df_bloklar = run_query("SELECT BlokID, BlokKod FROM Bloklar")
  if df_bloklar.empty:
    st.warning(
        "Henüz sisteme kayıtlı bir blok yok. Önce Blok Yönetimi sekmesinden"
        " blok ekleyin."
    )
  else:
    blok_opts = dict(zip(df_bloklar["BlokKod"], df_bloklar["BlokID"]))
    secilen_blok = st.selectbox("Kesilecek Blok", list(blok_opts.keys()))

    col1, col2 = st.columns(2)
    with col1:
      plaka_kod = st.text_input("Plaka Kodu", value="PLK-101")
      yuzey = st.selectbox(
          "Yüzey İşlemi", ["Cilalı", "Honlu", "Eskitme", "Ham"]
      )
      kalinlik = st.number_input(
          "Kalınlık (cm)", min_value=0.5, value=2.0, step=0.5
      )
    with col2:
      en = st.number_input("Plaka En (cm)", min_value=1, value=120)
      boy = st.number_input("Plaka Boy (cm)", min_value=1, value=240)
      m2 = (en * boy) / 10000.0
      st.info(f"Hesaplanan Metrekare: **{m2:.2f} m²**")

    if st.button("🔪 Plaka Ekle"):
      conn = get_connection()
      if conn:
        try:
          cursor = conn.cursor()
          cursor.execute(
              """
                        INSERT INTO Plakalar (BlokID, PlakaKod, YuzeyIslemi, Kalinlik_cm, En_cm, Boy_cm, Durum)
                        VALUES (%s, %s, %s, %s, %s, %s, 'Stokta')
                    """,
              (
                  blok_opts[secilen_blok],
                  plaka_kod,
                  yuzey,
                  kalinlik,
                  en,
                  boy,
              ),
          )
          conn.commit()
          conn.close()
          st.success(f"✅ {plaka_kod} plakası stoğa eklendi!")
          st.rerun()
        except Exception as e:
          st.error(f"Plaka Ekleme Hatası: {e}")
      else:
        st.error("Veritabanı bağlantısı kurulamadı!")

  st.divider()
  st.subheader("📋 Stoktaki Plakalar")
  df_plakalar = run_query("SELECT * FROM Plakalar")
  st.dataframe(df_plakalar, width="stretch")

# ---------------------------------------------------------
# 3. KASALAMA & SEVKİYAT
# ---------------------------------------------------------
elif choice == "Kasalama & Sevkiyat":
  st.header("📦 Kasalama & Sevkiyat")

  col1, col2 = st.columns(2)
  with col1:
    st.subheader("1. Yeni Kasa Oluştur")
    kasa_kod = st.text_input("Kasa Kodu", value="KSA-001")
    if st.button("📦 Kasa Aç"):
      conn = get_connection()
      if conn:
        try:
          cursor = conn.cursor()
          cursor.execute(
              """
              INSERT INTO Kasalar (KasaKod, ToplamAlan_m2, Durum)
              VALUES (%s, 0.0, 'Açık')
              """,
              (kasa_kod,),
          )
          conn.commit()
          conn.close()
          st.success(f"✅ {kasa_kod} kasası açıldı!")
          st.rerun()
        except Exception as e:
          st.error(f"Kasa Açma Hatası: {e}")

  with col2:
    st.subheader("2. Plakayı Kasaya Yerleştir (T-SQL SP)")
    df_acik_kasalar = run_query(
        "SELECT KasaID, KasaKod FROM Kasalar WHERE Durum = 'Açık'"
    )
    df_stok_plakalar = run_query(
        "SELECT PlakaID, PlakaKod FROM Plakalar WHERE Durum = 'Stokta'"
    )

    if not df_acik_kasalar.empty and not df_stok_plakalar.empty:
      kasa_opts = dict(
          zip(df_acik_kasalar["KasaKod"], df_acik_kasalar["KasaID"])
      )
      plaka_opts = dict(
          zip(df_stok_plakalar["PlakaKod"], df_stok_plakalar["PlakaID"])
      )

      secilen_kasa = st.selectbox("Hedef Kasa", list(kasa_opts.keys()))
      secilen_plaka = st.selectbox(
          "Yerleştirilecek Plaka", list(plaka_opts.keys())
      )

      if st.button("📦 Plakayı Kasala (T-SQL SP Çalıştır)"):
        res = execute_sp(
            "sp_PlakaKasala",
            [plaka_opts[secilen_plaka], kasa_opts[secilen_kasa]],
        )
        if res:
          st.success(
              f"🎉 {secilen_plaka} plakası {secilen_kasa} kasasına yerleştirildi"
              " ve m² otomatik hesaplandı!"
          )
          st.rerun()
    else:
      st.info(
          "Kasalama yapmak için en az 1 açık kasa ve 1 stokta plaka gereklidir."
      )

  st.divider()
  st.subheader("📦 Kasalar ve Metrekare (m²) Durumu")
  df_kasalar = run_query("SELECT * FROM Kasalar")
  st.dataframe(df_kasalar, width="stretch")
