import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# Grafik ayarları
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
sns.set_palette("husl")

print("=" * 70)
print("MAVİ - KEŞİFSEL VERİ ANALİZİ (EDA) VE SATIŞ TREND ANALİZİ")
print("=" * 70)

# 1. TEMİZLENMİŞ VERİLERİ OKUMA
print("\n1. TEMİZLENMİŞ VERİLERİ OKUMA")
print("-" * 40)

try:
    # Temizlenmiş CSV dosyalarını oku
    sales_df = pd.read_csv('sales_cleaned.csv', encoding='utf-8-sig')
    products_df = pd.read_csv('products_cleaned.csv', encoding='utf-8-sig')

    # Tarih kolonunu datetime'a çevir
    sales_df['DateCleaned'] = pd.to_datetime(sales_df['DateCleaned'])
    sales_df['YearMonth'] = pd.to_datetime(sales_df['YearMonth'])

    print(f"Sales verisi: {sales_df.shape[0]:,} kayıt, {sales_df.shape[1]} kolon")
    print(f"Products verisi: {products_df.shape[0]:,} kayıt, {products_df.shape[1]} kolon")

except FileNotFoundError as e:
    print(f"Hata: {e}")
    print("Önce veri temizleme scriptini çalıştırın!")
    exit()

# 2. TEMEL İSTATİSTİKSEL ANALİZ
print("\n2. TEMEL İSTATİSTİKSEL ANALİZ")
print("-" * 35)

# Satış verisi özet istatistikleri
print("SATIŞ VERİSİ ÖZET İSTATİSTİKLERİ:")
key_metrics = {
    'Toplam Satış Tutarı': f"{sales_df['Amount'].sum():,.0f} TL",
    'Ortalama İşlem Tutarı': f"{sales_df['Amount'].mean():.2f} TL",
    'Medyan İşlem Tutarı': f"{sales_df['Amount'].median():.2f} TL",
    'En Yüksek İşlem': f"{sales_df['Amount'].max():,.0f} TL",
    'En Düşük İşlem': f"{sales_df['Amount'].min():.2f} TL",
    'Toplam İşlem Sayısı': f"{len(sales_df):,}",
    'Benzersiz Mağaza': f"{sales_df['StoreCode'].nunique():,}",
    'Benzersiz Ürün': f"{sales_df['ProductCode'].nunique():,}",
}

for metric, value in key_metrics.items():
    print(f"   • {metric}: {value}")

# İade analizi
normal_sales = sales_df[~sales_df['IsReturn']]
returns = sales_df[sales_df['IsReturn']]

print(f"\nİADE ANALİZ DETAYı:")
print(f"   • Normal Satışlar: {len(normal_sales):,} işlem ({len(normal_sales) / len(sales_df) * 100:.1f}%)")
print(f"   • İadeler: {len(returns):,} işlem ({len(returns) / len(sales_df) * 100:.1f}%)")
print(f"   • Normal Satış Tutarı: {normal_sales['Amount'].sum():,.0f} TL")
print(f"   • İade Tutarı: {abs(returns['Amount'].sum()):,.0f} TL")
print(f"   • İade Oranı (Tutar): {abs(returns['Amount'].sum()) / normal_sales['Amount'].sum() * 100:.2f}%")

# 3. ZAMAN SERİSİ ANALİZİ - SATIŞ TRENDLERİ
print("\n3. ZAMAN SERİSİ ANALİZİ - SATIŞ TRENDLERİ")
print("-" * 45)

# Aylık satış trendi (sadece normal satışlar)
monthly_sales = (normal_sales.groupby('YearMonth')
                 .agg({
    'Amount': 'sum',
    'DocID': 'count',
    'AbsQuantity': 'sum'
})
                 .round(2))

monthly_sales.columns = ['Toplam_Ciro', 'İşlem_Sayısı', 'Toplam_Adet']

print("AYLIK SATIŞ TRENDİ (Normal Satışlar):")
for date, row in monthly_sales.head(12).iterrows():
    month_str = date.strftime('%Y-%m')
    print(f"   • {month_str}: {row['Toplam_Ciro']:,.0f} TL, {row['İşlem_Sayısı']:,} işlem")

