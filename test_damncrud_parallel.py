import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


# =============================================
# TC-03 | SQL Injection pada Login
# =============================================
def test_sql_injection_login(driver, base_url):
    """Test SQL Injection vulnerability pada login"""
    print("\n" + "="*60)
    print("TC-03 | SQL Injection pada Login")
    print("="*60)

    driver.get(f"{base_url}/login.php")
    time.sleep(1)

    sql_payload = "' OR '1'='1"
    driver.find_element(By.NAME, "username").send_keys(sql_payload)
    driver.find_element(By.NAME, "password").send_keys("apapun" + Keys.RETURN)
    time.sleep(2)

    print(f"  [INPUT]  Username: {sql_payload}")
    print(f"  [INPUT]  Password: apapun")
    print(f"  [URL]    Current URL: {driver.current_url}")

    if "index.php" in driver.current_url:
        print("  [RESULT] ❌ FAIL — Sistem RENTAN terhadap SQL Injection!")
    else:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"  [RESULT] ✅ PASS — Login ditolak. Pesan: {body_text[:80]}")


# =============================================
# TC-09 | Tambah Data Kontak Baru (Create)
# =============================================
def test_create_contact(logged_in_driver, base_url):
    """Test tambah kontak baru"""
    print("\n" + "="*60)
    print("TC-09 | Tambah Data Kontak Baru")
    print("="*60)

    driver = logged_in_driver
    driver.get(f"{base_url}/create.php")
    time.sleep(1)

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

    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    time.sleep(2)

    print(f"  [URL]    Current URL: {driver.current_url}")

    driver.get(f"{base_url}/index.php")
    time.sleep(1)
    page_content = driver.page_source

    if name_val in page_content:
        print(f"  [RESULT] ✅ PASS — Kontak '{name_val}' berhasil ditambahkan.")
    else:
        print(f"  [RESULT] ❌ FAIL — Kontak tidak muncul di daftar!")


# =============================================
# TC-11 | Edit Data Kontak
# =============================================
def test_edit_contact(logged_in_driver, base_url):
    """Test edit kontak"""
    print("\n" + "="*60)
    print("TC-11 | Edit Data Kontak")
    print("="*60)

    driver = logged_in_driver
    driver.get(f"{base_url}/index.php")
    time.sleep(1)

    try:
        edit_button = driver.find_element(By.LINK_TEXT, "edit")
        edit_button.click()
        time.sleep(2)

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

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(2)

        driver.get(f"{base_url}/index.php")
        time.sleep(1)
        page_content = driver.page_source

        if new_name in page_content:
            print(f"  [RESULT] ✅ PASS — Data kontak berhasil diperbarui menjadi '{new_name}'")
        else:
            print(f"  [RESULT] ❌ FAIL — Data kontak tidak berhasil diperbarui")
    except Exception as e:
        print(f"  [SKIP]   Tidak ada kontak untuk di-edit: {e}")


# =============================================
# TC-12 | Edit Kontak — Field Phone Tidak Termuat
# =============================================
def test_edit_phone_bug(logged_in_driver, base_url):
    """Test bug field phone kosong di form edit"""
    print("\n" + "="*60)
    print("TC-12 | Bug Field Phone Kosong di Form Edit")
    print("="*60)

    driver = logged_in_driver
    driver.get(f"{base_url}/update.php?id=1")
    time.sleep(2)

    print(f"  [URL]    {driver.current_url}")

    phone_field = driver.find_element(By.NAME, "phone")
    phone_value = phone_field.get_attribute("value")

    print(f"  [CHECK]  Nilai field phone yang ditampilkan: '{phone_value}'")

    if phone_value == "" or phone_value is None:
        print("  [RESULT] ❌ FAIL — Field phone kosong di form edit!")
    else:
        print(f"  [RESULT] ✅ PASS — Field phone terisi: '{phone_value}'")


# =============================================
# TC-13 | Hapus Data Kontak
# =============================================
def test_delete_contact(logged_in_driver, base_url):
    """Test hapus kontak"""
    print("\n" + "="*60)
    print("TC-13 | Hapus Data Kontak")
    print("="*60)

    driver = logged_in_driver
    driver.get(f"{base_url}/index.php")
    time.sleep(1)

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

    driver.get(delete_href)
    time.sleep(2)

    driver.get(f"{base_url}/index.php")
    time.sleep(1)
    page_content = driver.page_source

    if contact_name not in page_content:
        print(f"  [RESULT] ✅ PASS — Kontak '{contact_name}' berhasil dihapus")
    else:
        print(f"  [RESULT] ❌ FAIL — Kontak '{contact_name}' masih muncul di daftar")


# =============================================
# TC-14 | Akses delete.php Tanpa Parameter ID
# =============================================
def test_delete_no_id(logged_in_driver, base_url):
    """Test delete tanpa parameter ID"""
    print("\n" + "="*60)
    print("TC-14 | Akses delete.php Tanpa Parameter ID")
    print("="*60)

    driver = logged_in_driver
    driver.get(f"{base_url}/delete.php")
    time.sleep(1)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    print(f"  [URL]    {driver.current_url}")
    print(f"  [OUTPUT] Pesan yang ditampilkan: '{body_text}'")

    if "No ID specified!" in body_text:
        print("  [RESULT] ✅ PASS — Sistem menampilkan pesan error yang benar")
    else:
        print("  [RESULT] ❌ FAIL — Pesan error tidak sesuai harapan")


# =============================================
# TC-18 | XSS pada VPage
# =============================================
def test_xss_vpage(logged_in_driver, base_url):
    """Test XSS vulnerability pada vpage"""
    print("\n" + "="*60)
    print("TC-18 | XSS Reflected pada VPage")
    print("="*60)

    driver = logged_in_driver
    driver.get(f"{base_url}/vpage.php")
    time.sleep(1)

    xss_payload = "<script>alert('XSS')</script>"
    driver.find_element(By.NAME, "thing").send_keys(xss_payload)
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)

    print(f"  [INPUT]  Payload: {xss_payload}")
    print(f"  [URL]    {driver.current_url}")

    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        print(f"  [RESULT] ❌ FAIL — XSS BERHASIL! Alert muncul: '{alert_text}'")
    except Exception:
        page_source = driver.page_source
        if xss_payload in page_source or "alert" in page_source:
            print("  [RESULT] ❌ FAIL — Payload XSS ditemukan di page source (tidak di-escape)")
        else:
            print("  [RESULT] ✅ PASS — Input berhasil di-sanitasi, XSS tidak terjadi")


# =============================================
# TC-20 | Akses update.php Tanpa Login
# =============================================
def test_update_without_login(driver, base_url):
    """Test akses update tanpa login"""
    print("\n" + "="*60)
    print("TC-20 | Akses update.php Tanpa Login")
    print("="*60)

    driver.delete_all_cookies()
    time.sleep(1)

    driver.get(f"{base_url}/update.php?id=1")
    time.sleep(2)

    print(f"  [URL]    Current URL: {driver.current_url}")

    if "login.php" in driver.current_url:
        print("  [RESULT] ✅ PASS — Pengguna diarahkan ke login.php")
    else:
        page_title = driver.title
        print(f"  [RESULT] ❌ FAIL — Halaman dapat diakses tanpa login! Title: '{page_title}'")