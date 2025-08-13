# Python 3.6+
# 1. ADIM için örnek kodlar

import base64
import hmac
import hashlib
import requests
import json

# API Entegrasyon Bilgileri - Mağaza paneline giriş yaparak BİLGİ sayfasından alabilirsiniz.
merchant_id = 'XXXXXX'
merchant_key = b'YYYYYYYYYYYYYY'
merchant_salt = b'ZZZZZZZZZZZZZZ'

# Müşterinizin sitenizde kayıtlı veya form vasıtasıyla aldığınız eposta adresi
email = 'XXXXXXXX'

# Tahsil edilecek tutar.
payment_amount = '' # 9.99 için 9.99 * 100 = 999 gönderilmelidir.

# Sipariş numarası: Her işlemde benzersiz olmalıdır!! Bu bilgi bildirim sayfanıza yapılacak bildirimde geri gönderilir.
merchant_oid = ''

# Müşterinizin sitenizde kayıtlı veya form aracılığıyla aldığınız ad ve soyad bilgisi
user_name = ''

# Müşterinizin sitenizde kayıtlı veya form aracılığıyla aldığınız adres bilgisi
user_address = ''

# Müşterinizin sitenizde kayıtlı veya form aracılığıyla aldığınız telefon bilgisi
user_phone = ''

# Başarılı ödeme sonrası müşterinizin yönlendirileceği sayfa
# !!! Bu sayfa siparişi onaylayacağınız sayfa değildir! Yalnızca müşterinizi bilgilendireceğiniz sayfadır!
# !!! Siparişi onaylayacağız sayfa "Bildirim URL" sayfasıdır (Bakınız: 2.ADIM Klasörü).
merchant_ok_url = 'http://www.siteniz.com/odeme_basarili.php'

# Ödeme sürecinde beklenmedik bir hata oluşması durumunda müşterinizin yönlendirileceği sayfa
# !!! Bu sayfa siparişi iptal edeceğiniz sayfa değildir! Yalnızca müşterinizi bilgilendireceğiniz sayfadır!
# !!! Siparişi iptal edeceğiniz sayfa "Bildirim URL" sayfasıdır (Bakınız: 2.ADIM Klasörü).
merchant_fail_url = 'http://www.siteniz.com/odeme_hata.php'

# Müşterinin sepet/sipariş içeriği
user_basket = ''

# ÖRNEK $user_basket oluşturma - Ürün adedine göre array'leri çoğaltabilirsiniz
"""
user_basket = base64.b64encode(json.dumps([['Örnek ürün 1', '18.00', 1],
               ['Örnek ürün 2', '33.25', 2],
               ['Örnek ürün 3', '45.42', 1]]).encode())
"""

# !!! Eğer bu örnek kodu sunucuda değil local makinanızda çalıştırıyorsanız
# buraya dış ip adresinizi (https://www.whatismyip.com/) yazmalısınız. Aksi halde geçersiz paytr_token hatası alırsınız.
user_ip = ''

# İşlem zaman aşımı süresi - dakika cinsinden
timeout_limit = '30'

# Hata mesajlarının ekrana basılması için entegrasyon ve test sürecinde 1 olarak bırakın. Daha sonra 0 yapabilirsiniz.
debug_on = '1'

# Mağaza canlı modda iken test işlem yapmak için 1 olarak gönderilebilir.
test_mode = '1'

no_installment = '0' # Taksit yapılmasını istemiyorsanız, sadece tek çekim sunacaksanız 1 yapın

# Sayfada görüntülenecek taksit adedini sınırlamak istiyorsanız uygun şekilde değiştirin.
# Sıfır (0) gönderilmesi durumunda yürürlükteki en fazla izin verilen taksit geçerli olur.
max_installment = '0'

currency = 'TL'

# Bu kısımda herhangi bir değişiklik yapmanıza gerek yoktur.
hash_str = merchant_id + user_ip + merchant_oid + email + payment_amount + user_basket.decode() + no_installment + max_installment + currency + test_mode
paytr_token = base64.b64encode(hmac.new(merchant_key, hash_str.encode() + merchant_salt, hashlib.sha256).digest())

params = {
    'merchant_id': merchant_id,
    'user_ip': user_ip,
    'merchant_oid': merchant_oid,
    'email': email,
    'payment_amount': payment_amount,
    'paytr_token': paytr_token,
    'user_basket': user_basket,
    'debug_on': debug_on,
    'no_installment': no_installment,
    'max_installment': max_installment,
    'user_name': user_name,
    'user_address': user_address,
    'user_phone': user_phone,
    'merchant_ok_url': merchant_ok_url,
    'merchant_fail_url': merchant_fail_url,
    'timeout_limit': timeout_limit,
    'currency': currency,
    'test_mode': test_mode
}

result = requests.post('https://www.paytr.com/odeme/api/get-token', params)
res = json.loads(result.text)

if res['status'] == 'success':
    print(res['token'])

    """
    context = {
        'token': res['token']
    }
    """
else:
    print(result.text)


"""
# Ödeme formunun açılması için gereken HTML kodlar / Başlangıç #

<script src="https://www.paytr.com/js/iframeResizer.min.js"></script>
<iframe src="https://www.paytr.com/odeme/guvenli/{ token }" id="paytriframe" frameborder="0" scrolling="no" style="width: 100%;"></iframe>
<script>iFrameResize({},'#paytriframe');</script>

# Ödeme formunun açılması için gereken HTML kodlar / Bitiş #
"""