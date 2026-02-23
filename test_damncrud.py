from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os

# =============================================
# KONFIGURASI
# =============================================
BASE_URL = "http://localhost/DamnCRUD-main/DamnCRUD-main"
USERNAME = "admin"
PASSWORD = "nimda666!"

# Menonaktifkan pesan log DevTools dan error
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--log-level=3")
options.add_argument("--disable-gpu")

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.FATAL)

# Inisialisasi WebDriver
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)

# =============================================
# HELPER FUNCTION
# =============================================
def login():
    """Helper: login sebagai admin sebelum test yang membutuhkan autentikasi"""
    driver.get(f"{BASE_URL}/login.php")
    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD + Keys.RETURN)
    time.sleep(2)


# =============================================
# TC-03 | SQL Injection pada Login
# OBJECTIVE  : Menguji apakah sistem rentan terhadap SQL Injection
# EXPECTED   : Sistem menolak login, tidak memberikan akses
# STATUS     : FAIL (login.php menggunakan string concatenation)
# =============================================
def test_sql_injection_login():
    """
    Langkah-langkah:
    1. Buka halaman login
    2. Masukkan payload SQL Injection pada field username
    3. Masukkan password sembarang
    4. Klik tombol login
    5. Verifikasi bahwa sistem TIDAK memberikan akses ke index.php
    """
    print("\n" + "="*60)
    print("TC-03 | SQL Injection pada Login")
    print("="*60)

    driver.get(f"{BASE_URL}/login.php")
    time.sleep(1)

    # Step 1: Masukkan payload SQL Injection
    sql_payload = "' OR '1'='1"
    driver.find_element(By.NAME, "username").send_keys(sql_payload)
    driver.find_element(By.NAME, "password").send_keys("apapun" + Keys.RETURN)
    time.sleep(2)

    print(f"  [INPUT]  Username: {sql_payload}")
    print(f"  [INPUT]  Password: apapun")
    print(f"  [URL]    Current URL: {driver.current_url}")

    # Verifikasi: jika masuk ke index.php berarti sistem RENTAN (FAIL)
    if "index.php" in driver.current_url:
        print("  [RESULT] ❌ FAIL — Sistem RENTAN terhadap SQL Injection!")
        print("           Login berhasil padahal seharusnya ditolak.")
        print("  [BUG]    login.php menggunakan string concatenation:")
        print("           WHERE username = '\" . $user . \"'")
    else:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"  [RESULT] ✅ PASS — Login ditolak. Pesan: {body_text[:80]}")


# =============================================
# TC-09 | Tambah Data Kontak Baru (Create)
# OBJECTIVE  : Menguji fitur tambah kontak baru
# EXPECTED   : Data tersimpan dan muncul di index.php
# STATUS     : FAIL (variabel $id tidak didefinisikan di create.php)
# =============================================
def test_create_contact():
    """
    Langkah-langkah:
    1. Login terlebih dahulu
    2. Navigasi ke create.php
    3. Isi semua field (name, email, phone, title)
    4. Klik tombol Save
    5. Verifikasi data muncul di index.php
    """
    print("\n" + "="*60)
    print("TC-09 | Tambah Data Kontak Baru")
    print("="*60)

    login()
    driver.get(f"{BASE_URL}/create.php")
    time.sleep(1)

    # Step 1: Isi form tambah kontak
    name_val    = "Test Contact UAS"
    email_val   = "testuas@example.com"
    phone_val   = "08123456789"
    title_val   = "QA Engineer"

    driver.find_element(By.NAME, "name").send_keys(name_val)
    driver.find_element(By.NAME, "email").send_keys(email_val)
    driver.find_element(By.NAME, "phone").send_keys(phone_val)
    driver.find_element(By.NAME, "title").send_keys(title_val)

    print(f"  [INPUT]  Name : {name_val}")
    print(f"  [INPUT]  Email: {email_val}")
    print(f"  [INPUT]  Phone: {phone_val}")
    print(f"  [INPUT]  Title: {title_val}")

    # Step 2: Submit form
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    time.sleep(2)

    print(f"  [URL]    Current URL: {driver.current_url}")

    # Step 3: Verifikasi apakah kontak muncul di index.php
    driver.get(f"{BASE_URL}/index.php")
    time.sleep(1)
    page_content = driver.page_source

    if name_val in page_content:
        print(f"  [RESULT] ✅ PASS — Kontak '{name_val}' berhasil ditambahkan.")
    else:
        print(f"  [RESULT] ❌ FAIL — Kontak tidak muncul di daftar!")
        print("  [BUG]    Variabel $id tidak didefinisikan di create.php")
        print("           INSERT INTO contacts VALUES (?, ?, ?, ?, ?, ?)")
        print("           $id tidak pernah diset sehingga query error.")


