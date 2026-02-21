

---

# Vision System Technical Documentation

---

# 1. Amaç

Bu dosya, üst kameradan (top camera) alınan görüntü üzerinde:

* Çizgi tespiti
* Çizgi merkezinin hesaplanması
* Çizginin yön açısının belirlenmesi
* Keskin dönüş (turn) algılama

işlemlerini gerçekleştiren görüntü işleme modülünü açıklamaktadır.

Sistem OpenCV ve NumPy kullanarak gerçek zamanlı çalışacak şekilde tasarlanmıştır.

---

# 2. Kullanılan Kütüphaneler

```python
import cv2
import numpy as np
from abc import ABC, abstractmethod
import math
```

### cv2

OpenCV kütüphanesidir. Görüntü işleme, contour bulma, PCA hesaplama gibi işlemler için kullanılır.

### numpy

Matris işlemleri ve sayısal hesaplamalar için kullanılır.

### abc

Soyut sınıf (abstract base class) tanımlamak için kullanılır.
Modüler ve genişletilebilir mimari sağlar.

### math

Trigonometrik işlemler (atan2, degree dönüşümü) için kullanılır.

---

# 3. BaseVision (Soyut Sınıf)

```python
class BaseVision(ABC):
    @abstractmethod
    def process(self, frame):
        pass
```

## Amaç

Bu sınıf tüm vision modüllerinin ortak arayüzünü tanımlar.

### process(frame)

* Girdi: Kamera görüntüsü (frame)
* Çıktı: İşlenmiş bilgi (dictionary formatında)

Bu sayede farklı kamera sistemleri aynı kontrol katmanına bağlanabilir.

---

# 4. TopCameraVision Sınıfı

Bu sınıf üst kamera için çizgi algılama sistemini implement eder.

---

# 4.1 **init** (Başlatıcı)

```python
self.lower = np.array([0, 0, 0])
self.upper = np.array([180, 255, 50])
self.min_area = 1000
```

## HSV Threshold

Görüntü HSV renk uzayına dönüştürülür.

HSV:

* H → Hue (renk tonu)
* S → Saturation (doygunluk)
* V → Value (parlaklık)

Burada:

```
Lower = [0, 0, 0]
Upper = [180, 255, 50]
```

Bu aralık:

→ Düşük parlaklıktaki (karanlık) bölgeleri seçer
→ Siyah çizgiyi izole etmek için kullanılır

## min_area

Minimum contour alanı.

Amaç:

* Gürültüleri elemek
* Küçük lekeleri çizgi sanmamak

---

# 4.2 threshold_strip(frame)

```python
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, self.lower, self.upper)
```

## Adım 1 – Renk Uzayı Dönüşümü

BGR → HSV dönüşümü yapılır.

HSV, renk bazlı segmentasyon için daha stabildir.

## Adım 2 – Maskeleme

`inRange()` fonksiyonu:

* Belirlenen HSV aralığında olan pikselleri beyaz yapar
* Diğerlerini siyah yapar

Sonuç: Binary mask (siyah-beyaz görüntü)

---

## Morfolojik İşlemler

```python
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
```

### MORPH_CLOSE

* Küçük boşlukları kapatır
* Çizgideki kopuklukları giderir

### MORPH_OPEN

* Gürültüleri temizler
* Küçük beyaz noktaları yok eder

Amaç:
→ Daha temiz ve tek parça contour elde etmek

---

# 4.3 get_largest_contour(mask)

```python
contours, _ = cv2.findContours(...)
```

## Amaç

Maskeden tüm contour’ları bulur.

### cv2.RETR_EXTERNAL

Sadece dış contour’ları alır.

### cv2.CHAIN_APPROX_SIMPLE

Gereksiz nokta tekrarlarını azaltır.

---

## En Büyük Contour Seçimi

```python
largest = max(contours, key=cv2.contourArea)
```

En büyük alanlı contour seçilir.

Neden?

→ Çizgi genellikle görüntüdeki en büyük siyah bölgedir.

---

## Alan Kontrolü

```python
if cv2.contourArea(largest) < self.min_area:
    return None
```

Gürültü filtreleme mekanizmasıdır.

---

# 4.4 compute_centroid(contour)