# Büyüme analizi
monthly_sales['Ciro_Büyüme'] = monthly_sales['Toplam_Ciro'].pct_change() * 100
monthly_sales['İşlem_Büyüme'] = monthly_sales['İşlem_Sayısı'].pct_change() * 100

print(f"\nBÜYÜME TRENDİ ANALİZİ:")
avg_growth = monthly_sales['Ciro_Büyüme'].mean()
max_growth_month = monthly_sales['Ciro_Büyüme'].idxmax()
min_growth_month = monthly_sales['Ciro_Büyüme'].idxmin()

print(f"   • Ortalama Aylık Büyüme: {avg_growth:.2f}%")
print(
    f"   • En Yüksek Büyüme: {max_growth_month.strftime('%Y-%m')} ({monthly_sales.loc[max_growth_month, 'Ciro_Büyüme']:.2f}%)")
print(
    f"   • En Düşük Büyüme: {min_growth_month.strftime('%Y-%m')} ({monthly_sales.loc[min_growth_month, 'Ciro_Büyüme']:.2f}%)")

# Çeyreklik analiz
quarterly_sales = (normal_sales.groupby('Quarter')['Amount']
                   .agg(['sum', 'count', 'mean'])
                   .round(2))

print(f"\nÇEYREKLİK PERFORMANS:")
for quarter, row in quarterly_sales.iterrows():
    print(f"   • Q{quarter}: {row['sum']:,.0f} TL, {row['count']:,} işlem, Ort: {row['mean']:.2f} TL")

# 4. MAĞAZA PERFORMANS ANALİZİ
print("\n4. MAĞAZA PERFORMANS ANALİZİ")
print("-" * 35)

# En başarılı mağazalar
store_performance = (normal_sales.groupby('StoreCode')
                     .agg({
    'Amount': ['sum', 'count', 'mean'],
    'AbsQuantity': 'sum'
})
                     .round(2))

store_performance.columns = ['Toplam_Ciro', 'İşlem_Sayısı', 'Ortalama_İşlem', 'Toplam_Adet']
store_performance = store_performance.sort_values('Toplam_Ciro', ascending=False)

print("EN BAŞARILI MAĞAZALAR (Top 10):")
for store_code, row in store_performance.head(10).iterrows():
    print(f"   • Mağaza {store_code}: {row['Toplam_Ciro']:,.0f} TL, {row['İşlem_Sayısı']:,} işlem")

# Mağaza performans dağılımı
print(f"\MAĞAZA PERFORMANS DAĞILIMI:")
ciro_quartiles = store_performance['Toplam_Ciro'].quantile([0.25, 0.5, 0.75])
print(f"   • Alt %25 Mağaza Cirosu: {ciro_quartiles[0.25]:,.0f} TL altı")
print(f"   • Medyan Mağaza Cirosu: {ciro_quartiles[0.5]:,.0f} TL")
print(f"   • Üst %25 Mağaza Cirosu: {ciro_quartiles[0.75]:,.0f} TL üstü")

high_performers = store_performance[store_performance['Toplam_Ciro'] > ciro_quartiles[0.75]]
low_performers = store_performance[store_performance['Toplam_Ciro'] < ciro_quartiles[0.25]]

print(f"   • Yüksek Performanslı Mağaza: {len(high_performers)} adet")
print(f"   • Düşük Performanslı Mağaza: {len(low_performers)} adet")

# 5. ÜRÜN KATEGORİSİ ANALİZİ
print("\n5. ÜRÜN KATEGORİSİ ANALİZİ")
print("-" * 30)

# Sales ve Products tablolarını birleştir (analiz için)
df_analysis = normal_sales.merge(products_df, on='ProductCode', how='left')

# Ana kategori performansı
category_performance = (df_analysis.groupby('MainCategory')
                        .agg({
    'Amount': ['sum', 'count', 'mean'],
    'AbsQuantity': 'sum'
})
                        .round(2))

category_performance.columns = ['Toplam_Ciro', 'İşlem_Sayısı', 'Ortalama_İşlem', 'Toplam_Adet']
category_performance = category_performance.sort_values('Toplam_Ciro', ascending=False)

print("ANA KATEGORİ PERFORMANSI:")
total_sales = category_performance['Toplam_Ciro'].sum()
for category, row in category_performance.head(10).iterrows():
    percentage = (row['Toplam_Ciro'] / total_sales) * 100
    print(f"   • {category}: {row['Toplam_Ciro']:,.0f} TL ({percentage:.1f}%)")