# =============================================
# TC-11 | Edit Data Kontak
# OBJECTIVE  : Menguji fitur edit/update kontak yang sudah ada
# EXPECTED   : Data berhasil diperbarui di database
# STATUS     : PASS
# =============================================
def test_edit_contact():
    """
    Langkah-langkah:
    1. Login terlebih dahulu
    2. Buka index.php dan klik tombol 'edit' pada kontak pertama
    3. Ubah nama dan email kontak
    4. Submit form update
    5. Verifikasi data baru muncul di index.php
    """
    print("\n" + "="*60)
    print("TC-11 | Edit Data Kontak")
    print("="*60)

    login()
    driver.get(f"{BASE_URL}/index.php")
    time.sleep(1)

    # Step 1: Klik tombol edit pada kontak pertama
    edit_button = driver.find_element(By.LINK_TEXT, "edit")
    edit_button.click()
    time.sleep(2)

    print(f"  [URL]    Edit URL: {driver.current_url}")

    # Step 2: Ubah data kontak
    new_name  = "Jane Doe Updated"
    new_email = "janeupdated@example.com"

    name_input = driver.find_element(By.NAME, "name")
    name_input.clear()
    name_input.send_keys(new_name)

    email_input = driver.find_element(By.NAME, "email")
    email_input.clear()
    email_input.send_keys(new_email)

    print(f"  [INPUT]  New Name : {new_name}")
    print(f"  [INPUT]  New Email: {new_email}")

    # Step 3: Submit update
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    time.sleep(2)

    # Step 4: Verifikasi data baru di index.php
    driver.get(f"{BASE_URL}/index.php")
    time.sleep(1)
    page_content = driver.page_source

    if new_name in page_content:
        print(f"  [RESULT] ✅ PASS — Data kontak berhasil diperbarui menjadi '{new_name}'")
    else:
        print(f"  [RESULT] ❌ FAIL — Data kontak tidak berhasil diperbarui")


# =============================================
# TC-12 | Edit Kontak — Field Phone Tidak Termuat
# OBJECTIVE  : Verifikasi bug field phone kosong di form update
# EXPECTED   : Field phone seharusnya terisi data lama
# STATUS     : FAIL (value="" di update.php)
# =============================================
def test_edit_phone_bug():
    """
    Langkah-langkah:
    1. Login terlebih dahulu
    2. Buka update.php dengan ID kontak yang ada (id=1)
    3. Periksa apakah field phone terisi dengan data yang ada
    4. Jika kosong, catat sebagai FAIL (bug ditemukan)
    """
    print("\n" + "="*60)
    print("TC-12 | Bug Field Phone Kosong di Form Edit")
    print("="*60)

    login()
    driver.get(f"{BASE_URL}/update.php?id=1")
    time.sleep(2)

    print(f"  [URL]    {driver.current_url}")

    # Step: Ambil value field phone
    phone_field = driver.find_element(By.NAME, "phone")
    phone_value = phone_field.get_attribute("value")

    print(f"  [CHECK]  Nilai field phone yang ditampilkan: '{phone_value}'")

    if phone_value == "" or phone_value is None:
        print("  [RESULT] ❌ FAIL — Field phone kosong di form edit!")
        print("  [BUG]    update.php baris phone: value=\"\" (hardcoded kosong)")
        print("           Seharusnya: value=\"<?= $contact['phone'] ?>\"")
    else:
        print(f"  [RESULT] ✅ PASS — Field phone terisi: '{phone_value}'")


# =============================================
# TC-13 | Hapus Data Kontak
# OBJECTIVE  : Menguji fitur hapus kontak
# EXPECTED   : Data terhapus dari database dan tidak muncul di index.php
# STATUS     : PASS
# =============================================
def test_delete_contact():
    """
    Langkah-langkah:
    1. Login terlebih dahulu
    2. Catat nama kontak yang akan dihapus (kontak terakhir dalam daftar)
    3. Akses delete.php dengan ID kontak tersebut
    4. Verifikasi kontak tidak lagi muncul di index.php
    """
    print("\n" + "="*60)
    print("TC-13 | Hapus Data Kontak")
    print("="*60)

    login()
    driver.get(f"{BASE_URL}/index.php")
    time.sleep(1)

    # Step 1: Ambil nama kontak terakhir untuk verifikasi
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    if not rows:
        print("  [SKIP]   Tidak ada kontak di daftar")
        return

    last_row    = rows[-1]
    contact_name = last_row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
    delete_link  = last_row.find_element(By.LINK_TEXT, "delete")
    delete_href  = delete_link.get_attribute("href")

    print(f"  [INFO]   Kontak yang akan dihapus: '{contact_name}'")
    print(f"  [INFO]   Delete URL: {delete_href}")

    # Step 2: Langsung akses URL delete (bypass confirm dialog)
    driver.get(delete_href)
    time.sleep(2)

    # Step 3: Verifikasi kontak tidak muncul lagi
    driver.get(f"{BASE_URL}/index.php")
    time.sleep(1)
    page_content = driver.page_source

    if contact_name not in page_content:
        print(f"  [RESULT] ✅ PASS — Kontak '{contact_name}' berhasil dihapus")
    else:
        print(f"  [RESULT] ❌ FAIL — Kontak '{contact_name}' masih muncul di daftar")


