Bagaimana menggunakaan :
------------------------

1. Create database di mysql dengan nama : db_news

2. Git Clone https://github.com/Ione03/django_news_aes256.git

3. cd django_news_aes256

4. Install all library ketik : pip install -r requirements.txt

5. Create tabel ketik : python manage.py migrate

6. Untuk login ke halaman dashboard ketik : python manage.py createsuperuser

7. Masukkan data awal ke database ketik : python manage.py loaddata db/categories.json

8. Jalan aplikasi di local ketik : python manage.py runserver

9. Buka browser ketik : 127.0.0.1:8000

10. Ke halaman dashboard ketik : 127.0.0.1:8000/login
    (masukkan username dan password sesuai dengan yang diinput di step 6 di atas)

Mulai menggunakan aplikasi :
----------------------------

11. Di halaman dashboard masukkan data news, dan documents

12. Refresh tampilan depan, klik di bagian document untuk mencoba download file

13. Link download file hanya aktif selama 1 menit (ubah parameter ini di setting.py)

14. Setelah 1 menit link akan otomatis mati

15. User dengan IP yang sama hanya di perkenankan download satu jenis file satu kali saja, jika sudah expired file dapat di download setelah 24 jam

16. Library aes256 dapat diinstall dengan perintah : pip install python-aes256 (perintah ini sudah dijalankan di step 4 di atas)

