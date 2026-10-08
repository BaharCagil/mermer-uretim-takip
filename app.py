import altair as alt
import pandas as pd
import streamlit as st
from db_connection import execute_sp, get_connection, run_query

st.set_page_config(page_title="Mermer ERP", page_icon="🪨", layout="wide")

# --- LÜKS MERMER & ELAZIĞ VİŞNESİ KURUMSAL CSS ---
st.markdown("""
<style>
    /* Ana Sayfa: Koyu Damarlı Açık Mermer Dokusu */
    .stApp {
        background: radial-gradient(circle at 15% 20%, #f7f4f2 0%, #ece5e1 50%, #dfd5cf 100%) !important;
        color: #222222;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Sol Menü (Sidebar): Derin Elazığ Vişnesi / Bordo Arka Plan */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #420b12 0%, #2b060b 100%) !important;
    }
    [data-testid="stSidebar"] * {
        color: #fce8eb !important;
    }

    /* Selectbox (Açılır Liste) Okunabilirlik Düzeltmesi */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] span {
        color: #1a1a1a !important;
    }
    
    /* Metrik Kartları: Lüks Cam Efekti (Glassmorphism) ve Vişne Vurgusu */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.75) !important;
        border: 1px solid rgba(106, 17, 40, 0.2) !important;
        border-left: 6px solid #6A1128 !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 8px 24px rgba(106, 17, 40, 0.08) !important;
        backdrop-filter: blur(8px);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #555555 !important;
    }
    [data-testid="stMetricValue"] {
        color: #420b12 !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
    }

    /* Butonlar: Elazığ Vişnesi Dolgulu, Gölge Efektli Kurumsal Buton */
    .stButton>button {
        background: linear-gradient(135deg, #6A1128 0%, #4a0b1b 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 14px rgba(106, 17, 40, 0.35) !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #7e1531 0%, #580c20 100%) !important;
        box-shadow: 0 6px 20px rgba(106, 17, 40, 0.5) !important;
        transform: translateY(-1px);
    }

    /* Tablolar (Dataframe) ve Konteynerlar */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #d4c7c0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        background: #ffffff;
    }

    /* Başlık Çizgileri */
    h1, h2, h3 {
        color: #3b080f !important;
        letter-spacing: -0.5px;
    }
</style>
""", unsafe_allow_html=True)

# --- KİMLİK DOĞRULAMA (LOGIN) SİSTEMİ ---
if 'giris_yapildi' not in st.session_state:
    st.session_state['giris_yapildi'] = False
    st.session_state['yetki'] = ""
    st.session_state['kullanici'] = ""

