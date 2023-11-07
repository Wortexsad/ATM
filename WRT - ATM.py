import tkinter as tk 
from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
from time import strftime
import sqlite3
from tkinter import Tk, Canvas, Entry, Button, PhotoImage
import os
import random
import string
from PIL import Image, ImageTk
from pathlib import Path
from datetime import datetime


# İşlem Geçmişi DataBase

connection = sqlite3.connect("transaction_history.db")
cursor = connection.cursor()

# İşlem geçmişi tablosunu oluşturun
create_table_query = """
CREATE TABLE IF NOT EXISTS transaction_history (
    id INTEGER PRIMARY KEY,
    user TEXT,
    amount REAL,
    description TEXT
);
"""
cursor.execute(create_table_query)
connection.commit()

# İşlem Geçmişi DataBase







OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\90542\Desktop\build\assets\frame0")

def relative_to_assets(file):
    # assets klasörüne göre dosyanın yolunu oluştur
    assets_folder = "assets"  # Assets klasörünün adını güncelleyin
    file_path = os.path.join(assets_folder, file)
    return file_path

class ATM:

    def relative_to_assets(file):
    # assets klasörüne göre dosyanın yolunu oluştur
        assets_folder = "assets"  # Assets klasörünün adını güncelleyin
        file_path = os.path.join(assets_folder, file)
        return file_path

    def __init__(self, ana_pencere):
        self.ana_pencere = ana_pencere
        self.ana_pencere.title("WRT - ATM")
        self.ana_pencere.geometry("768x500")
        self.ana_pencere.configure(bg="#FFFFFF")

        # Veritabanı bağlantısını oluştur
        self.baglanti = sqlite3.connect("kullanicilar.db")
        self.cursor = self.baglanti.cursor()

        # Kredi başvuruları tablosunu oluştur
        create_table_query = """
        CREATE TABLE IF NOT EXISTS kredi_basvurulari (
            kullanici_adi TEXT,
            kredi_miktari INTEGER,
            durum TEXT,
            kredi_basvuru_id INTEGER
        );
        """
        # Kredi başvuruları tablosuna yeni bir sütun ekleyin
        

        self.cursor.execute(create_table_query)

        # Kullanıcılar tablosunu oluştur
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            kullanici_adi TEXT PRIMARY KEY,
            sifre TEXT,
            bakiye REAL,
            borc REAL,
            iban TEXT,
            bloke INTEGER
        );
        ''')

        # Bloke talepleri tablosunu oluştur
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS bloke_talepler (
            kullanici_adi TEXT,
            talep_mesaji TEXT
        );
        ''')
        # Destek Talepler 
        


       
        
        #ADMİN GİRİŞ BİLGİLERİ 
        self.admin_kullanici_adi = "admin"
        self.admin_sifre = "pass"


        # Diğer sınıf özelliklerini başlat
        self.transaction_history = []
        self.bakiye = 1000
        self.borc = 0
        self.kullanici_adi = ""
        self.sifre = ""
        self.aktif_kullanici = None
        self.kullanici_iban = ""
        self.bloke = 0
        self.sonuc_etiketi = tk.Label(self.ana_pencere, text="")
        self.sonuc_etiketi.grid(row=5, column=1)
        self.giris_ekrani()
      
    
    
    def bloke_acma_taleplerini_incele(self):
        self.temizle_ekran()

        # Veritabanından bloke açma taleplerini alın
        self.cursor.execute("SELECT * FROM bloke_talepler")
        talepler = self.cursor.fetchall()

        if talepler:
            talep_listesi = "Bloke Açma Talepleri:\n"
            for talep in talepler:
                talep_listesi += f"Kullanıcı Adı: {talep[0]}\nTalep Mesajı: {talep[1]}\n\n"

            self.talep_listesi_label = tk.Label(self.ana_pencere, text=talep_listesi)
            self.talep_listesi_label.grid(row=1, column=1)
             
            self.temizle_ekran
            self.onayla_button = tk.Button(self.ana_pencere, text="Bloke Açma Taleplerini İşle", command=self.bloke_acma_taleplerini_isle)
            self.onayla_button.grid(row=2, column=1)
            self.cıkıs_button = tk.Button(self.ana_pencere, text="Çıkış", command=self.admin_cikis)
            self.cıkıs_button.grid(row=4, column=2)

        else:
            messagebox.showerror("İncelenecek Talep Bulunmamakta")
            self.admin_menu()


    def para_transferi(self):
        hedef_kullanici_adi = simpledialog.askstring("Para Transferi", "Para transferi yapmak istediğiniz kullanıcının adını girin:")
        miktar = simpledialog.askfloat("Para Transferi", "Transfer etmek istediğiniz miktarı girin (TL):")

        if hedef_kullanici_adi and miktar:
            if miktar > 0 and self.aktif_kullanici[2] >= miktar:
                self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (hedef_kullanici_adi,))
                hedef_kullanici = self.cursor.fetchone()

                if hedef_kullanici:
                    # Para transferi işlemini gerçekleştir
                    self.aktif_kullanici = list(self.aktif_kullanici)
                    hedef_kullanici = list(hedef_kullanici)

                    self.aktif_kullanici[2] -= miktar
                    hedef_kullanici[2] += miktar

                    self.aktif_kullanici = tuple(self.aktif_kullanici)
                    hedef_kullanici = tuple(hedef_kullanici)

                    self.cursor.execute("UPDATE kullanicilar SET bakiye=? WHERE kullanici_adi=?", (self.aktif_kullanici[2], self.kullanici_adi))
                    self.cursor.execute("UPDATE kullanicilar SET bakiye=? WHERE kullanici_adi=?", (hedef_kullanici[2], hedef_kullanici_adi))
                    self.baglanti.commit()

                    # İşlem geçmişini güncelle
                    self.kaydet_islem_gecmisi(self.aktif_kullanici[2], f"{miktar} TL gönderildi", miktar)
                    self.kaydet_islem_gecmisi(hedef_kullanici[2], f"{miktar} TL alındı", miktar)

                    # Kullanıcıya bilgi ver
                    messagebox.showinfo("Para Transferi", f"{miktar} TL, {hedef_kullanici_adi} kullanıcısına transfer edildi. Yeni bakiyeniz: {self.aktif_kullanici[2]} TL")
                else:
                    messagebox.showerror("Hata", "Hedef kullanıcı bulunamadı.")
            else:
                messagebox.showerror("Hata", "Geçersiz miktar veya yetersiz bakiye.")
        self.menu_goster()
        

    def kaydet_islem_gecmisi(self, kullanici_id, aciklama, mikta):
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO transactions (user_id, description, date) VALUES (?, ?, ?)",
                    (kullanici_id, aciklama, tarih))
        connection.commit()

    def bloke_acma_taleplerini_isle(self):
        # Bloke açma taleplerini inceledikten sonra uygun aksiyonları alabilirsiniz.
        # Örneğin, kullanıcının blokesini kaldırabilirsiniz.
        # Bu işlem için kullanıcı adını alarak veritabanında blokeyi kaldırabilirsiniz.

        # Örnek: Kullanıcının blokesini kaldırma
        kullanici_adi = simpledialog.askstring("Bloke Açma", "Blokesi kaldırılacak kullanıcının adını girin:")

        if kullanici_adi:
            self.cursor.execute("UPDATE kullanicilar SET bloke=0 WHERE kullanici_adi=?", (kullanici_adi,))
            self.cursor.execute("DELETE FROM bloke_talepler WHERE kullanici_adi=?", (kullanici_adi,))  # Talepleri sil
            self.baglanti.commit()
            messagebox.showinfo("Bloke Açma", f"{kullanici_adi} kullanıcısının blokesi kaldırıldı.")

        # İşlem tamamlandığında, yöneticiyi talep listesi ekranına geri götürebilirsiniz.
        self.bloke_acma_taleplerini_incele()
        self.admin_menu()

    def giris_ekrani(self):
        self.temizle_ekran()

        self.kullanici_adi_label = tk.Label(self.ana_pencere, text="Kullanıcı Adı:")
        self.kullanici_adi_label.grid(row=1, column=0)
        self.kullanici_adi_entry = tk.Entry(self.ana_pencere)
        self.kullanici_adi_entry.grid(row=1, column=1)

        self.sifre_label = tk.Label(self.ana_pencere, text="Şifre:")
        self.sifre_label.grid(row=2, column=0)
        self.sifre_entry = tk.Entry(self.ana_pencere, show="*")
        self.sifre_entry.grid(row=2, column=1)

        self.giris_button = tk.Button(self.ana_pencere, text="Giriş", command=self.giris_kontrol)
        self.giris_button.grid(row=3, column=1)

        self.kayit_ol_button = tk.Button(self.ana_pencere, text="Kayıt Ol", command=self.kayit_ol)
        self.kayit_ol_button.grid(row=4, column=1)
    
    def relative_to_assets(path: str) -> Path:
        return ASSETS_PATH / Path(path)

    def bloke_acma_talebi_kaydet(self):
        kullanici_adi = self.kullanici_adi_entry.get()
        talep_mesaji = self.talep_mesaji_entry.get()

        # Kullanıcı adı ve talep mesajını kaydedebilir ve bu verileri yöneticiye iletebilirsiniz.
        # Yönetici bu talepleri daha sonra inceleyebilir ve uygun aksiyonları alabilir.
        # Örnek olarak, bir veritabanına veya dosyaya bu talepleri kaydedebilirsiniz.
        
        # Örnek: Veritabanına talepleri kaydetme
        self.cursor.execute("INSERT INTO bloke_talepler (kullanici_adi, talep_mesaji) VALUES (?, ?)", (kullanici_adi, talep_mesaji))
        self.baglanti.commit()

        # Talep gönderildiğinde kullanıcıya bir onay mesajı göstermek isteyebilirsiniz.
        messagebox.showinfo("Talep Gönderildi", "Bloke açma talebiniz gönderildi. Yönetici tarafından incelenecek.")

        # Kullanıcıyı ana menüye geri döndürün
        self.giris_ekrani()
    def bloke_acma_talebi_gonder(self):
        self.temizle_ekran()

        self.talep_label = tk.Label(self.ana_pencere, text="Bloke Açma Talebi Gönder")
        self.talep_label.grid(row=1, column=1)

        self.kullanici_adi_label = tk.Label(self.ana_pencere, text="Kullanıcı Adı:")
        self.kullanici_adi_label.grid(row=2, column=0)
        self.kullanici_adi_entry = tk.Entry(self.ana_pencere)
        self.kullanici_adi_entry.grid(row=2, column=1)

        self.talep_mesaji_label = tk.Label(self.ana_pencere, text="Talep Mesajı:")
        self.talep_mesaji_label.grid(row=3, column=0)
        self.talep_mesaji_entry = tk.Entry(self.ana_pencere)
        self.talep_mesaji_entry.grid(row=3, column=1)

        self.talep_gonder_button = tk.Button(self.ana_pencere, text="Talep Gönder", command=self.bloke_acma_talebi_kaydet)
        self.talep_gonder_button.grid(row=4, column=1)

        

        

    def temizle_ekran(self):
        for widget in self.ana_pencere.winfo_children():
            widget.destroy()

    def giris_kontrol(self):
        self.kullanici_adi = self.kullanici_adi_entry.get()
        self.sifre = self.sifre_entry.get()

        if self.kullanici_adi == self.admin_kullanici_adi and self.sifre == self.admin_sifre:
            self.aktif_kullanici = (self.kullanici_adi, self.sifre, 0, 0, "", 0)
            self.admin_menu()
        else:
            self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (self.kullanici_adi,))
            kullanici = self.cursor.fetchone()

            if kullanici and kullanici[1] == self.sifre:
                if kullanici[5] == 1:
                    self.temizle_ekran()
                    self.bloke_acma_talebi_gonder()
                else:
                    self.aktif_kullanici = kullanici
                    self.bakiye = kullanici[2]
                    self.borc = kullanici[3]
                    self.kullanici_iban = kullanici[4]
                    self.bloke = kullanici[5]
                    self.menu_goster()
                    
            else:
                # Create a new Label widget to display the error message
                error_label = tk.Label(self.ana_pencere, text="Hatalı kullanıcı adı veya şifre. Tekrar deneyin")
                error_label.grid(row=5, column=1)
    def sonuc_etiketi_guncelle(self, metin):
        self.sonuc_etiketi = tk.Label(self.ana_pencere, text=metin)
        self.sonuc_etiketi.grid(row=5, column=1)

    def menu_goster(self):
            for widget in self.ana_pencere.winfo_children():
                widget.destroy()

            row_number = 0
            column_number = 0

            kullanici_bilgisi_label = Label(self.ana_pencere, text="Kullanıcı Bilgileri")
            kullanici_bilgisi_label.grid(row=row_number, column=column_number)

            # Display user information
            kullanici_bilgisi = f"Kullanıcı: {self.kullanici_adi} - IBAN: {self.aktif_kullanici[4]}"
            kullanici_bilgisi_label = Label(self.ana_pencere, text=kullanici_bilgisi)
            kullanici_bilgisi_label.grid(row=row_number + 1, column=column_number, pady=10)

            # Create a frame for buttons
            buttons_frame = tk.Frame(self.ana_pencere)
            buttons_frame.grid(row=row_number + 2, column=column_number, pady=20)

            # Buttons
            button_data = [
                ("Bakiye Sorgula", self.bakiye_sorgula),
                ("Para Çek", self.para_cek),
                ("Para Yatır", self.para_yatir),
                ("Borç Sorgula", self.borc_sorgula),
                ("Kredi Başvurusu", self.kredi_basvurusu),
                ("Kredi Geri Ödeme", self.kredi_geri_odeme),
                ("Transfer İşlemi", self.para_transferi),
                ("Çıkış", self.cikis)
            ]

            for i, (button_text, command) in enumerate(button_data):
                button = tk.Button(buttons_frame, text=button_text, command=command, width=15, height=2)
                button.grid(row=i // 3, column=i % 3, padx=20, pady=20)

            # Check if the user is bloked and display the related button
            if self.bloke == 1:
                bloke_acma_button = tk.Button(self.ana_pencere, text="Bloke Açma Talebi Gönder", command=self.bloke_acma_talebi_gonder)
                bloke_acma_button.grid(row=row_number + 3, column=column_number)

        # Rest of your code



    def bakiye_sorgula(self):
        messagebox.showinfo("Bakiye Sorgulama", f"Bakiyeniz: {self.aktif_kullanici[2]} TL")
        self.menu_goster()

    def para_cek(self):
        miktar = simpledialog.askfloat("Para Çekme", "Çekmek istediğiniz miktarı girin (TL):")
        if miktar:
            if miktar > self.aktif_kullanici[2]:
                messagebox.showerror("Hata", "Yetersiz bakiye. İşlem gerçekleştirilemedi.")
            else:
                self.aktif_kullanici = list(self.aktif_kullanici)
                self.aktif_kullanici[2] -= miktar
                self.aktif_kullanici = tuple(self.aktif_kullanici)

                self.cursor.execute("UPDATE kullanicilar SET bakiye=? WHERE kullanici_adi=?", (self.aktif_kullanici[2], self.kullanici_adi))
                self.baglanti.commit()
                self.transaction_history.append(f"{self.kullanici_adi} kullanıcısı {miktar} TL çekti")
                self.transaction_history_goster()  # İşlem geçmişini güncellemek için
                messagebox.showinfo("İşlem Başarılı", f"{miktar} TL çekildi. Yeni bakiyeniz: {self.aktif_kullanici[2]} TL")
                self.menu_goster()

    def para_yatir(self):
        miktar = simpledialog.askfloat("Para Yatırma", "Yatırmak istediğiniz miktarı girin (TL):")
        if miktar:
            self.aktif_kullanici = list(self.aktif_kullanici)
            self.aktif_kullanici[2] += miktar
            self.aktif_kullanici = tuple(self.aktif_kullanici)

            self.cursor.execute("UPDATE kullanicilar SET bakiye=? WHERE kullanici_adi=?", (self.aktif_kullanici[2], self.kullanici_adi))
            self.baglanti.commit()
            messagebox.showinfo("İşlem Başarılı", f"{miktar} TL yatırıldı. Yeni bakiyeniz: {self.aktif_kullanici[2]} TL")
            self.menu_goster()
            
    def borc_sorgula(self):
        borc = self.aktif_kullanici[3]
        if borc > 0:
            messagebox.showinfo("Borç Sorgulama", f"Toplam borcunuz: {borc} TL")
        else:
            messagebox.showinfo("Borç Sorgulama", "Borcunuz bulunmamaktadır.")
        self.menu_goster()

    def kredi_basvurusu(self):
        kullanici_adi = self.kullanici_adi  # Aktif kullanıcının adını kullanabilirsiniz
        miktar = simpledialog.askfloat("Kredi Başvurusu", "Başvurmak istediğiniz kredi miktarını girin (TL):")

        if miktar:
            # Kullanıcının kredi başvurusunu kaydedin
            self.cursor.execute("INSERT INTO kredi_basvurulari (kullanici_adi, kredi_miktari, durum) VALUES (?, ?, ?)",
                            (kullanici_adi, miktar, "Beklemede"))
            self.baglanti.commit()
            messagebox.showinfo("Kredi Başvurusu", f"{miktar} TL kredi başvurunuz alınmıştır.")
    

    def kredi_geri_odeme(self):
        if self.aktif_kullanici[5] == 0:
            messagebox.showerror("Hata", "Kredi geri ödemeniz için ödemeniz gereken bir kredi olmalıdır.")
        else:
            odeme_miktari = simpledialog.askfloat("Kredi Geri Ödeme", "Ödemek istediğiniz miktarı girin (TL):")
            if odeme_miktari:
                self.aktif_kullanici = list(self.aktif_kullanici)
                self.aktif_kullanici[5] = 0  # Kredi geri ödendi
                self.aktif_kullanici = tuple(self.aktif_kullanici)

                self.cursor.execute("UPDATE kullanicilar SET borc=?, bloke=? WHERE kullanici_adi=?", (0, 0, self.kullanici_adi))
                self.baglanti.commit()
                messagebox.showinfo("Kredi Geri Ödeme", f"{odeme_miktari} TL kredi geri ödemesi yapıldı.")
        self.menu_goster()

    def kullaniciyi_guncelle(self):
        self.cursor.execute("UPDATE kullanicilar SET bakiye=?, borc=? WHERE kullanici_adi=?", (self.bakiye, self.borc, self.kullanici_adi))
        self.baglanti.commit()
    
    
    def cikis(self):
        self.aktif_kullanici = None
        self.kullanici_adi = ""
        self.sifre = ""
        self.bakiye = 1000
        self.borc = 0
        self.kullanici_iban = ""
        self.bloke = 0
        self.giris_ekrani()
    def admin_cikis(self):
        self.admin_menu()

    def kayit_ol(self):
        yeni_kullanici_adi = simpledialog.askstring("Kayıt Ol", "Kullanıcı adınızı girin:")
        yeni_sifre = simpledialog.askstring("Kayıt Ol", "Şifrenizi girin:")

        # Rastgele 11 haneli IBAN numarası oluşturma
        yeni_iban = ''.join(random.choice(string.digits) for _ in range(11))

        self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (yeni_kullanici_adi,))
        kullanici = self.cursor.fetchone()

        if kullanici:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.")
        else:
            self.cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, bakiye, borc, iban, bloke) VALUES (?, ?, ?, ?, ?, ?)",
                                (yeni_kullanici_adi, yeni_sifre, 1000, 0, yeni_iban, 0))
            self.baglanti.commit()
            messagebox.showinfo("Kayıt Başarılı", "Yeni kullanıcı kaydı oluşturuldu.")
            self.giris_ekrani()

    def admin_menu(self):
        self.temizle_ekran()

        # Create a frame for the buttons grid
        buttons_frame = tk.Frame(self.ana_pencere)
        buttons_frame.grid(row=1, column=1)

        # Define button labels and corresponding functions
        button_data = [
            ("Kullanıcıları Listele", self.kullanicilari_listele),
            ("Kullanıcı Para Yatır", self.kullanicilara_para_yatir),
            ("Kullanıcı Para Çek", self.kullanicilara_para_cek),
            ("Kullanıcı Para Sıfırlama", self.kullanicilara_para_sifirlama),
            ("Kullanıcı Borç Ekleme", self.kullanicilara_borc_ekleme),
            ("Kullanıcı Borç Silme", self.kullanicilarin_borc_silme),
            ("Kullanıcı Borç Sıfırlama", self.kullanicilarin_borc_sifirlama),
            ("Kullanıcı Bloke Etme", self.kullanicilari_bloke_etme),
            ("Kullanıcı Bloke Kaldır", self.kullanicilarin_bloke_kaldirma),
            ("Kullanıcı Bloke İnceleme", self.bloke_acma_taleplerini_incele),
            ("Kullanıcı Kredi Başvuruları", self.kredi_basvurularini_incele),
            ("Kullanıcılar İşlem Geçmişi", self.transaction_history_goster),

        ]

        row_number = 0
        column_number = 0
        button_width = 15
        button_height = 2

        for button_text, command in button_data:
            button = tk.Button(buttons_frame, text=button_text, command=command, width=button_width, height=button_height)
            button.grid(row=row_number, column=column_number, padx=20, pady=20)
            column_number += 1
            if column_number == 3:
                column_number = 0
                row_number += 1

        # Add an exit button
        exit_button = tk.Button(buttons_frame, text="Çıkış", command=self.cikis, width=button_width, height=button_height)
        exit_button.grid(row=row_number, column=column_number, padx=20, pady=20)

    
    def kullanicilari_listele(self):
        self.temizle_ekran()
        self.cursor.execute("SELECT * FROM kullanicilar")
        kullanicilar = self.cursor.fetchall()

        # Kullanıcıları listelemek için bir metin oluşturun
        liste_metni = "Kullanıcı Adı\tBakiye\tBorç\tIBAN\tBloke Durumu\n"
        for kullanici in kullanicilar:
            liste_metni += f"{kullanici[0]}\t{kullanici[2]}\t{kullanici[3]}\t{kullanici[4]}\t{kullanici[5]}\n"

        # Metni gösterin
        liste_label = tk.Label(self.ana_pencere, text=liste_metni)
        liste_label.grid(row=1, column=1)

        # Admin menüsüne dönme düğmesi ekleyin
        admin_menu_button = tk.Button(self.ana_pencere, text="Admin Menüsüne Dön", command=self.admin_menu)
        admin_menu_button.grid(row=2, column=1)

        # Ek sütunlar için sütun numarasını tanımlayın
        column_number = 2  # Örnek olarak 2. sütuna yerleştirdik

        # İkinci sütunda bir düğme eklemek için
        admin_listele_button = tk.Button(self.ana_pencere, text="Kullanıcıları Listeleyin", command=self.kullanicilari_listele)
        admin_listele_button.grid(row=1, column=column_number)
        
        # İkinci sütunda bir etiket eklemek için
        additional_label = tk.Label(self.ana_pencere, text="Ek Sütun")
        additional_label.grid(row=3, column=column_number)


    def kredi_basvurularini_incele(self):
        # Kredi başvurularını veritabanından alın
        self.cursor.execute("SELECT * FROM kredi_basvurulari")
        basvurular = self.cursor.fetchall()

        if not basvurular:
            messagebox.showinfo("Kredi Başvuruları", "Henüz kredi başvurusu yapılmış veri bulunmuyor.")
            return

        # Yeni bir pencere oluşturun
        inceleme_penceresi = tk.Toplevel()
        inceleme_penceresi.title("Kredi Başvurularını İncele")

        def onayla_basvuru(basvuru_id, kullanici_id, kredi_miktari):
            
            yeni_kredi_bakiye = self.bakiye + int(kredi_miktari)
            self.cursor.execute("UPDATE kullanicilar SET kredi_bakiye = ? WHERE kullanici_adi = ?", (yeni_kredi_bakiye, kullanici_adi))
            self.cursor.execute("UPDATE kredi_basvurulari SET durum = ? WHERE kredi_basvuru_id = ?", ("Onaylandı", basvuru_id))
            self.cursor.execute("DELETE FROM kredi_basvurulari WHERE kredi_basvuru_id = ?", (basvuru_id,))

            self.baglanti.commit()
            self.admin_menu()

        def reddet_basvuru(basvuru_id):
            self.cursor.execute("UPDATE kredi_basvurulari SET durum = ? WHERE kredi_basvuru_id = ?", ("Reddedildi", basvuru_id))
            self.baglanti.commit()
            self.admin_menu()

        for basvuru in basvurular:
            basvuru_id, kullanici_adi, kredi_miktari, durum = basvuru
            basvuru_metni = f"Kullanıcı Adı: {kullanici_adi}\nKredi Miktarı: {kredi_miktari}\nDurumu: {durum}\n"

            # Her başvuru için ayrı bir çerçeve oluşturun
            basvuru_cercevesi = tk.Frame(inceleme_penceresi)
            basvuru_cercevesi.pack()

            basvuru_metin_etiketi = tk.Label(basvuru_cercevesi, text=basvuru_metni)
            basvuru_metin_etiketi.pack()

            onayla_dugmesi = tk.Button(basvuru_cercevesi, text="Onayla", command=lambda id=basvuru_id, kullanici_adi=kullanici_adi, kredi_miktari=kredi_miktari: onayla_basvuru(id, kullanici_adi, kredi_miktari))
            onayla_dugmesi.pack()

            reddet_dugmesi = tk.Button(basvuru_cercevesi, text="Reddet", command=lambda id=basvuru_id: reddet_basvuru(id))
            reddet_dugmesi.pack()

    def transaction_history_goster(self):
        self.temizle_ekran()
        self.ana_pencere.geometry("768x600")  # Geçmişin sığması için pencere yüksekliğini artırın

        history_label = Label(self.ana_pencere, text="İşlem Geçmişi", font=("Helvetica", 16))
        history_label.grid(row=0, column=1, pady=10)

        # İşlem geçmişini bir metin kutusunda görüntüle
        history_text = tk.Text(self.ana_pencere, height=15, width=50)
        history_text.grid(row=1, column=1, padx=20)

        for transaction in self.transaction_history:
            history_text.insert(tk.END, f"{transaction}\n")

        back_button = tk.Button(self.ana_pencere, text="Geri Dön", command=self.admin_menu)
        back_button.grid(row=2, column=1, pady=10)

    def kredi_basvurusunu_onayla(self):
        kullanici_adi = simpledialog.askstring("Kredi Başvurusunu Onayla", "Kredi başvurusunu yapmış kullanıcının adını girin:")
        
        if kullanici_adi:
            # Kredi başvurusu için "durum" güncelleme sorgusu
            guncelleme_sorgusu = """
            UPDATE kredi_basvurulari
            SET durum = ?
            WHERE kullanici_adi = ?;
            """
            
            # Kredi başvurusunu onayla (durumu güncelle)
            self.cursor.execute(guncelleme_sorgusu, ("Onaylandı", kullanici_adi))
            self.connection.commit()
            messagebox.showinfo("Kredi Başvuruları", f"{kullanici_adi} adlı kullanıcının kredi başvurusu onaylandı.")
        


    def kullanicilara_para_yatir(self):
        kullanici_adi = simpledialog.askstring("Para Yatırma", "Para yatırmak istediğiniz kullanıcının adını girin:")
        if kullanici_adi:
            miktar = simpledialog.askfloat("Para Yatırma", f"{kullanici_adi} kullanıcısına ne kadar para yatırmak istiyorsunuz?")
            if miktar:
                self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,))
                kullanici = self.cursor.fetchone()
                if kullanici:
                    kullanici_bakiye = kullanici[2]
                    kullanici_bakiye += miktar
                    self.cursor.execute("UPDATE kullanicilar SET bakiye=? WHERE kullanici_adi=?", (kullanici_bakiye, kullanici_adi))
                
                    self.baglanti.commit()
                    self.transaction_history.append(f"{self.kullanici_adi} kullanıcısı {miktar} TL yatırdı")
                    self.transaction_history_goster()
                    messagebox.showinfo("Para Yatırma", f"{kullanici_adi} kullanıcısına {miktar} TL para yatırıldı. Yeni bakiyesi: {kullanici_bakiye} TL")
                else:
                    messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
                self.admin_menu()

    def kullanicilara_para_cek(self):
        kullanici_adi = simpledialog.askstring("Para Çekme", "Para çekmek istediğiniz kullanıcının adını girin:")
        if kullanici_adi:
            miktar = simpledialog.askfloat("Para Çekme", f"{kullanici_adi} kullanıcısından ne kadar para çekmek istiyorsunuz?")
            if miktar:
                self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,))
                kullanici = self.cursor.fetchone()
                if kullanici:
                    kullanici_bakiye = kullanici[2]
                    if miktar > kullanici_bakiye:
                        messagebox.showerror("Hata", "Kullanıcının bakiyesi yetersiz.")
                    else:
                        kullanici_bakiye -= miktar
                        self.cursor.execute("UPDATE kullanicilar SET bakiye=? WHERE kullanici_adi=?", (kullanici_bakiye, kullanici_adi))
                        self.baglanti.commit()
                        self.transaction_history_goster.append(f"{self.kullanici_adi} kullanıcısından {miktar} TL El Konuldu .")
                        self.transaction_history_goster()
                        messagebox.showinfo("Para Çekme", f"{kullanici_adi} kullanıcısından {miktar} TL para çekildi. Yeni bakiyesi: {kullanici_bakiye} TL")
                else:
                    messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
                self.admin_menu()

    def kullanicilara_para_sifirlama(self):
        kullanici_adi = simpledialog.askstring("Para Sıfırlama", "Kullanıcının adını girin:")
        if kullanici_adi:
            self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,))
            kullanici = self.cursor.fetchone()
            if kullanici:
                self.cursor.execute("UPDATE kullanicilar SET bakiye=? WHERE kullanici_adi=?", (0, kullanici_adi))
                self.baglanti.commit()
                messagebox.showinfo("Para Sıfırlama", f"{kullanici_adi} kullanıcısının bakiyesi sıfırlandı.")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
            self.admin_menu()

    def kullanicilara_borc_ekleme(self):
        kullanici_adi = simpledialog.askstring("Borç Ekleme", "Borç eklemek istediğiniz kullanıcının adını girin:")
        if kullanici_adi:
            miktar = simpledialog.askfloat("Borç Ekleme", f"{kullanici_adi} kullanıcısına ne kadar borç eklemek istiyorsunuz?")
            if miktar:
                self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,))
                kullanici = self.cursor.fetchone()
                if kullanici:
                    kullanici_borc = kullanici[3]
                    kullanici_borc += miktar
                    self.cursor.execute("UPDATE kullanicilar SET borc=? WHERE kullanici_adi=?", (kullanici_borc, kullanici_adi))
                    self.baglanti.commit()
                    messagebox.showinfo("Borç Ekleme", f"{kullanici_adi} kullanıcısına {miktar} TL borç eklendi. Toplam borcu: {kullanici_borc} TL")
                else:
                    messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
                self.admin_menu()

    def kullanicilarin_borc_silme(self):
        kullanici_adi = simpledialog.askstring("Borç Silme", "Borcu silmek istediğiniz kullanıcının adını girin:")
        if kullanici_adi:
            self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,))
            kullanici = self.cursor.fetchone()
            if kullanici:
                kullanici_borc = kullanici[3]
                if kullanici_borc == 0:
                    messagebox.showinfo("Borç Silme", f"{kullanici_adi} kullanıcısının borcu zaten sıfır.")
                else:
                    self.cursor.execute("UPDATE kullanicilar SET borc=? WHERE kullanici_adi=?", (0, kullanici_adi))
                    self.baglanti.commit()
                    messagebox.showinfo("Borç Silme", f"{kullanici_adi} kullanıcısının borcu silindi.")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
            self.admin_menu()


    def kullanicilarin_borc_sifirlama(self):
        self.cursor.execute("UPDATE kullanicilar SET borc=0")
        self.baglanti.commit()
        messagebox.showinfo("Borç Sıfırlama", "Tüm kullanıcıların borçları sıfırlandı.")
        self.admin_menu()

    def kullanicilari_bloke_etme(self):
        kullanici_adi = simpledialog.askstring("Kullanıcı Bloke Etme", "Bloke etmek istediğiniz kullanıcının adını girin:")
        if kullanici_adi:
            self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,))
            kullanici = self.cursor.fetchone()
            if kullanici:
                self.cursor.execute("UPDATE kullanicilar SET bloke=1 WHERE kullanici_adi=?", (kullanici_adi,))
                self.baglanti.commit()
                messagebox.showinfo("Kullanıcı Bloke Etme", f"{kullanici_adi} kullanıcısı bloke edildi.")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
            self.admin_menu()

    
   

    

   

    def kullanicilarin_bloke_kaldirma(self):
        kullanici_adi = simpledialog.askstring("Kullanıcı Bloke Kaldırma", "Bloke kaldırmak istediğiniz kullanıcının adını girin:")
        if kullanici_adi:
            self.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,))
            kullanici = self.cursor.fetchone()
            if kullanici:
                self.cursor.execute("UPDATE kullanicilar SET bloke=0 WHERE kullanici_adi=?", (kullanici_adi,))
                self.baglanti.commit()
                messagebox.showinfo("Kullanıcı Bloke Kaldırma", f"{kullanici_adi} kullanıcısının blokesi kaldırıldı.")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
            self.admin_menu()

if __name__ == "__main__":
    ana_pencere = tk.Tk()
    uygulama = ATM(ana_pencere)
    ana_pencere.mainloop()
