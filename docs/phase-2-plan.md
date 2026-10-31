# Faz 2 Planı — Deterministik Kontrollü Doğal Dil (CNL) Alt Kümesi

Tarih: 2026-11-01
Durum: öneri — onay bekliyor, kod yazılmadı
Başlangıç sürümü: 0.2.1 (PyPI + npm'de yayında)

## 0. Dayanak ve varsayımlar

- Depoda yazılı bir yol haritası yok. README yalnızca faz-1 sözleşmesini anlatıyor:
  İngilizce Python kaynağının anahtar sözcüklerini 20 yerel dile çeviren, aynı
  girdi + yerel + sürüm için bayt düzeyinde aynı çıktıyı üreten bir araç.
- "Faz 2 = kontrollü doğal dil (CNL)" tanımı önceki karardan geliyor; depo
  içinde yazılı bir spesifikasyon değil. Bu plan o varsayımla yazıldı. Varsayım
  yanlışsa planın tamamı geçersizdir.
- Faz 1 durumu: 20 yerel, 35 sabit anahtar sözcük (+ yumuşak anahtar listeleri),
  `run`/`check`/`translate`/`locales`/`keywords` komutları, npm sarmalayıcı,
  240 test, %100 ifade kapsamı, üç işletim sisteminde determinizm işi.
- Faz 2 kod yazımı bu belgeyle yetkilendirilmez. Uygulama, ayrı bir açık onay
  ve 2.0'daki tasarım sözleşmesinin kabulüyle başlar.

## 1. Değişmezler

Her tasarım kararı aşağıdakileri korumak zorundadır:

1. **Determinizm:** Aynı kaynak + yerel + araç sürümü ⇒ bayt düzeyinde aynı
   çıktı. Rastgelelik, ağ, saat, ortam değişkeni veya sözlük sırasına bağlılık
   yok. Mevcut determinizm işi faz 2 örneklerini de kapsayacak şekilde genişler.
2. **Tahmin yok:** Eşleşme varsa çevrilir, yoksa anlaşılır ve konumlu hata
   verilir. "Yaklaşık doğru" çeviri, sessizce yutulan belirsizlik veya en olası
   anlamı seçme yok.
3. **Faz 1 bozulmaz:** Varsayılan davranış, mevcut 40 örnek, CLI sözleşmesi,
   npm sarmalayıcı ve %100 kapsam kapısı aynen kalır. Faz 2 yalnızca açıkça
   etkinleştirildiğinde devreye girer (opt-in).
4. **Kapsam kapısı:** %100 ifade kapsamı korunur; yeni yollar için test
   yazılmadan kod birleştirilmez.
5. **Güvenlik:** Çeviri dışında yürütme yok; CNL katmanı Python kodu üretir,
   onu yorumlamaz ve `eval`/`exec` ile doğrudan çalıştırmaz.

## 2. Aşamalar

### 2.0 Tasarım sözleşmesi (kod yok)

Amaç: 2.1'e başlamadan önce dilbilgisi ve sınırların yazılı hale gelmesi.

- `docs/phase-2-design.md` yazılır: kabul edilen CNL cümle kalıpları, belirsizlik
  politikası, hata biçimi, sürümleme kuralı, yerel başına yetenek bayrakları.
- Opt-in biçimi kararlaştırılır (bkz. Bölüm 4): `--cnl` bayrağı, ilk satır
  yönergesi (`# polyglot-python: xx cnl`) veya ayrı dosya son eki.
- Sözleşme kabul edilmeden 2.1 kodu yazılmaz.

Çıkış ölçütü: sözleşme belgesi + en az bir yerel için kalıp listesi taslağı +
opt-in biçimi kararı.

### 2.1 Sözcüksel ifade katmanı

Amaç: Tek tek anahtar sözcüklerin ötesinde, sabit sözcük dizilerini (ifadeler)
çevirmek — cümle dilbilgisi eklemeden.

- **Makro tablosu:** Her yerel için sürümlenmiş, veri dosyasında tutulan
  "kaynak belirteç dizisi → hedef belirteç dizisi" eşlemeleri. Tablo, mevcut
  `locales.json` doğrulamasına benzer biçimde yüklenir ve doğrulanır.
- **Eşleştirme:** Belirteç düzeyinde, en uzun eşleşme kazanır; sözcük sınırları
  `tokenize` ile korunur. Dizeler, yorumlar, f-string'ler ve nokta sonrası
  adlar dokunulmaz kalır.
- **Sıfır genişlikli makrolar:** Bir belirteci tamamen silen makrolar, satır
  başına sütun eşlemesini bozar. İlk sürümde ya reddedilir ya da sütun
  eşlemesi bu durumu ifade edecek şekilde genişletilir — karar sözleşmede.
- **Çakışma doğrulaması:** Makrolar anahtar sözcükleri gölgeleyemez; iki makro
  aynı öneki paylaşıp en-uzun-eşleşmeyle çözülemiyorsa yükleme hatası verilir.
- **Ters yön:** İngilizce → yerel çeviri yalnızca bire bir geri eşlemesi olan
  makrolar için yapılır; birden çok kaynağa giden hedef ifade geri çevrilmez.
- **Yetenek bayrakları:** Her yerel hangi makro kümesini desteklediğini bildirir;
  eksik yereller sessizce yarım çalışmaz, `locales` çıktısında görünür.
- **Testler:** Her yerelde her makro iki yönde; en-uzun-eşleşme; gölgeleme ve
  çakışma reddi; sıfır genişlik davranışı; faz-1 örneklerinin bayt düzeyinde
  değişmediği; üç işletim sisteminde determinizm.
- **Kapsam:** %100 ifade kapsamı korunur.

Çıkış ölçütü: en az bir pilot yerelde makro katmanı çalışıyor, faz-1 çıktıları
bayt düzeyinde aynı, determinizm işi genişletilmiş.

### 2.2 Kapalı küme deyim şablonları

Amaç: "eğer … ise", "her … için" gibi sınırlı sayıda deyim kalıbını çevirmek.
Bu, gerçek bir ayrıştırma aşaması gerektirir; belirteç yeniden yazımı yetmez.

- **Kapalı küme:** Yalnızca sözleşmede listelenen şablonlar desteklenir. Liste
  dışı cümle çevrilmez; hata verilir.
- **Yer tutucular:** Şablon içindeki ifadeler mevcut Python ifadeleri olmalıdır;
  serbest doğal dil alt cümle kabul edilmez.
- **Belirsizlik politikası:** Eşleş veya hata ver. Aynı cümle iki şablona
  uyuyorsa hata; sessiz tercih yok.
- **Hatalar:** Yerelleştirilmiş, satır/sütun konumlu ve hangi şablonların
  denendiğini söyleyen mesajlar.
- **Talep kapısı:** 2.2 yalnızca 2.1'in yetersiz kaldığı gerçek kullanım
  örnekleriyle gerekçelendirilirse başlar; aksi halde ertelenir.
- **Testler:** Her şablon iki yönde, belirsizlik reddi, liste dışı ret, iç içe
  kullanım, faz-1 ve 2.1 çıktılarının değişmemesi.

Çıkış ölçütü: kapalı küme çalışıyor, belirsizlikte her zaman hata, kapsam %100.

### 2.3 Sürüm ve yayın

- Hedef sürüm 0.3.0'dır; ancak **açık onay olmadan sürüm artırılmaz ve yayın
  yapılmaz**.
- CHANGELOG'a "Added" olarak CNL katmanı işlenir; faz-1 davranış değişikliği
  yoksa "Changed" maddesi eklenmez.
- Mevcut Trusted Publishing iş akışları kullanılır; npm sarmalayıcı sürümü
  Python paketiyle eşitlenir (mevcut metadata testi bunu zaten zorluyor).
- Yayın öncesi: iki işletim sisteminde iki kez çeviri + bayt/ satır sayısı
  karşılaştırması, temiz ortamda tekerlek kurulumu ve duman testi.

## 3. Eleştiri

- **CNL ile "tahmin yok" gerilimi:** Doğal dil doğası gereği belirsizdir.
  Kapalı küme + "eşleş veya hata" bunu sınırlar, ama kullanıcı beklentisi daha
  geniş olabilir. Kapsam kayması riski bu fazın en büyük riskidir.
- **Daha yüksek getirili alternatif:** Yerelleştirilmiş yerleşik fonksiyon ve
  standart kütüphane hata mesajları, CNL'den daha çok kişiye dokunabilir. Bu
  yalnızca not edildi; uygulanmadı ve plana eklenmedi.
- **Bakım maliyeti:** 20 yerel × makro tablosu + iki yönlü test matrisi kalıcı
  bakım yükü getirir. Yerel başına yetenek bayrağı ve pilot yerelle başlama
  bunu sınırlar.
- **Test patlaması:** İki yönlü yerel matrisi ve üç işletim sisteminde
  determinizm, CI süresini büyütür; iş bölümü ve önbellek gerekebilir.
- **Dilbilgisi ayrıştırıcısı:** 2.2, belirteç yeniden yazımından niteliksel
  olarak farklı bir bileşen ekler. Bu, projenin "küçük ve denetlenebilir"
  karakterini zorlar; 2.1 ile sınırlı kalınması savunulabilir.

## 4. Açık kararlar

1. Faz 2 gerçekten CNL mi, yoksa yerelleştirilmiş yerleşik/stdlib mesajları mı
   önce gelmeli?
2. Opt-in biçimi: yalnız bayrak, yalnız yönerge, ayrı dosya son eki veya
   bunların birleşimi?
3. Pilot yerel(ler) hangisi olmalı?
4. 2.1 tek başına yeterli mi, 2.2'ye geçilmeli mi?
5. 0.3.0 ne zaman ve hangi onayla yayınlanacak?

Bu kararlar verilmeden 2.0 dışında hiçbir aşama başlamaz.
