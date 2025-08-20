import pandas as pd
import matplotlib.pyplot as plt


# Türkçe karakterler için
plt.rcParams['font.family'] = ['DejaVu Sans']

print("=" * 60)
print("MAVİ.XLSX - VERİ MANIPÜLASYONU VE TEMİZLEME")
print("=" * 60)

# 1. VERİ OKUMA
print("\n1. VERİ OKUMA İŞLEMİ")
print("-" * 30)

try:
    # Excel dosyasını oku
    sales_df = pd.read_excel('mavi.xlsx', sheet_name='Sales')
    products_df = pd.read_excel('mavi.xlsx', sheet_name='Products')

    print(f"Sales tablosu: {sales_df.shape[0]:,} satır, {sales_df.shape[1]} sütun")
    print(f"Products tablosu: {products_df.shape[0]:,} satır, {products_df.shape[1]} sütun")

except FileNotFoundError:
    print("Hata: mavi.xlsx dosyası bulunamadı!")
    print("Lütfen dosyanın mevcut dizinde olduğundan emin olun.")
    exit()

# 2. VERİ KALİTESİ KONTROLÜ
print("\n2. VERİ KALİTESİ KONTROLÜ")
print("-" * 30)

print("\nSALES TABLOSU EKSİK VERİ ANALİZİ:")
sales_missing = sales_df.isnull().sum()
sales_missing_pct = (sales_missing / len(sales_df)) * 100
missing_summary = pd.DataFrame({
    'Eksik_Sayı': sales_missing,
    'Eksik_Yüzde': sales_missing_pct.round(2)
})
print(missing_summary[missing_summary['Eksik_Sayı'] > 0])

if sales_missing.sum() == 0:
    print("Sales tablosunda eksik veri yok!")

print("\nPRODUCTS TABLOSU EKSİK VERİ ANALİZİ:")
products_missing = products_df.isnull().sum()
products_missing_pct = (products_missing / len(products_df)) * 100
products_missing_summary = pd.DataFrame({
    'Eksik_Sayı': products_missing,
    'Eksik_Yüzde': products_missing_pct.round(2)
})
print(products_missing_summary[products_missing_summary['Eksik_Sayı'] > 0])

# 3. TARİH VERİSİ TEMİZLEME
print("\n3. TARİH VERİSİ TEMİZLEME VE DÖNÜŞTÜRME")
print("-" * 45)

# Tarih kolonunu kontrol et ve düzelt
print("Tarih formatı kontrol ediliyor...")

# Tarih verisi zaten datetime formatında mı kontrol et
if sales_df['Date'].dtype == 'datetime64[ns]':
    print("Tarih verisi zaten datetime formatında!")
    sales_df['DateCleaned'] = sales_df['Date']
else:
    print("Tarih verisi dönüştürülüyor...")
    # Eğer numeric ise Excel serial number formatından çevir
    if pd.api.types.is_numeric_dtype(sales_df['Date']):
        sales_df['DateCleaned'] = pd.to_datetime(sales_df['Date'], origin='1899-12-30', unit='D')
    else:
        # String formatında ise parse et
        sales_df['DateCleaned'] = pd.to_datetime(sales_df['Date'], errors='coerce')

# Yeni tarih kolonları ekle
sales_df['Year'] = sales_df['DateCleaned'].dt.year
sales_df['Month'] = sales_df['DateCleaned'].dt.month
sales_df['Quarter'] = sales_df['DateCleaned'].dt.quarter
sales_df['DayOfWeek'] = sales_df['DateCleaned'].dt.dayofweek
sales_df['WeekDay'] = sales_df['DateCleaned'].dt.day_name()
sales_df['MonthName'] = sales_df['DateCleaned'].dt.month_name()
sales_df['YearMonth'] = sales_df['DateCleaned'].dt.to_period('M')
sales_df['QuarterYear'] = sales_df['DateCleaned'].dt.to_period('Q')
sales_df['DateString'] = sales_df['DateCleaned'].dt.strftime('%Y-%m-%d')

# Tarih aralığını göster
min_date = sales_df['DateCleaned'].min()
max_date = sales_df['DateCleaned'].max()
date_range = (max_date - min_date).days

