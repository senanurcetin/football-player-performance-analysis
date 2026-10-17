# All-dashboard Power BI modernization plan

> **Archived historical record — 17 October 2026.** This document preserves prior engineering decisions and evidence; it is not the current delivery status. For current verified vs. pending checks, see [Project status](../../PROJECT_STATUS.md) and the [documentation index](../../README.md).


> **Production Desktop handoff:** [Open the real BigQuery PBIP and record source checks](../../POWER_BI_DESKTOP_HANDOFF.md). Run `python scripts/check_powerbi_release_handoff.py --output powerbi-handoff.json` from the repository root. Passing source checks does not remove Desktop/BigQuery acceptance HOLD.

> **New visual refinement roadmap:** [NEXUS Football typography, page hierarchy, navigation and Desktop acceptance](POWER_BI_VISUAL_REFINEMENT_ROADMAP.md). ML Reliability table typography is improved at **source level** in both editions; real Desktop acceptance is still required.

## Güncel plan — 13 Ekim 2026 / PR #44 sonrası

> **Karar: SOURCE UPDATED / DESKTOP QA HOLD / PRODUCTION DATA HOLD.**
> Bu bölüm, aşağıdaki tarihsel Stage A listesinden daha günceldir. Kaynakta değişmiş bir PBIR nesnesi, Power BI Desktop'ta çalıştığı veya ürün kalitesini geçtiği anlamına gelmez.

### Kanıtlanmış değişiklikler ve tamamlanmamış doğrulama

| Konu | 13 Ekim kaynak durumu | Kabul için eksik kanıt |
| --- | --- | --- |
| Sentetik `dim_clubs` (6/6) | PR #44 ile `average_age` ve `foreigners_percentage` alanlarındaki toplam 12 tırnaklı sayısal literal sayısal değerlere çevrildi; kaynak testi eklendi | Offline-demo Desktop refresh sonrası 6 satır / 0 error ve ilişki doğrulaması |
| Gerçek `fct_club_risk_profile` (6 hata bildirimi) | PR #42 ile 13 kolon sözleşmesi ve read-only BigQuery triage dokümanı eklendi; üretim modeline dokunulmadı | Hatalı Power Query adımı, kolon, hata metni, BigQuery şema/örnek satır farkı; gerçek refresh 0 error |
| Demo/production ayrımı | `workspace` gerçek BigQuery; `offline-demo` sentetik `#table` tabloları; üretimde DEMO ibareleri yok | Üretim ekranındaki tüm KPI'lar için gerçek veri kökeni; demo ekranlarında SYNTHETIC uyarısının korunması |
| NEXUS logo | Orijinal PNG kayıtlı; 9 analiz/detail masthead için içine özgün PNG gömülü kırpılmış SVG; Home/Closing hero orijinal görsel | Desktop'ta SVG kaynak çözümleme, boyut, netlik ve başlık çakışması kontrolü |
| Global görsel sistem | 9 analitik/detail sayfada `#091E33`, Home/Closing'de `#071829`; grafik paleti mavi/cyan/lavender; KPI ve detay sayfa kaçakları kaynakta düzeltildi | 13 sayfada gerçek 100% zoom kontrast, sonradan baskın çıkan object-level stiller ve tooltip görünümü |
| Sayfa akışı | 13 PBIR sayfası: 9 görünür, 2 gizli drillthrough, 2 tooltip; Home 7 modül, footer 6 analiz sayfasında yenilendi | Tıklama, keyboard-focus, selected-state, çapraz filtre, drillthrough/tooltip ve footer kapanma testi |
| Veri tabloları | Transfer tablosu 362→615 px genişletildi, değerleme başlıkları birimleriyle sadeleştirildi | Gerçek satırlarla kolon kırpılması, scroll, toplam satırı, veri tipleri ve ölçü biçimi |
| Test ve yayın | Kaynak regresyon testleri mevcut; son düzeltmeler [skip ci] ile birleşti | Yerel Python/testler, gerçek Desktop render, BigQuery reconciliation, onaylı ekran görüntüleri |

**Önemli:** `dim_clubs` sentetik hatasının kaynak düzeltmesini, üretimdeki `fct_club_risk_profile` sorununun giderildiği şeklinde yorumlama. Gerçek veri verilirken sentetik uyarılarını silmek yerine **üretim PBIP** sürümünü kullan.

### Yeni öncelik sırası ve tamamlanma ölçütleri

