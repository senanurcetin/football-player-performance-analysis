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

### Güvenlik ve veri kanıtı sınırları

Bu notebook **BigQuery credentials/ADC istemez**, Google Cloud tablo okuma-yazma işlemi yapmaz, Github Actions/CircleCI başlatmaz ve model yayınlamaz. Ücretsiz Colab/Kaggle kaynak süresi sınırlarına tabidir. Çalıştırıcıda gerçekte PASS olmayan bir komut **genel sonucu FAIL yapar**; boş rapor hiçbir zaman PASS olmaz.

- **BigQuery veri testi hâlâ ayrı:** BigQuery ChatGPT bağlayıcısı yönetici tarafından devre dışı. Tarihsel modelin gerçek veriyle yeniden değerlendirilmesi, `dbt build/test`, kaynak freshness ve hedef değerleme dışlama etkisi için ayrıca yetkili Google Cloud oturumu, veri işleme maliyet onayı ve gerçek veri gerekir. Colab/Kaggle notebook'unu çalıştırmak tek başına bu kanıtı sağlamaz.
- **Power BI ve final CI sonraki kapılar:** Kullanıcının belirttiği sıraya uyulur: önce kaynak ve BigQuery/model doğrulaması, sonra Power BI'nin gerekli kabulü, en son tek seferlik nihai CI. `.github/workflows/ml-production.yml` manual-only / çift onaylı olarak kalır.
- **Gizli anahtar taşımayın.** Kaggle API key, BigQuery service-account JSON, personal access token ve cloud credential'larını notebook hücrelerine, çıktı raporuna veya GitHub deposuna koymayın.

### Kanıt durumu

19 Ekim 2026'da notebook dosyası `nbformat.validate` ile doğrulandı, runner `py_compile` ve `--help` ile çalıştırıldı; runner için `tests/test_run_offline_verification.py` kapsamında **iki lokal PASS** alındı. **Bunlar football repo testlerinin çalıştırıldığı anlamına gelmez.** Bu ChatGPT ortamından GitHub archive indirme isteği DNS hatası verdi; bağlı `Senanur` Desktop Commander cihazı kota nedeniyle kullanılamıyor. Tam depo ve BigQuery kabul sonuçları ancak yetkili alternatif kernel çalıştırıldığında üretilebilir.

Sürüm ve açık engeller için [PROJECT_STATUS.md](PROJECT_STATUS.md) tek güncel karar kaynağıdır.