print(f"Tarih aralığı: {min_date.strftime('%Y-%m-%d')} - {max_date.strftime('%Y-%m-%d')}")
print(f"Toplam gün sayısı: {date_range} gün")
print(f"{len(sales_df)} kayıt için tarih bilgisi eklendi")

# 4. NUMERİK VERİLER VE YENİ HESAPLAMALAR
print("\n4. NUMERİK VERİLER VE YENİ HESAPLAMALAR")
print("-" * 42)

# Yeni hesaplanmış kolonlar
sales_df['NetAmount'] = sales_df['Amount'] + sales_df['DiscountAmount']
sales_df['AbsQuantity'] = sales_df['Quantity'].abs()
sales_df['IsReturn'] = sales_df['ReturnFlag'] == 1
sales_df['IsWeekend'] = sales_df['DayOfWeek'].isin([5, 6])  # Cumartesi=5, Pazar=6

print("Yeni kolonlar eklendi:")
print("   - NetAmount: Indirim dahil net tutar")
print("   - AbsQuantity: Mutlak miktar")
print("   - IsReturn: İade durumu (True/False)")
print("   - IsWeekend: Hafta sonu kontrolü")


# 5. PRODUCTS VERİSİNİ TEMİZLEME
print("\n5. PRODUCTS VERİSİNİ TEMİZLEME")
print("-" * 30)

# Eksik İngilizce kategorileri Türkçe ile doldur
print("Eksik İngilizce kategoriler Türkçe karşılıkları ile dolduruluyor...")

products_df['MainCategoryEN'] = products_df['MainCategoryEN'].fillna(products_df['MainCategory'])
products_df['CategoryEN'] = products_df['CategoryEN'].fillna(products_df['Category'])
products_df['SubCategoryEN'] = products_df['SubCategoryEN'].fillna(products_df['SubCategory'])
products_df['SubCategoryClassEN'] = products_df['SubCategoryClassEN'].fillna(products_df['SubCategoryClass'])

# Yeni kategorik kolonlar
products_df['FullCategoryPath'] = (products_df['Class'] + ' > ' +
                                   products_df['MainCategory'] + ' > ' +
                                   products_df['Category'] + ' > ' +
                                   products_df['SubCategory'])

products_df['ProductLevel'] = products_df['SubCategoryClass'].apply(
    lambda x: 'Detailed' if pd.notna(x) else 'Basic'
)

print("Products tablosu temizlendi")
print(f"{products_df['MainCategoryEN'].notna().sum()} / {len(products_df)} kayıt için İngilizce kategori tamamlandı")

# 6. VERİLERİ BİRLEŞTİRME
print("\n6. VERİLERİ BİRLEŞTİRME")
print("-" * 25)

# 7. VERİ KALİTESİ SONUÇ RAPORU
print("\n7. VERİ KALİTESİ SONUÇ RAPORU")
print("-" * 35)

print("TEMEL İSTATİSTİKLER:")
print(f"   • Toplam satış kaydı: {len(sales_df):,}")
print(f"   • Benzersiz mağaza sayısı: {sales_df['StoreCode'].nunique():,}")
print(f"   • Benzersiz ürün sayısı: {sales_df['ProductCode'].nunique():,}")
print(f"   • Tarih aralığı: {date_range} gün")

# 8. VERİYİ KAYDETME
print("\n8. TEMİZLENMİŞ VERİYİ KAYDETME")
print("-" * 35)

try:
    # Temizlenmiş veriyi kaydet
    sales_df.to_csv('sales_cleaned.csv', index=False, encoding='utf-8-sig')
    products_df.to_csv('products_cleaned.csv', index=False, encoding='utf-8-sig')

    print("Dosyalar başarıyla kaydedildi:")
    print("   • sales_cleaned.csv")
    print("   • products_cleaned.csv")

except Exception as e:
    print(f"Kaydetme hatası: {e}")

print("\n" + "=" * 60)
print("VERİ TEMİZLEME SÜRECİ TAMAMLANDI!")
print("=" * 60)