**P0-A — Veri güvenilirliği (yayın engelleyici)**
1. Offline PBIP: 33 sentetik model partition'ını Desktop'ta yenile; `dim_clubs` için 6 satır / **0 hata**, referans/ilişki bütünlüğü ve otomatik tür adımlarını doğrula.
2. Production PBIP: `fct_club_risk_profile` için Power Query **Keep Errors / View Errors** adım, kolon, native hata ve `club_id` kanıtlarını kaydet. `docs/POWER_BI_CLUB_RISK_REFRESH_TRIAGE.md` içindeki BigQuery INFORMATION_SCHEMA ve anomali SQL'lerini yalnızca salt-okunur çalıştır.
3. Hata nedenine göre yalnızca gerekli Power Query/TMDL veya otoritatif dbt modeli düzelt; `NULL` değerleri körlemesine 0 yapma ve yüzdelik 0–100 birimleri ile 0–1 formatını karıştırma.
4. Production BigQuery refresh sonucu **0 conversion error**; tablo satır sayısı, club_id anahtarları, risk kategori ve kaynak mart metrikleri uzlaştırılmış olmalı.

**P0-B — Tek ürün kimliği ve okunabilirlik (kaynak hazır, görsel kabul açık)**
1. Home/Closing `#071829`, analitik/detail `#091E33` koyu NEXUS yüzeyini Desktop'ta doğrula; iki tooltip'in açık mavi bağlamsal yüzeyini ayrıca kontrasttan geçir. Eski açık/lavanta sayfa zeminlerini anlatan dokümantasyon, güncel PBIR ile eşitlenmeli.
2. Kırpılmış wordmark'ı Desktop'ta yükle; resmi logo okunaklı olmalı ve karanlık yuvarlak padding görünmemeli. Desteklenmiyorsa sahte/eksik logo yayımlamak yerine orijinal PNG'ye dön.
3. Eski pembe/somon/mint/yeşil serileri treemap, scatter, tablolardaki striping, ML ve iki detay sayfasında tek tek kontrol et; semantik uyarı rengi dışında palet dışına çıkma.
4. Alt navigasyon ve sol rail ilk kez kullanan bir kişinin sayfa hedeflerini okuyabileceği şekilde incelenmeli: ikon + kısa metin, aktif/hover/focus durumları, yeterli tıklama alanı. Kaynakta yalnız H/P/S/C/T/V/M monogramları bırakılmış olması UX kabulü değildir; ML Reliability'ye erişimi açıkça denetle.
5. Footer için 679–718 source bölgesi; veri görselleri y=671 öncesinde bitmeli. Desktop'ta alt barın görünebilirliği ve tablo/slicer ile çakışma testi şart.

**P1 — Sayfa bazlı görsel ve metrik kabulü**

| Sayfa / tür | Değişikliklerden kalan ürün düzeyi kontrol |
| --- | --- |
| Home | Büyük orijinal NEXUS logo, net hero tipografi, 7 anlamlı modül kartı, tüm linklerin doğru hedefi ve odağı |
| Player Performance | 5 koyu KPI kartında değer/label kontrastı, per-90/Top N semantiği, slicer, tooltip ve görsel kalabalık |
| Player Segmentation | Gerçek grup dağılımı, market-value yatay karşılaştırma, düzgün treemap/bar eksenleri ve küçük etiketler |
| Club & League | Win-rate % gösterimi, eksi gol farkı, kulüp/lig slicer, kulüp risk verisiyle ilişki |
| Transfer Success 365d | Gözlenmiş sonuç ile tahmin ayrımı; 365 gün, 20 yüzde puanı eşiği, eligible/observed paydalar, follow-up coverage |
| Transfer & Market Value | 615px evidence tablosunda 7 kolon, € ve % birimleri, değeri bilinen ücret kapsamı, yatay scroll |
| Player Market Value Prediction | Önceki/tahmini değer, alt/üst belirsizlik sınırı ve model tahmininin gözlenen gerçekle karışmaması |
| ML Model Reliability | Navy panel kontrastı, baseline/WAPE/R² ve veri tazeliği kanıtı; gerekçesiz başarı eşiği yok |
| Closing | Başlık/logo çakışması yok, okunabilir hiyerarşi, Home dönüş linki |
| Transfer Detail + Prediction Detail | 1280×720 dark canvas, mint/pastel yok, drillthrough filtre bağlamı, boş veri ve uzun isim senaryoları |
| İki tooltip | 560×320 küçük tuvalde taşma yok, filtre bağlamı ve hover doğru; dashboard sayfası gibi sunulmaz |

