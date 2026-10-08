<div align="center">
  <!-- Proje logonuz veya ekran görüntünüz varsa buraya ekleyebilirsiniz -->
  <!-- <img src="docs/logo.png" alt="Logo" width="150" height="150"> -->

  <h1 align="center">Mermer Üretim ve Stok Takip ERP</h1>

  <p align="center">
    Endüstriyel mermer tesisleri için tasarlanmış; veri bütünlüğünü T-SQL katmanında garanti altına alan, yüksek performanslı ve modern arayüzlü Kurumsal Kaynak Planlama (ERP) sistemi.
    <br />
    <a href="#-kurulum"><strong>Kurulum Adımlarını İncele »</strong></a>
    <br />
    <br />
    <a href="#-ekran-görüntüleri">Ekran Görüntüleri</a>
    ·
    <a href="https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ/issues">Hata Bildir</a>
    ·
    <a href="https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ/issues">Özellik İste</a>
  </p>
</div>

<!-- ROZETLER (BADGES) -->
<div align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Microsoft%20SQL%20Server-CC292B?style=for-the-badge&logo=microsoft-sql-server&logoColor=white" alt="MS SQL">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge" alt="License">
</div>

---

## 📖 İçindekiler
<details>
  <summary>Tabloyu Genişletmek İçin Tıklayın</summary>
  <ol>
    <li><a href="#-proje-hakkında">Proje Hakkında</a></li>
    <li><a href="#-mimari-ve-teknoloji-yığını">Mimari ve Teknoloji Yığını</a></li>
    <li><a href="#-veritabanı-iş-mantığı-t-sql">Veritabanı İş Mantığı (T-SQL)</a></li>
    <li><a href="#-uiux-ve-tasarım-felsefesi">UI/UX ve Tasarım Felsefesi</a></li>
    <li><a href="#-kurulum">Kurulum</a></li>
    <li><a href="#-kullanım-ve-modüller">Kullanım ve Modüller</a></li>
    <li><a href="#-proje-dizini">Proje Dizini</a></li>
    <li><a href="#-geliştirici">Geliştirici</a></li>
  </ol>
</details>

## 🏭 Proje Hakkında

**Mermer Üretim ve Stok Takip ERP**, bir mermer fabrikasının hammadde (blok) kabulünden başlayarak, plaka kesimi, stoklanması ve kasalanıp sevkiyata hazır hale getirilmesine kadar geçen tüm operasyonel ömrünü dijitalleştiren kapsamlı bir yönetim sistemidir. 

Fırat Üniversitesi **Veri Tabanı Yönetim Sistemleri (VTYS)** dersi kapsamında geliştirilen bu proje, sıradan CRUD uygulamalarından farklı olarak **"Database-Level Programming" (Veritabanı Seviyesinde Programlama)** prensibini benimser. Tüm iş kuralları, kapasite kontrolleri ve transaction işlemleri doğrudan MS SQL Server üzerinde koşar.

## 🏗 Mimari ve Teknoloji Yığını

Sistem, ayrıştırılmış ve ölçeklenebilir bir mimari üzerine inşa edilmiştir:

* **Backend & Sunum Katmanı:** Python 3.13, Streamlit
* **Veritabanı Motoru:** Microsoft SQL Server 2022 (İzole edilmiş Docker Container ortamında çalışır)
* **Veritabanı Sürücüsü:** `pymssql`
* **Veri Analizi & Dashboard:** `pandas`, `altair` (Dinamik ve veriye bağlı renk eşleştirmeli grafikler)
* **Versiyon Kontrol ve CI/CD:** Git & GitHub

## 🗄 Veritabanı İş Mantığı (T-SQL)

Veri bütünlüğü, Python tarafındaki olası kesintilerden etkilenmemesi adına doğrudan T-SQL nesneleri ile SQL Server içerisine gömülmüştür.

| Nesne Türü | İsim | Açıklama ve Görevi |
| :--- | :--- | :--- |
| **Tablolar** | `Kullanicilar`, `Bloklar`, `Plakalar`, `Kasalar` | 3. Normal Form (3NF) kurallarına uygun, ilişkisel (Foreign Key) veri mimarisi. |
| **Stored Procedure** | `sp_PlakaKasala` | Plakanın kasaya atanması ve kasa $m^2$ değerinin güncellenmesini tek bir **Transaction** içinde yapar. Hata anında otomatik *Rollback* çalışır. |
| **Trigger** | `trg_KasaKapasiteKontrol` | `Kasalar` tablosunda `UPDATE` olduğunda tetiklenir. Toplam hacim **30 $m^2$ veya üzerine** çıkarsa, kasa statüsünü "Açık" konumundan "Kapalı" (Sevkiyata Hazır) konumuna çeker. |
| **View** | `vw_UretimVerimlilikRaporu` | Yönetici Dashboard'unu besleyen sanal tablodur. `LEFT JOIN` kullanarak blok-plaka verimlilik (tonaj/kesim) hesaplamalarını yüksek hızda sunar. |

## 🎨 UI/UX ve Tasarım Felsefesi

Endüstriyel bir yazılımın sıkıcı olması gerekmez. Proje, Streamlit'in varsayılan arayüzünden tamamen arındırılmış ve **"Elazığ Vişne"** konseptiyle kurumsallaştırılmıştır.

* **Renk Metodolojisi:** `altair` grafikleri veriye duyarlıdır. Sistemde "Elazığ Vişne" mermeri her zaman derin bordo (`#6A1128`), "Traverten" toprak beji (`#c19a6b`), "Afyon Beyaz" ise açık gri olarak render edilir.
* **Glassmorphism:** Yönetici Dashboard'undaki KPI kartları; arka plandaki fildişi/mermer dokusu ile bütünleşen, şeffaf (`backdrop-filter`) ve sol kenarı vişne renkli lüks bileşenler olarak tasarlanmıştır.
* **Modern Geri Bildirimler:** Veri kayıt veya hata durumlarında geleneksel uyarı kutuları yerine sağ alt köşeden akıcı animasyonla gelen modern `st.toast` bileşenleri kullanılmıştır.

## 🔐 Rol Bazlı Erişim (RBAC)
Sistem `st.session_state` tabanlı güvenli oturum yönetimine sahiptir.
* 👑 **Yönetici:** Analitik Dashboard dahil sistemdeki tüm üretim, stok ve raporlama modüllerine sınırsız erişim. 
* 👷 **Operatör:** Sadece operasyonel veri girişi (Blok Girişi, Kesim, Kasalama). Analitik ekranlara erişim kısıtlaması.

---

## 🚀 Kurulum

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin. Sisteminizde [Python 3.13+](https://www.python.org/downloads/) ve [Docker](https://www.docker.com/) kurulu olmalıdır.

### 1. Depoyu Klonlayın
```bash
git clone [https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git](https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git)
cd REPO_ADINIZ