# Alt kategori detayı
subcategory_performance = (df_analysis.groupby(['MainCategory', 'SubCategory'])['Amount']
                           .agg(['sum', 'count'])
                           .round(2)
                           .sort_values('sum', ascending=False))

print(f"\nALT KATEGORİ DETAY (Top 10):")
for (main_cat, sub_cat), row in subcategory_performance.head(10).iterrows():
    print(f"   • {main_cat} > {sub_cat}: {row['sum']:,.0f} TL, {row['count']:,} işlem")

# 6. ZAMAN BAZLI DESENLER
print("\n6. ZAMAN BAZLI DESENLER")
print("-" * 25)

# Haftanın günleri analizi
daily_performance = (normal_sales.groupby('WeekDay')['Amount']
                     .agg(['sum', 'count', 'mean'])
                     .round(2))

# Günleri sırala
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
daily_performance = daily_performance.reindex(day_order)

print("HAFTANIN GÜNLERİ ANALİZİ:")
total_weekly_sales = daily_performance['sum'].sum()
for day, row in daily_performance.iterrows():
    percentage = (row['sum'] / total_weekly_sales) * 100
    print(f"   • {day}: {row['sum']:,.0f} TL ({percentage:.1f}%)")

# Hafta sonu vs hafta içi
weekend_sales = normal_sales[normal_sales['IsWeekend']]['Amount'].sum()
weekday_sales = normal_sales[~normal_sales['IsWeekend']]['Amount'].sum()
weekend_percentage = (weekend_sales / (weekend_sales + weekday_sales)) * 100

print(f"\nHAFTA SONU vs HAFTA İÇİ:")
print(f"   • Hafta İçi Satışlar: {weekday_sales:,.0f} TL ({100 - weekend_percentage:.1f}%)")
print(f"   • Hafta Sonu Satışlar: {weekend_sales:,.0f} TL ({weekend_percentage:.1f}%)")