**P2 — Test ve ürün kabulü**
1. Yerelde **CI kotası harcamadan** `python scripts/check_powerbi_project.py`, `python scripts/check_powerbi_offline_demo.py`, `python scripts/audit_powerbi_visuals.py`, `python scripts/audit_powerbi_layout.py`, `python scripts/check_powerbi_nexus_product.py`, `python -m unittest discover -s tests -p 'test_powerbi_*.py'` çalıştır; exit code ve uyarıları kayıt altına al.
2. Power BI Desktop'ta 9 görünür + 2 gizli drillthrough + 2 tooltip olmak üzere **13 sayfa** için screenshot matrix oluştur. En az 100% zoom'da tekst kırpma, taşma, renk ve etkileşim incelemesi kaydet.
3. Gerçek BigQuery'ye karşı satır/anahtar/metrik/kur/para birimi / veri tazeliği karşılaştırması yap; 365d outcome vs ML prediction terminolojisi doğru olmalı.
4. Yalnızca **üretim workspace** render'ından alınmış, doğrulanmış ekran görüntülerini portfolyo için kullan. Demo capture yayımlanırsa kaynak açıklaması mutlaka görünür kalmalı.
5. Kabul kaydı: rapor Git SHA, PBIP edition, veri kaynağı, refresh timestamp, 0 error, test sonuçları, screenshot referansları, open blocker=0. Ancak bundan sonra **HOLD → ACCEPTED**.

### Yönetim ilkeleri

- Yeni pazarlama mockup'ı, PowerPoint kopyası veya photoshop'lu sözde Power BI ekranı üretme. Gerçek çıktı editable PBIR/PBIP.
- Güncel kodun durumu `PR #44` merged/commit `04e60ebc` ile gösterilir; önceki kaynak testlerinin varlığı **çalıştırıldıklarını** göstermez.
- `docs/BI_DESIGN_SYSTEM.md` ve `docs/POWER_BI_VISUAL_QA.md` içindeki önceki açık pastel sayfa anlatımlarını PBIR son sürümüyle karşılaştır; geçmişi silmeden güncel nihai paletteki sapmayı gider.
- Nihai onay Power BI Desktop ve BigQuery ölçüm kanıtına bağlı; salt GitHub merge veya kaynak JSON denetimi yeterli değil.

---

**Project:** `senanurcetin/football-player-performance-analysis`  
**Report editions:** `powerbi/workspace/FootballPlayerAnalysis/` (BigQuery) and `powerbi/offline-demo/FootballPlayerAnalysis/` (synthetic fixtures)  
**Source of truth:** `Report/definition/` (PBIR), not legacy `Report/sections/` or historical screenshot PNGs.

## Deliverable standard

Every page must be structurally valid, obey NEXUS navy/blue identity, have meaningful chart bindings and readable labels, allow safe navigation, and carry honest data provenance. Never treat static JSON inspection as a Power BI Desktop test. Synthetic outputs must not be presented as real football or model-quality results.

### Page-by-page inventory and remaining acceptance

| PBIR page | Current source work | Power BI Desktop acceptance remaining |
|---|---|---|
| Home | Global NEXUS theme, page order and link-contract checks | Navigation, contrast and keyboard focus |
| Player Performance Analysis | Theme, four primary data visual descriptions, weighted/per-90 legacy corrections | Render, rank direction, drill/filter interactions |
| Player Segmentation | Theme, four query-bound plots and accessibility descriptions | Meaningful nonblank group results; check market-value aggregation |
| Club & League Analysis | Theme, four plot descriptions | Win-rate units, negative goal differences, league filters |
| Transfer Success Analysis (365d) | Theme, four charts plus four cohort/coverage/reliability cards, alt text | Production 365-day outcomes, denominator/coverage and absence of fabricated prediction claims |
| Transfer & Market Value Analysis | Theme and four visual descriptions | Known-fee coverage, percent units, seasonal trends |
| Player Market Value Prediction | Theme and four visual descriptions | Prediction quality, uncertainty bands, non-realized growth caveat |
| ML Model Reliability | Theme and four visual descriptions | Quality-gate logic, missing backtest data and feature importance |
| Closing | Theme, 16:9 canvas registry | Readability and focus ordering |
| Player Transfer Detail (hidden) | Theme and hidden drillthrough registry | Drillthrough entry points, required field context |
| Player Prediction Detail (hidden) | Theme and hidden drillthrough registry | Drillthrough, attribution and quality badges |
| Tooltip Transfer (hidden) | Explicit 560×320 Tooltip page binding, 2 visual descriptions | Hover trigger compatibility and values within small canvas |
| Tooltip Prediction (hidden) | Explicit 560×320 Tooltip page binding, 2 visual descriptions | Hover context and non-interactive tooltip legibility |