# =============================================
# TC-14 | Akses delete.php Tanpa Parameter ID
# OBJECTIVE  : Verifikasi pesan error saat delete tanpa ID
# EXPECTED   : Sistem menampilkan "No ID specified!"
# STATUS     : PASS
# =============================================
def test_delete_no_id():
    """
    Langkah-langkah:
    1. Login terlebih dahulu
    2. Akses delete.php tanpa parameter ?id=
    3. Verifikasi pesan error "No ID specified!" muncul
    """
    print("\n" + "="*60)
    print("TC-14 | Akses delete.php Tanpa Parameter ID")
    print("="*60)

    login()
    driver.get(f"{BASE_URL}/delete.php")
    time.sleep(1)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    print(f"  [URL]    {driver.current_url}")
    print(f"  [OUTPUT] Pesan yang ditampilkan: '{body_text}'")

    if "No ID specified!" in body_text:
        print("  [RESULT] ✅ PASS — Sistem menampilkan pesan error yang benar")
    else:
        print("  [RESULT] ❌ FAIL — Pesan error tidak sesuai harapan")


# =============================================
# TC-20 | Akses update.php Tanpa Login
# OBJECTIVE  : Verifikasi proteksi halaman update tanpa autentikasi
# EXPECTED   : Pengguna dialihkan ke login.php
# STATUS     : FAIL (update.php tidak ada cek sesi)
# =============================================
def test_update_without_login():
    """
    Langkah-langkah:
    1. Pastikan tidak ada sesi aktif (hapus cookies)
    2. Akses langsung update.php?id=1 tanpa login
    3. Verifikasi apakah diarahkan ke login.php atau bisa diakses
    """
    print("\n" + "="*60)
    print("TC-20 | Akses update.php Tanpa Login")
    print("="*60)

    # Step 1: Hapus semua cookies untuk memastikan tidak ada sesi
    driver.delete_all_cookies()
    time.sleep(1)

    # Step 2: Akses update.php langsung tanpa login
    driver.get(f"{BASE_URL}/update.php?id=1")
    time.sleep(2)

    print(f"  [URL]    Current URL: {driver.current_url}")

    # Step 3: Verifikasi redirect ke login.php atau tidak
    if "login.php" in driver.current_url:
        print("  [RESULT] ✅ PASS — Pengguna diarahkan ke login.php")
    else:
        page_title = driver.title
        print(f"  [RESULT] ❌ FAIL — Halaman dapat diakses tanpa login! Title: '{page_title}'")
        print("  [BUG]    update.php tidak memiliki pengecekan $_SESSION['user']")
        print("           Semua halaman protected seharusnya memiliki:")
        print("           if (!isset($_SESSION['user'])) { header('location: login.php'); }")


# =============================================
# MAIN — Jalankan Semua Test
# =============================================
if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# DAMNCRUD - AUTOMATION TEST")
    print("# 8 Test Cases (termasuk 2 FAIL)")
    print("#"*60)

    results = {}

    test_cases = [
        ("TC-03 SQL Injection Login",           test_sql_injection_login),
        ("TC-09 Tambah Kontak",                 test_create_contact),
        ("TC-11 Edit Kontak",                   test_edit_contact),
        ("TC-12 Bug Phone di Form Edit",        test_edit_phone_bug),
        ("TC-13 Hapus Kontak",                  test_delete_contact),
        ("TC-14 Delete Tanpa ID",               test_delete_no_id),
        ("TC-20 Update Tanpa Login",            test_update_without_login),
    ]

    for name, func in test_cases:
        try:
            func()
        except Exception as e:
            print(f"  [ERROR]  Exception pada {name}: {e}")

    print("\n" + "#"*60)
    print("# SEMUA TEST SELESAI DIJALANKAN")
    print("#"*60)

    driver.quit()