# Saatlik analiz (Time kolonu kullanarak)
sales_df['Hour'] = (sales_df['Time'] // 100).astype(int)
hourly_sales = (normal_sales.groupby(sales_df['Hour'])['Amount']
                .agg(['sum', 'count'])
                .round(2)
                .sort_index())

print(f"\nSAATLIK SATIŞ DESENLERİ (Top 5 Saat):")
top_hours = hourly_sales.sort_values('sum', ascending=False).head(5)
for hour, row in top_hours.iterrows():
    print(f"   • {hour:02d}:00: {row['sum']:,.0f} TL, {row['count']:,} işlem")

# 7. POTANSİYEL ALAN ANALİZİ
print("\n7. POTANSİYEL ALAN ANALİZİ")
print("-" * 30)

# Büyüme potansiyeli yüksek kategoriler
category_growth = df_analysis.groupby(['MainCategory', 'YearMonth'])['Amount'].sum().unstack().fillna(0)
category_growth_rate = category_growth.pct_change(axis=1).mean(axis=1).sort_values(ascending=False)

print("BÜYÜME POTANSİYELİ YÜKSEK KATEGORİLER:")
for category, growth_rate in category_growth_rate.head(5).items():
    if not np.isnan(growth_rate):
        print(f"   • {category}: %{growth_rate * 100:.2f} ortalama aylık büyüme")

# Düşük performanslı ama potansiyeli olan mağazalar
store_potential = store_performance.copy()
store_potential['Potansiyel_Skoru'] = (store_potential['İşlem_Sayısı'] / store_potential['Ortalama_İşlem'])
low_avg_high_volume = store_potential[
    (store_potential['Ortalama_İşlem'] < store_potential['Ortalama_İşlem'].median()) &
    (store_potential['İşlem_Sayısı'] > store_potential['İşlem_Sayısı'].median())
    ].head(5)

print(f"\nGELİŞTİRME POTANSİYELİ OLAN MAĞAZALAR:")
print("   (Yüksek işlem hacmi, düşük ortalama işlem tutarı)")
for store_code, row in low_avg_high_volume.iterrows():
    print(f"   • Mağaza {store_code}: {row['İşlem_Sayısı']:,} işlem, {row['Ortalama_İşlem']:.2f} TL ort.")

# İndirim analizi
discount_analysis = normal_sales.copy()
discount_analysis['İndirim_Oranı'] = np.where(
    discount_analysis['Amount'] != 0,
    (discount_analysis['DiscountAmount'] / discount_analysis['Amount']) * 100,
    0
)

print(f"\nİNDİRİM ANALİZİ:")
print(f"   • Ortalama İndirim Oranı: %{discount_analysis['İndirim_Oranı'].mean():.2f}")
print(f"   • İndirimli İşlem Oranı: %{(discount_analysis['DiscountAmount'] != 0).mean() * 100:.1f}")

high_discount = discount_analysis[discount_analysis['İndirim_Oranı'] > 20]
print(
    f"   • %20+ İndirimli İşlem: {len(high_discount):,} adet ({len(high_discount) / len(discount_analysis) * 100:.1f}%)")

# 8. ANOMALY VE AYKIRI DEĞER TESPİTİ
print("\n8. ANOMALY VE AYKIRI DEĞER TESPİTİ")
print("-" * 40)

# Amount için aykırı değer analizi
Q1 = normal_sales['Amount'].quantile(0.25)
Q3 = normal_sales['Amount'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = normal_sales[(normal_sales['Amount'] < lower_bound) | (normal_sales['Amount'] > upper_bound)]

print(f"AYKIRI DEĞER ANALİZİ (Amount):")
print(f"   • Alt Sınır: {lower_bound:.2f} TL")
print(f"   • Üst Sınır: {upper_bound:.2f} TL")
print(f"   • Aykırı Değer Sayısı: {len(outliers):,} ({len(outliers) / len(normal_sales) * 100:.2f}%)")
print(f"   • En Yüksek İşlem: {normal_sales['Amount'].max():,.2f} TL")

# Günlük satış anomalileri
daily_sales = normal_sales.groupby('DateString')['Amount'].sum()
daily_mean = daily_sales.mean()
daily_std = daily_sales.std()
daily_anomalies = daily_sales[(daily_sales > daily_mean + 2 * daily_std) |
                              (daily_sales < daily_mean - 2 * daily_std)]

print(f"\nGÜNLÜK SATIŞ ANOMALİLERİ:")
print(f"   • Ortalama Günlük Satış: {daily_mean:,.0f} TL")
print(f"   • Standart Sapma: {daily_std:,.0f} TL")
print(f"   • Anomali Gün Sayısı: {len(daily_anomalies)}")

if len(daily_anomalies) > 0:
    print("   • Anomali Günler:")
    for date, amount in daily_anomalies.head(5).items():
        print(f"     - {date}: {amount:,.0f} TL")

# 9. ÖZET VE ÖNERİLER
print("\n9. ÖZET VE ÖNERİLER")
print("-" * 25)

print("ÖNEMLİ BULGULAR:")
print(f"   • En karlı kategori: {category_performance.index[0]}")
print(f"   • En yüksek ciro ayı: {monthly_sales['Toplam_Ciro'].idxmax().strftime('%Y-%m')}")
print(f"   • En başarılı mağaza: {store_performance.index[0]}")
print(f"   • İade oranı: %{len(returns) / len(sales_df) * 100:.1f}")

print(f"\nAKSIYON ÖNERİLERİ:")
print("   1. Düşük performanslı mağazalara odaklanın")
print("   2. Büyüme potansiyeli yüksek kategorileri destekleyin")
print("   3. Hafta sonu satış stratejilerini gözden geçirin")
print("   4. İndirim politikalarını optimize edin")
print("   5. Aykırı yüksek işlemleri analiz edin")

print("\n" + "=" * 70)
print("KEŞİFSEL VERİ ANALİZİ TAMAMLANDI! 🎉")
print("=" * 70)

print(f"\nnaliz Edilen Veri:")
print(f"   • {len(normal_sales):,} normal satış işlemi")
print(f"   • {sales_df['StoreCode'].nunique():,} mağaza")
print(f"   • {len(products_df):,} ürün")
print(f"   • {len(monthly_sales):,} aylık veri nokta")

print(f"\nSonraki Adım Önerileri:")
print("   • Tahmin modelleri geliştirin")
print("   • Dashboard oluşturun")
print("   • A/B test stratejileri tasarlayın")
print("   • Müşteri segmentasyonu yapın")