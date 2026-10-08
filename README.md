# 🪨 Mermer Üretim ve Stok Takip ERP

Fırat Üniversitesi - Veri Tabanı Yönetim Sistemleri (VTYS) Dersi Projesi olarak geliştirilmiş; mermer fabrikalarının blok kabulünden, plaka kesimine ve kasalanıp sevkiyata hazır hale gelmesine kadar geçen tüm üretim bandını yöneten tam kapsamlı bir ERP (Kurumsal Kaynak Planlaması) sistemidir. 

Proje, gücünü **T-SQL (Microsoft SQL Server)** mimarisinden almakta olup, ön yüzünde endüstriyel "Elazığ Vişne" mermeri konseptiyle tasarlanmış lüks bir **Streamlit** arayüzü barındırmaktadır.

---

## 🚀 Projenin Öne Çıkan Özellikleri

### 1. Gelişmiş T-SQL Mimarisi (Veri Tabanı Seviyesi İş Mantığı)
Uygulamanın iş mantığı tamamen SQL Server üzerinde çalışacak şekilde tasarlanmıştır:
*   **Stored Procedure (Saklı Yordamlar):** Plakaların kasalara atanması ve m² hesaplamaları `sp_PlakaKasala` prosedürü ile tek bir transaction üzerinden güvenli bir şekilde yapılır.
*   **Trigger (Tetikleyiciler):** İşçi kasaya plaka ekledikçe çalışan `trg_KasaKapasiteKontrol` tetikleyicisi, kasanın toplam m²'sini dinler ve 30 m² sınırına ulaşıldığında kasanın durumunu otomatik olarak "Kapalı" (Sevkiyata Hazır) statüsüne çeker.
*   **View (Görünümler):** Dashboard ekranındaki karmaşık metrikler, `JOIN` işlemleriyle optimize edilmiş `vw_UretimVerimlilikRaporu` üzerinden anlık ve performanslı bir şekilde çekilir.

### 2. Rol Bazlı Erişim Kontrolü (RBAC)
Sistem, gerçek bir fabrika hiyerarşisine uygun olarak iki farklı yetki seviyesi sunar:
*   **Yönetici (Admin):** Tüm üretim modüllerine ve şirketin anlık durumunu, stok maliyetlerini, üretim verimliliğini gösteren Yönetici Özeti (Dashboard) ekranına tam erişim sağlar.
*   **Saha Operatörü:** Sadece veri giriş modüllerini (Blok, Plaka, Kasa işlemleri) görebilir; finansal veya özet raporlara erişemez.

### 3. Profesyonel UI/UX Tasarımı
*   **Cam Efekti (Glassmorphism) & Kurumsal Renkler:** Sistem, açık renkli mermer dokulu bir arka plan üzerine, Elazığ Vişnesi mermerinden ilham alınan derin bordo tonlarıyla zenginleştirilmiş metrik kartları sunar.
*   **Dinamik Veri Görselleştirme:** Altair grafik motoru kullanılarak oluşturulan dinamik raporlar, her mermer türünü (Elazığ Vişne, Afyon Beyaz, Traverten vb.) kendi gerçek doğa rengiyle haritalayarak sunar. 
*   **Modern Bildirimler:** Gerçek zamanlı Toast bildirimleri ile kullanıcı etkileşimi en üst düzeyde tutulmuştur.

---

## 🛠️ Kullanılan Teknolojiler

*   **Veri Tabanı:** Microsoft SQL Server 2022 (Docker Container)
*   **Veri Tabanı Programlama:** T-SQL (Transact-SQL)
*   **Backend & Frontend:** Python 3.13, Streamlit
*   **Veri Analizi ve Görselleştirme:** Pandas, Altair
*   **Veri Tabanı Sürücüsü:** pymssql
*   **Versiyon Kontrolü:** Git & GitHub

---

## 💻 Kurulum ve Çalıştırma Talimatları

Projeyi kendi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin:

**1. Depoyu Klonlayın**
```bash
git clone <sizin-github-repo-linkiniz>
cd mermer-uretim-takip