if not st.session_state['giris_yapildi']:
    st.markdown("<h1 style='text-align: center; color: #3b080f;'>🪨 Mermer Üretim ERP</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sisteme erişmek için giriş yapınız.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            k_adi = st.text_input("Kullanıcı Adı")
            sifre = st.text_input("Şifre", type="password")
            submit = st.form_submit_button("Giriş Yap", use_container_width=True)
            
            if submit:
                df_user = run_query(f"SELECT Yetki FROM Kullanicilar WHERE KullaniciAdi='{k_adi}' AND Sifre='{sifre}'")
                if not df_user.empty:
                    st.session_state['giris_yapildi'] = True
                    st.session_state['yetki'] = df_user.iloc[0]['Yetki']
                    st.session_state['kullanici'] = k_adi
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre!")
    st.stop()

# --- ANA UYGULAMA (Giriş Başarılı) ---
st.sidebar.success(f"👤 Hoş geldin, {st.session_state['kullanici']} - Yetki: {st.session_state['yetki']}")
if st.sidebar.button("🚪 Çıkış Yap"):
    st.session_state['giris_yapildi'] = False
    st.rerun()

st.title("🪨 Mermer Üretim ve Stok Takip ERP")

# YETKİYE GÖRE MENÜ KONTROLÜ
if st.session_state['yetki'] == 'Yönetici':
    menu = ["Yönetici Özeti", "Blok Yönetimi", "Plaka Kesim ve Stok", "Kasalama ve Sevkiyat"]
else:
    menu = ["Blok Yönetimi", "Plaka Kesim ve Stok", "Kasalama ve Sevkiyat"]

choice = st.sidebar.selectbox("Modül Seçin", menu)

# ---------------------------------------------------------
# 0. YÖNETİCİ ÖZETİ
# ---------------------------------------------------------
if choice == "Yönetici Özeti":
    st.header("📊 Yönetici Özeti")
    st.markdown("İşletmenin anlık üretim, stok ve sevkiyat durum raporu.")

    col1, col2, col3 = st.columns(3)
    
    df_blok = run_query("SELECT COUNT(*) as Adet, SUM(Agirlik_Ton) as Tonaj FROM Bloklar")
    blok_adet = df_blok.iloc[0]['Adet'] if not df_blok.empty and pd.notna(df_blok.iloc[0]['Adet']) else 0
    blok_tonaj = df_blok.iloc[0]['Tonaj'] if not df_blok.empty and pd.notna(df_blok.iloc[0]['Tonaj']) else 0

    df_plaka = run_query("SELECT COUNT(*) as Adet, SUM(CAST(En_cm AS FLOAT) * CAST(Boy_cm AS FLOAT) / 10000.0) as ToplamM2 FROM Plakalar WHERE Durum = 'Stokta'")
    plaka_adet = df_plaka.iloc[0]['Adet'] if not df_plaka.empty and pd.notna(df_plaka.iloc[0]['Adet']) else 0
    plaka_m2 = df_plaka.iloc[0]['ToplamM2'] if not df_plaka.empty and pd.notna(df_plaka.iloc[0]['ToplamM2']) else 0

    df_kasa = run_query("SELECT COUNT(*) as Adet FROM Kasalar WHERE Durum = 'Açık'")
    kasa_adet = df_kasa.iloc[0]['Adet'] if not df_kasa.empty and pd.notna(df_kasa.iloc[0]['Adet']) else 0

    with col1:
        st.metric(label="🪨 Toplam İşlenen Blok", value=f"{blok_adet} Adet", delta=f"{blok_tonaj:.1f} Ton Hacim")
    with col2:
        st.metric(label="🔪 Stoktaki Plaka (m²)", value=f"{plaka_m2:.2f} m²", delta=f"{plaka_adet} Adet Kesilmiş Plaka")
    with col3:
        st.metric(label="📦 Sevkiyat Bekleyen Kasa", value=f"{kasa_adet} Kasa", delta="Açık Durumda", delta_color="off")

    st.divider()

    col_grafik1, col_grafik2 = st.columns(2)
    
    with col_grafik1:
        st.subheader("Mermer Türüne Göre Blok Dağılımı")
        df_tur = run_query("SELECT MermerTuru, COUNT(*) as Adet FROM Bloklar GROUP BY MermerTuru")
        if not df_tur.empty:
            # Altair ile Profesyonel ve Kesin Renk Eşleştirmesi
            renk_skalasi = alt.Scale(
                domain=["Elazığ Vişne", "Elazig Visne", "Afyon Beyaz", "Muğla Beyaz", "Traverten"],
                range=["#6A1128", "#6A1128", "#dcdcdc", "#f4f4f4", "#c19a6b"]
            )
            grafik1 = alt.Chart(df_tur).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("MermerTuru", title="Mermer Türü", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Adet", title="Blok Adedi"),
                color=alt.Color("MermerTuru", scale=renk_skalasi, legend=None),
                tooltip=["MermerTuru", "Adet"]
            ).properties(height=350)
            st.altair_chart(grafik1, use_container_width=True)
        else:
            st.info("Henüz blok verisi yok.")
            
    with col_grafik2:
        st.subheader("Yüzey İşlemine Göre Stoklar")
        df_yuzey = run_query("SELECT YuzeyIslemi, COUNT(*) as Adet FROM Plakalar WHERE Durum = 'Stokta' GROUP BY YuzeyIslemi")
        if not df_yuzey.empty:
            yuzey_skalasi = alt.Scale(
                domain=["Cilalı", "Honlu", "Eskitme", "Ham"],
                range=["#1f77b4", "#ff7f0e", "#8c564b", "#7f7f7f"]
            )
            grafik2 = alt.Chart(df_yuzey).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("YuzeyIslemi", title="Yüzey İşlemi", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Adet", title="Plaka Adedi"),
                color=alt.Color("YuzeyIslemi", scale=yuzey_skalasi, legend=None),
                tooltip=["YuzeyIslemi", "Adet"]
            ).properties(height=350)
            st.altair_chart(grafik2, use_container_width=True)
        else:
            st.info("Henüz plaka verisi yok.")

    st.divider()
    st.subheader("Üretim Verimlilik Raporu")
    df_verimlilik = run_query("SELECT * FROM vw_UretimVerimlilikRaporu")
    st.dataframe(df_verimlilik, width="stretch")

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
        st.toast(f"✅ {blok_kod} kodlu blok başarıyla kaydedildi!", icon="🪨")
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
# 2. PLAKA KESİM VE STOK
# ---------------------------------------------------------
elif choice == "Plaka Kesim ve Stok":
  st.header("🔪 Plaka Kesim ve Stok")

  df_bloklar = run_query("SELECT BlokID, BlokKod FROM Bloklar")
  if df_bloklar.empty:
    st.warning("Henüz sisteme kayıtlı bir blok yok. Önce Blok Yönetimi sekmesinden blok ekleyin.")
  else:
    blok_opts = dict(zip(df_bloklar["BlokKod"], df_bloklar["BlokID"]))
    secilen_blok = st.selectbox("Kesilecek Blok", list(blok_opts.keys()))

    col1, col2 = st.columns(2)
    with col1:
      plaka_kod = st.text_input("Plaka Kodu", value="PLK-101")
      yuzey = st.selectbox(
          "Yüzey İşlemi", ["Cilalı", "Honlu", "Eskitme", "Ham"]
      )
      kalinlik = st.number_input("Kalınlık (cm)", min_value=0.5, value=2.0, step=0.5)
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
              (blok_opts[secilen_blok], plaka_kod, yuzey, kalinlik, en, boy),
          )
          conn.commit()
          conn.close()
          st.toast(f"✅ {plaka_kod} plakası stoğa eklendi!", icon="🔪")
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
# 3. KASALAMA VE SEVKİYAT
# ---------------------------------------------------------
elif choice == "Kasalama ve Sevkiyat":
  st.header("📦 Kasalama ve Sevkiyat")

  col1, col2 = st.columns(2)
  with col1:
    st.subheader("Yeni Kasa Oluştur")
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
          st.toast(f"📦 {kasa_kod} kasası başarıyla açıldı!", icon="✅")
          st.rerun()
        except Exception as e:
          st.error(f"Kasa Açma Hatası: {e}")

  with col2:
    st.subheader("Plakayı Kasaya Yerleştir")
    df_acik_kasalar = run_query("SELECT KasaID, KasaKod FROM Kasalar WHERE Durum = 'Açık'")
    df_stok_plakalar = run_query("SELECT PlakaID, PlakaKod FROM Plakalar WHERE Durum = 'Stokta'")

    if not df_acik_kasalar.empty and not df_stok_plakalar.empty:
      kasa_opts = dict(zip(df_acik_kasalar["KasaKod"], df_acik_kasalar["KasaID"]))
      plaka_opts = dict(zip(df_stok_plakalar["PlakaKod"], df_stok_plakalar["PlakaID"]))

      secilen_kasa = st.selectbox("Hedef Kasa", list(kasa_opts.keys()))
      secilen_plaka = st.selectbox("Yerleştirilecek Plaka", list(plaka_opts.keys()))

      if st.button("📦 Plakayı Kasala"):
        res = execute_sp(
            "sp_PlakaKasala",
            [plaka_opts[secilen_plaka], kasa_opts[secilen_kasa]],
        )
        if res:
          st.toast(f"📦 {secilen_plaka} plakası {secilen_kasa} kasasına yerleştirildi!", icon="🚀")
          st.rerun()
    else:
      st.info("Kasalama yapmak için en az 1 açık kasa ve 1 stokta plaka gereklidir.")

  st.divider()
  st.subheader("📦 Mevcut Kasa Durumları")
  df_kasalar = run_query("SELECT * FROM Kasalar")
  st.dataframe(df_kasalar, width="stretch")