All 13 pages receive the registered `NEXUSMidnight-20261012-v2.json` custom report theme. It sets global fallback styling for **13 visual types** without overriding the explicit semantics or individual chart axes. A versioned RegisteredResources reference avoids Desktop caching an old `AccessibleTidal` resource.

## Execution stages

### Stage A — PBIR source work (changes prepared)

- [x] Audit page counts, page order, theme registration, page type and source model distinctions
- [x] Register consistent NEXUS Midnight theme in both report editions
- [x] Repair both tooltip pages per edition: `pageBinding.type=Tooltip`, hidden tab, `ActualSize`, 560×320
- [x] Add metric-specific alternative text for 36 chart/KPI objects in both editions (72 files)
- [x] Add automated whole-report page/theme/tooltip/accessibility regression tests
- [ ] Verify remaining hardcoded theme overrides across **all** pre-existing visual objects (not automatically overruled by theme)
- [x] Remove legacy green surface literals from the four identified ML prediction slicer/KPI/chart visuals in both report editions; add a regression test for these objects
- [x] Replace legacy green/gray hardcoded accents in 16 principal analytics visuals per edition (Player Performance, Transfer & Market Value, Market Value Prediction, ML Model Reliability); preserve their query roles
- [ ] Run all preflight scripts and Python unit tests on a full working copy

### Stage A.2 — Single editorial report and repository diet

- [x] Give each of the 13 editable PBIR pages its own coordinated NEXUS canvas
- [x] Introduce different asymmetric chart compositions on Player Segmentation and Club & League pages; preserve original Category/Y query roles
- [x] Keep Home / Closing dark and maintain demo-versus-production naming distinction
- [x] Remove decorative emoji page-name prefixes; move ML reliability before Closing in visible storytelling order
- [x] Give 365-day Transfer Success its own 63/37 and 67/33 data-chart hierarchy
- [x] Remove the six outdated green Power BI screenshot PNGs, their archive index and the superseded SVG cover
- [x] Keep production workspace and deterministic offline-demo because they serve different data sources, **not** two exported PowerPoint presentations
- [x] Add static regression checks for palette, native chart geometry and workspace/demo role parity
- [ ] Confirm all native visual overlaps and browser/Power BI Desktop rendering; no engine-level validation was run here
- [ ] Audit PBIR RegisteredResources binary image references before considering any further asset removal

### Stage B — Engine-level verification (blocked)

- [ ] Open the offline PBIP in a supported Power BI Desktop
- [ ] Refresh all 33 inline demo model partitions; verify zero unexpected BigQuery prompts
- [ ] Inspect all 11 full-size pages, plus 2 tooltip pages, against their bindings
- [ ] Test Home/sidebar navigation, keyboard tab order, slicers, drillthrough, custom visuals and report-page tooltips
- [ ] Check 365-day outcome counts, value-growth unit conversion and follow-up coverage in Power BI itself
- [ ] Recheck production against authenticated BigQuery marts and SQL governance
- [ ] Run dark/light contrast and overflow checks on screenshots at 100% zoom

### Stage C — Portfolio evidence (blocked until Stage B)

- [ ] Capture **actual** Power BI Desktop screenshots, record report commit and data source
- [ ] Keep visible SYNTHETIC DEMO marking on every demo capture
- [ ] Replace legacy green screenshots **only after** validated real captures exist
- [ ] Reconcile every numeric README/dashboard caption to the matching production or clearly synthetic run
- [ ] Remove 'HOLD' release status only after a documented rendered/warehouse pass

## Offline checks

From repository root in a local checkout (no GitHub Actions minutes needed):

```bash
python scripts/check_powerbi_project.py
python scripts/check_powerbi_offline_demo.py
python scripts/audit_powerbi_visuals.py
python -m unittest discover -s tests -p 'test_powerbi_*.py'
```

The new `tests/test_powerbi_all_dashboard_quality.py` checks **both** model editions for the same 13 pages, start page, canvas and tooltip dimensions, theme registration, required visual styles, six Home navigation links, and accessible alternative text on the 36 specified data visuals. CI config has not been changed as part of this design pass.

**Scope limitation:** The user-authorized Desktop Commander machine was last observed offline. No Power BI Desktop screenshots, DAX execution or BigQuery refresh have been observed during this stage. Design improvements are source-level until verified in Power BI.
