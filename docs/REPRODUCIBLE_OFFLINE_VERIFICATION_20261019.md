# Desktop Commander kotası olmadan bağımsız ML doğrulaması — 19 Ekim 2026

**Kapsam:** NEXUS Football Intelligence açık kaynak araştırma deposu. **Ürünleştirme yok, ücretli BigQuery işi yok, CI tetiklemesi yok.**

## Alternatif çalışma ortamı

Desktop Commander erişimi kota nedeniyle kullanılamadığında ücretsiz CPU kotası dahilinde **Google Colab** veya **Kaggle Notebook** kullanılabilir. Bu iki ortam, kaynak kodu doğrudan GitHub'dan indirir ve tam checkout içinde bağımsız Python/dbt-kaynak doğrulaması yapabilir. Kullanıcı bu ortamlardan birinde notebook'u çalıştırmalıdır; ChatGPT bu oturumdan ücretsiz Colab/Kaggle kernel'ini doğrudan başlatamaz.

**GitHub'dan aç:** [NEXUS offline verification notebook](../notebooks/nexus_football_offline_verification.ipynb)

**Colab GitHub açılışı:** https://colab.research.google.com/github/senanurcetin/football-player-performance-analysis/blob/main/notebooks/nexus_football_offline_verification.ipynb

**Kaggle:** Notebook'u içe aktar, **Internet = On**, CPU seç; ardından hücreleri sırayla çalıştır. Kaggle'ın kendine ait çalışma süresi kotası ve İnternet erişimi kuralları vardır; bunlar Desktop Commander ve GitHub Actions kotasından bağımsızdır.

## Çalışma sırası

1. `git clone --depth 1 --branch main` ile depoyu kernel'in yerel dosya alanına al. Güncel `git rev-parse HEAD` değeri raporda saklanır; testler `main` üzerinde kayıtlı *o commit* için anlamlıdır. Notebook hiçbir dosyayı GitHub'a push etmez.
2. Depodaki `requirements.txt`, `requirements-ml.txt` ile YAML/Jinja doğrulama bağımlılıklarını kur. **Paket kurmak bulut sorgusu çalıştırmaz**.
3. `scripts/run_offline_verification.py --phases source ml` çalıştır. Kaynak aşaması Python syntax, YAML/Jinja SQL preflight ve doküman bütünlüğü; ML aşaması yeni ve mevcut ML unit dosyaları ile sentetik model smoke testidir.
4. Bu sonuç **PASS** ise aynı çalıştırıcıyla `--phases full` aşamasında **tüm** `test_*.py` Python testlerini çalıştır. Statik Power BI kaynak testleri bulunabilir; bu aşama Power BI Desktop başlatmaz veya canlı Power BI kabulü sayılmaz.
5. `nexus_football_ml_verification.json` ve `nexus_football_full_verification.json` çıktısını sakla; her raporda commit SHA, alt komut, çıkış kodu, sınırlı çıktı dökümü, süre ve kesin PASS/FAIL bilgisi vardır. Notebook bunları ZIP olarak verir. FAIL durumunda full aşaması **atlanır**; model yayın veya final CI tetiklenmez.

Örnek terminal kullanım:

```bash
python scripts/run_offline_verification.py --phases source ml \
  --repo . --report verification_report.json
python scripts/run_offline_verification.py --phases full \
  --repo . --report verification_full_report.json
```

### Kaggle CPU'da kesin sürümle doğrulama — 19 Ekim eklemesi

**Kaggle çalıştırma adımları:** Kaggle → Code → New Notebook → File → Import Notebook; GitHub'dan `notebooks/nexus_football_offline_verification.ipynb` dosyasını import et. Settings bölümünde **Internet → On** ve **Accelerator → None (CPU)** seç. `Run All` (veya `Save Version → Save & Run All`) ile yürüt. Test kanıtı `/kaggle/working/nexus_football_verification_reports.zip` içinde oluşur; notebook çıktısından indirilebilir. GitHub'daki `main` üzerinden *aynı notebook* seçildiğinde de aynı adımlar geçerlidir.

Güvenilir sonuç şartı: notebook önce tam 40 karakterli Git SHA'yı okur ve hem `source ml` hem `full` raporlarına `--expected-commit` verir. Çalıştırıcı SHA'yı okuyamaz, Git komutu başarısız olur veya SHA aşamalar arasında değişirse **genel sonuç FAIL** olmalıdır. Salt test komutlarının sıfır çıkış kodu vermesi yeterli değildir.

Bu katı kural için iki ek Python regresyon testi eklendi: **Git SHA yok** ve **beklenen SHA uyuşmuyor** koşullarında PASS üretme. Güncel dört testin tam GitHub checkout koşusu **henüz Kaggle'da çalıştırılmadı**. Önceki iki testin geçmesi yeni eklenenlerin PASS olduğu anlamına gelmez.

## Güvenlik ve veri kanıtı sınırları

Bu notebook **BigQuery credentials/ADC istemez**, Google Cloud tablo okuma-yazma işlemi yapmaz, Github Actions/CircleCI başlatmaz ve model yayınlamaz. Ücretsiz Colab/Kaggle kaynak süresi sınırlarına tabidir. Çalıştırıcıda gerçekte PASS olmayan bir komut **genel sonucu FAIL yapar**; boş rapor hiçbir zaman PASS olmaz.

- **BigQuery veri testi hâlâ ayrı:** BigQuery ChatGPT bağlayıcısı yönetici tarafından devre dışı. Tarihsel modelin gerçek veriyle yeniden değerlendirilmesi, `dbt build/test`, kaynak freshness ve hedef değerleme dışlama etkisi için ayrıca yetkili Google Cloud oturumu, veri işleme maliyet onayı ve gerçek veri gerekir. Colab/Kaggle notebook'unu çalıştırmak tek başına bu kanıtı sağlamaz.
- **Power BI ve final CI sonraki kapılar:** Kullanıcının belirttiği sıraya uyulur: önce kaynak ve BigQuery/model doğrulaması, sonra Power BI'nin gerekli kabulü, en son tek seferlik nihai CI. `.github/workflows/ml-production.yml` manual-only / çift onaylı olarak kalır.
- **Gizli anahtar taşımayın.** Kaggle API key, BigQuery service-account JSON, personal access token ve cloud credential'larını notebook hücrelerine, çıktı raporuna veya GitHub deposuna koymayın.

### Kanıt durumu

**Güncel kanıt (19 Ekim 2026):** SentinelX üzerinden Windows'ta izole edilmiş tam GitHub checkout'u kullanılarak **243/243 Python**, **47/47 ML testi** ve SHA eşleşmeli dokuz aşamalı taşınabilir doğrulama çalıştırıcısı **PASS** verdi. dbt çevrimdışı parse işlemi de başarılıdır. Colab/Kaggle notebook'u alternatif olarak korunuyor, ancak **Kaggle sunucusunda çalıştırıldığı iddia edilmiyor**. Bu başarılar gerçek BigQuery kaynak sorgularının ve yeniden eğitilmiş modelin kabulü değildir. [Çalıştırılmış test kanıtı](SENTINELX_OFFLINE_VERIFICATION_20261019.md).

Sürüm ve açık engeller için [PROJECT_STATUS.md](PROJECT_STATUS.md) tek güncel karar kaynağıdır.