```python
M = cv2.moments(contour)
```

## Moments Nedir?

Momentler, şeklin geometrik özelliklerini verir.

Özellikle:

* m00 → alan
* m10, m01 → ağırlıklı koordinatlar

---

## Centroid Hesabı

```
cx = m10 / m00
cy = m01 / m00
```

Bu:

→ Çizginin kütle merkezini verir.

Bu değer robotun hata hesaplamasında kullanılır.

---

# 4.5 compute_angle(contour)

Bu fonksiyon çizginin yön açısını hesaplar.

---

## PCA Kullanımı

```python
mean, eigenvectors = cv2.PCACompute(...)
```

Principal Component Analysis:

→ Contour noktalarının ana yönünü bulur.

En büyük eigenvector:

→ Çizginin baskın yönünü temsil eder.

---

## Açı Hesabı

```python
angle = math.degrees(math.atan2(vy, vx))
```

atan2:

→ 2D vektörün açısını verir.

---

## Normalizasyon

```python
if angle > 90: angle -= 180
if angle < -90: angle += 180
```

Amaç:

Açıyı -90 ile +90 derece arasına sıkıştırmak.

Bu:

→ Kontrol sistemini daha stabil yapar.

---

# 4.6 detect_turn(contour, frame)

Amaç:

Keskin dönüşleri algılamak.

---

## Bounding Box

```python
x, y, w, h = cv2.boundingRect(contour)
```

Contour’ü kapsayan en küçük dikdörtgeni hesaplar.

---

## Oran Kontrolü

```python
if w > h * 1.5:
```

Eğer genişlik yüksekliğe göre çok büyükse:

→ Çizgi yataylaşmış demektir
→ Büyük ihtimalle dönüş bölgesindeyiz

---

## Yön Belirleme

Centroid'in frame merkezine göre konumuna bakılır.

```
cx > frame_center → RIGHT
else → LEFT
```

---

# 4.7 process(frame)

Bu ana fonksiyondur.

Tüm pipeline burada çalışır.

---

## Adım 1

Maske oluşturulur.

## Adım 2

En büyük contour bulunur.

## Adım 3

Centroid hesaplanır.

## Adım 4 – Hata Hesabı

```python
center_error = (cx - frame_center) / frame_center
```

Normalize edilmiş hata:

* -1 → Tam sol
* 0 → Ortada
* +1 → Tam sağ

Bu değer PID sistemine girer.

---

## Adım 5 – Açı

Çizginin eğimi hesaplanır.

---

## Adım 6 – Turn Detection

Keskin dönüş kontrol edilir.

---

## Debug Çizimleri

```python
cv2.circle(...)
cv2.line(...)
```

* Kırmızı nokta → centroid
* Mavi çizgi → frame merkezi

Amaç:
→ Görsel debug

---

# 5. Fonksiyon Çıktısı

Fonksiyon şu formatta bir dictionary döndürür:

```python
{
    "line_found": True/False,
    "center_error": float,
    "angle": float,
    "turn_detected": bool,
    "turn_direction": "LEFT"/"RIGHT"/None
}
```

Bu yapı:

→ Controller katmanından bağımsız
→ Modüler
→ Test edilebilir

---

# 6. Genel Mimari Yaklaşım

Bu vision sistemi:

* Renk segmentasyonu
* Gürültü temizleme
* Geometrik analiz
* Özellik çıkarımı

adımlarından oluşan klasik bir görüntü işleme pipeline’ıdır.

Makine öğrenmesi içermez.

Tamamen deterministik ve gerçek zamanlı çalışacak şekilde tasarlanmıştır.

---

# 7. Neden Bu Yaklaşım Seçildi?

✔ Hesaplama maliyeti düşüktür
✔ Gerçek zamanlıdır
✔ PID ile entegre çalışmaya uygundur
✔ Donanım dostudur
✔ Debug edilmesi kolaydır

---

# 8. Sistem Özeti

Bu modül:

* Görüntüden çizgiyi izole eder
* Çizgi merkezini hesaplar
* Çizgi yönünü belirler
* Dönüş algılar
* Kontrol sistemine sayısal hata üretir

Bu veriler motor kontrol katmanında kullanılır.

---

hazırlayabilirim.
