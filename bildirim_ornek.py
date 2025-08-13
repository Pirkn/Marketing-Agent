# Python 3.6+
# Django Web Framework referans alınarak hazırlanmıştır
# 2. ADIM için örnek kodlar
"""
ÖNEMLİ UYARILAR
1) Bu sayfaya oturum (SESSION) ile veri taşıyamazsınız. Çünkü bu sayfa müşterilerin yönlendirildiği bir sayfa değildir.
2) Entegrasyonun 1. ADIM'ında gönderdiğniz merchant_oid değeri bu sayfaya POST ile gelir. Bu değeri kullanarak veri tabanınızdan ilgili siparişi tespit edip onaylamalı veya iptal etmelisiniz.
3) Aynı sipariş için birden fazla bildirim ulaşabilir (Ağ bağlantı sorunları vb. nedeniyle). Bu nedenle öncelikle siparişin durumunu veri tabanınızdan kontrol edin, eğer onaylandıysa tekrar işlem yapmayın. Örneği aşağıda bulunmaktadır.
"""

import base64
import hashlib
import hmac

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def callback(request):

    if request.method != 'POST':
        return HttpResponse(str(''))

    post = request.POST

    # API Entegrasyon Bilgileri - Mağaza paneline giriş yaparak BİLGİ sayfasından alabilirsiniz.
    merchant_key = b'YYYYYYYYYYYYYY'
    merchant_salt = 'ZZZZZZZZZZZZZZ'

    # Bu kısımda herhangi bir değişiklik yapmanıza gerek yoktur.
    # POST değerleri ile hash oluştur.
    hash_str = post['merchant_oid'] + merchant_salt + post['status'] + post['total_amount']
    hash = base64.b64encode(hmac.new(merchant_key, hash_str.encode(), hashlib.sha256).digest())

    # Oluşturulan hash'i, paytr'dan gelen post içindeki hash ile karşılaştır
    # (isteğin paytr'dan geldiğine ve değişmediğine emin olmak için)
    # Bu işlemi yapmazsanız maddi zarara uğramanız olasıdır.
    if hash != post['hash']:
        return HttpResponse(str('PAYTR notification failed: bad hash'))

    # BURADA YAPILMASI GEREKENLER
    # 1) Siparişin durumunu post['merchant_oid'] değerini kullanarak veri tabanınızdan sorgulayın.
    # 2) Eğer sipariş zaten daha önceden onaylandıysa veya iptal edildiyse "OK" yaparak sonlandırın.

    if post['status'] == 'success':  # Ödeme Onaylandı
        """
        BURADA YAPILMASI GEREKENLER
        1) Siparişi onaylayın.
        2) Eğer müşterinize mesaj / SMS / e-posta gibi bilgilendirme yapacaksanız bu aşamada yapmalısınız.
        3) 1. ADIM'da gönderilen payment_amount sipariş tutarı taksitli alışveriş yapılması durumunda değişebilir. 
        Güncel tutarı post['total_amount'] değerinden alarak muhasebe işlemlerinizde kullanabilirsiniz.
        """
        print(request)
    else:  # Ödemeye Onay Verilmedi
        """
        BURADA YAPILMASI GEREKENLER
        1) Siparişi iptal edin.
        2) Eğer ödemenin onaylanmama sebebini kayıt edecekseniz aşağıdaki değerleri kullanabilirsiniz.
        post['failed_reason_code'] - başarısız hata kodu
        post['failed_reason_msg'] - başarısız hata mesajı
        """
        print(request)

    # Bildirimin alındığını PayTR sistemine bildir.
    return HttpResponse(str('OK'))
