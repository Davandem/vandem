import pandas as pd
import os
import time
from datetime import datetime


FILE_USER = 'users.csv'
FILE_PRODUK= 'produk.csv'
FILE_ORDER = 'order.csv'


KOLOM_USER = ['id_user', 'username', 'password', 'role', 'alamat']
KOLOM_PRODUK = ['id_produk', 'id_penjual', 'nama_produk', 'deskripsi', 'harga', 'stok']
KOLOM_ORDER = ['id_order', 'id_pembeli', 'id_produk', 'id_penjual', 'kuantitas', 'harga_pembelian', 'waktu_transaksi']


PENGGUNA_SAAT_INI = None

def clear_screen():
    '''fungsi hapus terminal'''
    os.system('cls' if os.name == 'nt' else 'clear')


def read_csv(filename):
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"File tidak ditemukan")
        return pd.DataFrame()

def read_csv_string(filepath):
    try:
        df = pd.read_csv(filepath, dtype=str)
        return df
    except FileNotFoundError:
        print(f"File tidak ditemukan")
        return pd.DataFrame()
    
def write_csv(df_data, filename):
    try:
        df_data.to_csv(filename, mode='w', header=True, index=False)
        return True
    except Exception as e:
        print(f"Eror saat menulis ke {filename}: {e}")
        return False

 
def append_csv(df_data, filename):
    try:
        df_data.to_csv(filename, mode='a', header=False, index=False)
        return True
    except Exception as e:
        print(f"Eror saat menambah ke {filename}: {e}")
        return False

def inisiai_file():
    '''fungsi inisiasi'''
    dic_file = {
        FILE_USER: KOLOM_USER,
        FILE_PRODUK: KOLOM_PRODUK,
        FILE_ORDER: KOLOM_ORDER
    }
    for filename, kolom in dic_file.items():
        if not os.path.exists(filename):
            df_header = pd.DataFrame(columns=kolom)
            write_csv(df_header, filename)

def id_baru(filename, nama_kolom):
    '''fungsi pengecekan ID'''
    
    inisiai_file()
    try:
        df = read_csv(filename)
        if df.empty:
            return 1
        df[nama_kolom] = pd.to_numeric(df[nama_kolom], errors='coerce')
        
        df_valid_id = df.dropna(subset=[nama_kolom])
        
        
        if df_valid_id.empty:
            
            return 1
        max_id = df_valid_id[nama_kolom].max()
        return int(max_id) + 1
            
    except Exception as e:
        print(f"Error saat mencari ID untuk {filename}: {e}")
        return 1


def menu_login(role):
    '''fungsi menu login'''
    global PENGGUNA_SAAT_INI
    while PENGGUNA_SAAT_INI is None:
        clear_screen()
        print(f"--- SELAMAT DATANG {role.upper()} ---")
        print("1. Login")
        print("2. Daftar (Register)")
        print("3. Kembali ke Menu Utama")
        pilihan = input("Pilihan: ")

        if pilihan == '1':
            login(role)
        elif pilihan == '2':
            register(role)
        elif pilihan == '3':
            return
        else:
            print("Pilihan tidak valid.")
            time.sleep(1)
    if PENGGUNA_SAAT_INI['role'] == 'penjual':
        menu_penjual()
    elif PENGGUNA_SAAT_INI['role'] == 'pembeli':
        menu_pembeli()
    
def register(role):
    '''fungsi daftar akun'''
    print("\n--- DAFTAR AKUN BARU ---")
    username = str(input("Masukkan Username (Kode Unik): ")).strip()
    
    if not username:
        print("Username tidak boleh kosong")
        time.sleep(2)
        return
    
    df_users = read_csv_string(FILE_USER)
    if username in df_users['username'].values:
        print("\nUsername sudah digunakan. Silakan pilih nama lain.")
        time.sleep(2)
        return

    password = str(input("Masukkan Password: ")).strip()
    alamat = str(input("Masukkan Alamat Anda: ")).strip()
    
    
    user_baru = pd.DataFrame({
        'id_user': [id_baru(FILE_USER, 'id_user')],
        'username': [str(username)],
        'password': [str(password)],
        'role': [role],
        'alamat': [str(alamat)]
    }, columns= KOLOM_USER)

    if append_csv(user_baru, FILE_USER):
        print(f"Pendaftaran berhasil! Username '{username}' terdaftar sebagai {role} ")
        time.sleep(2)
    else:
        time.sleep(2)

def login(role):
    '''fungsi login'''
    global PENGGUNA_SAAT_INI
    print("\n------- PROSES LOGIN -------")
    username = str(input("Username: ").strip())
    password = str(input("Password: ").strip())
    df_users = read_csv_string(FILE_USER)
    if df_users.empty:
        print("Login gagal, belum ada pengguna terdaftar")
        return None
    
    filter_mask = (df_users['username'].astype(str) == username) & (df_users['password'].astype(str) == password)
    df_cocok = df_users[filter_mask]
    if len(df_cocok) == 1:
        
        PENGGUNA_SAAT_INI = df_cocok.iloc[0].to_dict()

        
        if PENGGUNA_SAAT_INI['role'] != role:
            print(f"Akses ditolak: Akun '{username}' terdaftar sebagai {PENGGUNA_SAAT_INI['role']}, bukan {role}")
            PENGGUNA_SAAT_INI= None
            time.sleep(2)
            return None
        print(f"Login Berhasil, Selamat datang, {username} ({role})")
        time.sleep(2)
        return PENGGUNA_SAAT_INI
    
    else:
        print("Login Gagal, Username atau password salah")
        time.sleep(2)
        return None


def menu_penjual():
    global PENGGUNA_SAAT_INI
    while True:
        clear_screen()
        print(f"--- MENU UTAMA PENJUAL: {PENGGUNA_SAAT_INI['username']} ---")
        print("1. Data Produk Saya")
        print("2. Tambah Barang")
        print("3. Update Barang")
        print("4. Hapus Barang")
        print("5. Riwayat Penjualan")
        print("6. Logout")
        pilihan = input("Pilihan: ")
        
        if pilihan == '1':
            lihat_produk()
        elif pilihan == '2':
            tambah_produk()
        elif pilihan == '3':
            update_produk()
        elif pilihan == '4':
            hapus_produk()
        elif pilihan == '5':
            riwayat_penjualan()
        elif pilihan == '6':
            PENGGUNA_SAAT_INI = None
            print("Anda telah logout.")
            time.sleep(1)
            break
        else:
            print("Pilihan tidak valid.")
            time.sleep(1)

def lihat_produk(jeda=True):
    clear_screen()
    df_produk = read_csv(FILE_PRODUK)
    if df_produk.empty:
        print("Tidak ada data produk yang tersimpan di sistem.")
        if jeda:
            input("\nTekan Enter untuk kembali")
        return

    print("--- DATA PRODUK SAYA ---")
    id_penjual_saat_ini = int(PENGGUNA_SAAT_INI['id_user'])
    
   
    df_produk['id_penjual'] = pd.to_numeric(df_produk['id_penjual'], errors='coerce').fillna(0).astype(int)
    mask_produk_saya = (df_produk['id_penjual'] == id_penjual_saat_ini)
    df_tampil_produk = df_produk[mask_produk_saya]
            
    
    if df_tampil_produk.empty:
        print("Anda belum memiliki produk yang terdaftar.")
    else:
        
        df_tampil_produk = df_tampil_produk.sort_values(by='id_produk')
                
        
        for i, produk in df_tampil_produk.iterrows():
            
            id_produk_val = int(produk['id_produk'])
            
            harga_val = int(produk['harga']) if not pd.isna(produk['harga']) else 0
            stok_val = int(produk['stok']) if not pd.isna(produk['stok']) else 0
                        
            
            harga_formatted = f"Rp {harga_val:,}".replace(",", ".")
                        
            print(f"\nID Produk: {id_produk_val}")
            print(f"    Nama: {produk['nama_produk']}")
            print(f"    Harga: {harga_formatted}")
            print(f"    Stok: {stok_val}")
            print(f"    Deskripsi: {produk['deskripsi']}")
                
    
    if jeda:
        input("\nTekan Enter untuk kembali...")

def tambah_produk():
    clear_screen()
    print("--- TAMBAH BARANG BARU ---")
    
    while True:
        nama_produk = input("Nama Bibit: ").strip()
        if nama_produk:
            break
        print("Nama produk tidak boleh kosong. Silakan masukkan kembali.")

    deskripsi = input("Deskripsi: ").strip() 

    
    while True:
        try:
            
            input_harga = input("Harga (contoh: 50000): ").replace('.', '').replace('Rp', '').strip()
            harga = int(input_harga)
            
            input_stok = input("Stok Awal: ").strip()
            stok = int(input_stok)
            
            
            if harga < 0 or stok < 0:
                 print("\nHarga dan Stok harus bernilai positif (≥ 0).")
                 continue 
            
            break 
            
        except ValueError:
            print("\nKesalahan Input: Harga dan Stok harus berupa angka bilangan bulat.")
            
            continue
            
    produk_baru_dict = {
        'id_produk': [id_baru(FILE_PRODUK, 'id_produk')],
        'id_penjual': [PENGGUNA_SAAT_INI['id_user']],
        'nama_produk': [nama_produk],
        'deskripsi': [deskripsi],
        'harga': [harga],
        'stok': [stok]
    }
    
    
    df_baru = pd.DataFrame(produk_baru_dict, columns=KOLOM_PRODUK)
    
    
    if append_csv(df_baru, FILE_PRODUK): 
        print(f"\nProduk '{nama_produk}' berhasil ditambahkan ke inventaris Anda.")
    else:
        print("\nProduk gagal ditambahkan karena error penulisan file.")
        
    time.sleep(2)

def update_produk():
    '''Memperbarui informasi produk menggunakan pandas DataFrame'''
    clear_screen()
    
    
    lihat_produk(jeda=False) 
    
    id_penjual_saat_ini = int(PENGGUNA_SAAT_INI['id_user'])
    
    
    print("\n--- UPDATE DATA PRODUK ---")
    id_produk_input = input("Masukkan ID Produk yang ingin di-update (atau 'batal'): ").strip()
    if id_produk_input == 'batal':
        return
    id_produk_input =int(id_produk_input)

    
    df_produk = read_csv(FILE_PRODUK) 
    
    
    df_produk['id_penjual'] = pd.to_numeric(df_produk['id_penjual'], errors='coerce').fillna(0).astype(int)
    df_produk['id_produk'] = pd.to_numeric(df_produk['id_produk'], errors='coerce').fillna(0).astype(int)
    mask_produk = (df_produk['id_produk'] == id_produk_input) & (df_produk['id_penjual'] == id_penjual_saat_ini)
    
    
    indeks_update = df_produk.index[mask_produk]

    if indeks_update.empty:
        print(f"\nProduk dengan ID {id_produk_input} tidak ditemukan atau bukan milik Anda.")
        time.sleep(2)
        return
    
    
    idx = indeks_update[0]
    produk_nama_lama = df_produk.at[idx, 'nama_produk']
    
    print(f"\nProduk yang Diupdate: '{produk_nama_lama}' (ID: {id_produk_input})")
    print(">>> Kosongkan input jika tidak ingin diubah.")
    
    nama_lama = df_produk.at[idx, 'nama_produk']
    deskripsi_lama = df_produk.at[idx, 'deskripsi']
    
    nama_baru = input(f"Nama Baru (saat ini: {nama_lama}): ").strip()
    deskripsi_baru = input(f"Deskripsi Baru (saat ini: {deskripsi_lama}): ").strip()
    
    
    if nama_baru: 
        df_produk.at[idx, 'nama_produk'] = nama_baru
    if deskripsi_baru: 
        df_produk.at[idx, 'deskripsi'] = deskripsi_baru
    
    harga_lama = df_produk.at[idx, 'harga']
    stok_lama = df_produk.at[idx, 'stok']
    
    harga_baru_input = input(f"Harga Baru (saat ini: {harga_lama}): ").strip()
    stok_baru_input = input(f"Stok Baru (saat ini: {stok_lama}): ").strip()

    
    if harga_baru_input:
        try:
            
            harga_bersih = harga_baru_input.replace('.', '').replace('Rp', '').strip()
            harga_val = int(harga_bersih)
            if harga_val < 0:
                print("Peringatan: Harga harus positif. Nilai diabaikan.")
            else:
                df_produk.at[idx, 'harga'] = harga_val
        except ValueError:
            print("Error: Input harga tidak valid (bukan angka). Nilai diabaikan.")

    
    if stok_baru_input:
        try:
            stok_val = int(stok_baru_input)
            if stok_val < 0:
                print("Peringatan: Stok harus positif. Nilai diabaikan.")
            else:
                df_produk.at[idx, 'stok'] = stok_val
        except ValueError:
            print("Error: Input stok tidak valid (bukan angka). Nilai diabaikan.")

    print("\nProduk berhasil diupdate.")
    
    
    write_csv(df_produk, FILE_PRODUK)
    time.sleep(2)

def hapus_produk():
    '''Menghapus produk menggunakan pandas DataFrame'''
    clear_screen()
    
    
    lihat_produk(jeda=False) 

    id_penjual_saat_ini = int(PENGGUNA_SAAT_INI['id_user'])

   
    print("\n--- HAPUS DATA PRODUK ---")
    id_produk_input = input("Masukkan ID Produk yang ingin dihapus (atau 'batal'): ").strip()
    if id_produk_input.lower() == 'batal':
        return
    id_produk_input = int(id_produk_input)
    
    df_produk = read_csv(FILE_PRODUK)
    
    
    df_produk['id_penjual'] = pd.to_numeric(df_produk['id_penjual'], errors='coerce').fillna(0).astype(int)
    df_produk['id_produk'] = pd.to_numeric(df_produk['id_produk'], errors='coerce').fillna(0).astype(int)
    mask_target = (df_produk['id_produk'] == id_produk_input) & \
                  (df_produk['id_penjual'] == id_penjual_saat_ini)

    if mask_target.any():
        
        produk_dihapus_nama = df_produk.loc[mask_target, 'nama_produk'].iloc[0]
        
        
        konfirmasi = input(f"Anda yakin ingin menghapus '{produk_dihapus_nama}'? (ya/tidak): ").lower().strip()
        
        if konfirmasi == 'ya':
            
            indeks_hapus = df_produk[mask_target].index
            
            df_produk = df_produk.drop(index=indeks_hapus)
            
            
            if write_csv(df_produk, FILE_PRODUK):
                print(f"\nProduk '{produk_dihapus_nama}' berhasil dihapus secara permanen.")
            else:
                print("\nError: Produk gagal dihapus karena kesalahan penulisan file.")
        else:
            print("Penghapusan dibatalkan oleh pengguna.")
    else:
        
        print(f"\nProduk dengan ID {id_produk_input} tidak ditemukan atau bukan milik Anda.")
        
    time.sleep(2)

def riwayat_penjualan():
    clear_screen()
    print("--- RIWAYAT PENJUALAN ---")

    df_order = read_csv(FILE_ORDER)
    df_produk = read_csv(FILE_PRODUK)
    df_user = read_csv(FILE_USER)  

    if df_order.empty:
        print("Belum ada transaksi.")
        input("\nTekan Enter untuk kembali...")
        return

    
    df_order['id_penjual'] = pd.to_numeric(df_order['id_penjual'], errors='coerce').fillna(0).astype(int)
    df_order['id_pembeli'] = pd.to_numeric(df_order['id_pembeli'], errors='coerce').fillna(0).astype(int)
    df_order['harga_pembelian'] = pd.to_numeric(df_order['harga_pembelian'], errors='coerce').fillna(0).astype(int)
    df_produk['id_produk'] = pd.to_numeric(df_produk['id_produk'], errors='coerce').fillna(0).astype(int)
    df_user['id_user'] = pd.to_numeric(df_user['id_user'], errors='coerce').fillna(0).astype(int)

    id_penjual = int(PENGGUNA_SAAT_INI['id_user'])
    df_jual = df_order[df_order['id_penjual'] == id_penjual]

    if df_jual.empty:
        print("Anda belum memiliki riwayat penjualan.")
        input("\nTekan Enter untuk kembali...")
        return

    total_semua = 0

    for _, jual in df_jual.iterrows():
        
        produk = df_produk[df_produk['id_produk'] == jual['id_produk']]
        if not produk.empty:
            nama_produk = produk.iloc[0]['nama_produk']
            harga_satuan = int(produk.iloc[0]['harga'])
        else:
            nama_produk = "(Produk tidak ditemukan)"
            harga_satuan = 0

        
        pembeli = df_user[df_user['id_user'] == int(jual['id_pembeli'])]
        if not pembeli.empty:
            nama_pembeli = pembeli.iloc[0]['username']
        else:
            nama_pembeli = "(Pembeli tidak ditemukan)"

        
        subtotal = harga_satuan * int(jual['kuantitas'])
        total_semua += subtotal

        
        print(f"\nID Order       : {jual['id_order']}")
        print(f"Produk         : {nama_produk}")
        print(f"Harga Satuan   : Rp {harga_satuan:,}".replace(",", "."))
        print(f"Kuantitas      : {jual['kuantitas']}")
        print(f"Subtotal       : Rp {subtotal:,}".replace(",", "."))
        print(f"Pembeli        : {nama_pembeli}")
        print(f"Waktu Transaksi: {jual.get('waktu_transaksi', '-')}")
        print("-" * 40)

    print(f"TOTAL PENJUALAN: Rp {total_semua:,}".replace(",", "."))
    print("-" * 40)

    input("\nTekan Enter untuk kembali...")


def menu_pembeli():
    global PENGGUNA_SAAT_INI
    '''menu utama pembeli'''
    while True:
        clear_screen()
        print(f"--- SELAMAT DATANG, {PENGGUNA_SAAT_INI['username']} ---")
        print("1. Menu Belanja")
        print("2. Ubah Alamat")
        print("3. Riwayat Pembelian")
        print("4. Logout")
        pilihan = input("Pilihan: ").strip()

        if pilihan == '1':
            menu_belanja()
        elif pilihan == '2':
            ubah_alamat()
        elif pilihan == '3':
            riwayat_pembelian()
        elif pilihan == '4':
            PENGGUNA_SAAT_INI = None
            print("Anda telah logout.")
            time.sleep(1)
            break
        else:
            print("Pilihan tidak valid.")
            time.sleep(1)

def ubah_alamat():
    '''Ubah alamat pembeli'''
    global PENGGUNA_SAAT_INI
    clear_screen()
    print("--- UBAH ALAMAT ---")
    alamat_baru = input("Masukkan alamat baru: ").strip()
    if not alamat_baru:
        print("Alamat tidak boleh kosong.")
        time.sleep(2)
        return
    
    df_users = read_csv(FILE_USER)
    idx = df_users.index[df_users['id_user'] == PENGGUNA_SAAT_INI['id_user']][0]
    df_users.at[idx, 'alamat'] = alamat_baru
    write_csv(df_users, FILE_USER)
    
    PENGGUNA_SAAT_INI['alamat'] = alamat_baru
    print("Alamat berhasil diperbarui.")
    time.sleep(2)

def lihat_semua_bibit():
    df_produk = read_csv(FILE_PRODUK)
    if df_produk.empty:
        print("Belum ada bibit di sistem.")
        return pd.DataFrame()  
    
    print("--- SEMUA BIBIT TERSEDIA ---")
   
    df_produk['stok'] = pd.to_numeric(df_produk['stok'], errors='coerce').fillna(0).astype(int)
    df_tersedia = df_produk[df_produk['stok'] > 0]
    
    if df_tersedia.empty:
        print("Semua stok bibit saat ini habis.")
        return pd.DataFrame()

    for i, produk in df_tersedia.iterrows():
        id_produk_val = int(produk['id_produk'])
        nama_val = produk['nama_produk']
        harga_val = int(produk['harga']) if not pd.isna(produk['harga']) else 0
        stok_val = int(produk['stok']) if not pd.isna(produk['stok']) else 0
        deskripsi_val = produk['deskripsi']

        harga_formatted = f"Rp {harga_val:,}".replace(",", ".")
        print("-" * 30)
        print(f"ID Produk: {id_produk_val}")
        print(f"Nama     : {nama_val}")
        print(f"Harga    : {harga_formatted}")
        print(f"Stok     : {stok_val}")
        print(f"Deskripsi: {deskripsi_val}")
        print("-" * 30)
        
    return df_tersedia 

def cari_produk_tertentu():
    '''Cari produk berdasarkan nama'''
    clear_screen()
    print("--- CARI PRODUK ---")
    kata_kunci = input("Masukkan nama produk/kata kunci: ").strip()
    if not kata_kunci:
        print("Kata kunci tidak boleh kosong.")
        time.sleep(2)
        return pd.DataFrame()

    df_produk = read_csv(FILE_PRODUK)
    if df_produk.empty:
        print("Belum ada produk di sistem.")
        time.sleep(2)
        return pd.DataFrame()

    
    df_hasil = df_produk[df_produk['nama_produk'].str.contains(kata_kunci, case=False, na=False)]

    if df_hasil.empty:
        print(f"Tidak ada produk yang cocok dengan '{kata_kunci}'")
        time.sleep(2)
        return pd.DataFrame()

    
    for i, produk in df_hasil.iterrows():
        print(f"ID: {int(produk['id_produk'])}")
        print(f"Nama: {produk['nama_produk']}")
        print(f"Harga: Rp {int(produk['harga']):,}".replace(",", "."))
        print(f" Stok: {int(produk['stok'])}")
    return df_hasil

def riwayat_pembelian():
    clear_screen()
    print("--- RIWAYAT PEMBELIAN ---")

    df_order = read_csv(FILE_ORDER)
    df_produk = read_csv(FILE_PRODUK)
    df_user = read_csv(FILE_USER)

    if df_order.empty:
        print("Belum ada transaksi.")
        input("\nTekan Enter untuk kembali...")
        return

    
    df_order['id_pembeli'] = pd.to_numeric(df_order['id_pembeli'], errors='coerce').fillna(0).astype(int)
    df_order['id_penjual'] = pd.to_numeric(df_order['id_penjual'], errors='coerce').fillna(0).astype(int)
    df_order['harga_pembelian'] = pd.to_numeric(df_order['harga_pembelian'], errors='coerce').fillna(0).astype(int)

    df_user['id_user'] = pd.to_numeric(df_user['id_user'], errors='coerce').fillna(0).astype(int)
    df_produk['id_produk'] = pd.to_numeric(df_produk['id_produk'], errors='coerce').fillna(0).astype(int)

    id_pembeli = int(PENGGUNA_SAAT_INI['id_user'])
    df_beli = df_order[df_order['id_pembeli'] == id_pembeli]

    if df_beli.empty:
        print("Anda belum memiliki riwayat pembelian.")
        input("\nTekan Enter untuk kembali...")
        return

    total_semua_transaksi = 0

    for _, item in df_beli.iterrows():
        
        produk = df_produk[df_produk['id_produk'] == item['id_produk']]
        if not produk.empty:
            nama_produk = produk.iloc[0]['nama_produk']
            harga_satuan = int(produk.iloc[0]['harga'])
        else:
            nama_produk = "(Produk tidak ditemukan)"
            harga_satuan = 0

        
        penjual = df_user[df_user['id_user'] == int(item['id_penjual'])]
        if not penjual.empty:
            nama_penjual = penjual.iloc[0]['username']
        else:
            nama_penjual = "(Penjual tidak ditemukan)"

        
        subtotal = harga_satuan * int(item['kuantitas'])
        total_semua_transaksi += subtotal

       
        print(f"\nID Order   : {item['id_order']}")
        print(f"Produk     : {nama_produk}")
        print(f"Harga      : Rp {harga_satuan:,}".replace(",", "."))
        print(f"Kuantitas  : {item['kuantitas']}")
        print(f"Subtotal   : Rp {subtotal:,}".replace(",", "."))
        print(f"Penjual    : {nama_penjual}")
        print(f"Waktu beli : {item.get('waktu_transaksi', '-')}")
        print("-" * 40)

    print(f"TOTAL SEMUA BELANJA: Rp {total_semua_transaksi:,}".replace(",", "."))
    print("-" * 40)
    input("\nTekan Enter untuk kembali...")

def beli_produk_langsung(produk):
    df_produk = read_csv(FILE_PRODUK)
    df_order = read_csv(FILE_ORDER)

    
    df_produk['stok'] = pd.to_numeric(df_produk['stok'], errors='coerce').fillna(0).astype(int)
    df_produk['harga'] = pd.to_numeric(df_produk['harga'], errors='coerce').fillna(0).astype(int)

    idx_produk = df_produk.index[df_produk['id_produk'] == produk['id_produk']][0]

    if df_produk.at[idx_produk, 'stok'] <= 0:
        print("Stok habis, tidak bisa dibeli.")
        time.sleep(2)
        return
    
    while True:
        try:
            qty = int(input(f"Masukkan jumlah yang ingin dibeli (max {df_produk.at[idx_produk, 'stok']}): "))
            if qty <= 0 or qty > df_produk.at[idx_produk, 'stok']:
                print("Jumlah tidak valid.")
                continue
            break
        except ValueError:
            print("Harus angka!")
    
    df_produk.at[idx_produk, 'stok'] -= qty
    new_id_order = id_baru(FILE_ORDER, 'id_order')

    new_row = {
        'id_order': new_id_order,
        'id_pembeli': int(PENGGUNA_SAAT_INI['id_user']),
        'id_produk': produk['id_produk'],
        'id_penjual': produk['id_penjual'],
        'kuantitas': qty,
        'harga_pembelian': produk['harga'] * qty,
        'waktu_transaksi': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    df_order.loc[len(df_order)] = new_row

    write_csv(df_order, FILE_ORDER)
    write_csv(df_produk, FILE_PRODUK)

    print(f"\nOrder ID {new_id_order} berhasil: {produk['nama_produk']} x{qty}")
    time.sleep(2)

def menu_belanja():
    df_produk = read_csv(FILE_PRODUK)
    if df_produk.empty:
        print("Belum ada produk tersedia")
        time.sleep(2)
        return
    
    
    df_order = read_csv(FILE_ORDER)
    
    
    if not df_order.empty:
        df_order['id_order'] = pd.to_numeric(df_order['id_order'], errors='coerce').fillna(0).astype(int)
        df_order['id_pembeli'] = pd.to_numeric(df_order['id_pembeli'], errors='coerce').fillna(0).astype(int)
    id_awal_sesi = df_order['id_order'].max() if not df_order.empty else 0

    while True:
        clear_screen()
        print("------CARI BIBIT ------")
        print("1. Lihat semua bibit")
        print("2. Cari bibit tertentu")
        print("3. Selesai belanja / Checkout")
        print("4. Kembali ke menu pembeli (pembelian dibatalkan)")
        pilihan = input("Pilihan: ").strip()

        if pilihan == '1':
            df_semua = lihat_semua_bibit()
            if df_semua.empty:
                input("\nTekan Enter untuk kembali...")
                continue
            pilih_id = input("\nMasukkan ID produk untuk beli (atau 'batal'): ").strip()
            if pilih_id.lower() == 'batal':
                continue
            
            try:
                pilih_id_int = int(pilih_id)
                mask_beli = (df_semua['id_produk'] == pilih_id_int)
                if mask_beli.any():
                    produk = df_semua[mask_beli].iloc[0]
                    beli_produk_langsung(produk)
                else:
                    print("Produk tidak ditemukan di daftar tersedia.")
                    time.sleep(2)
            except ValueError:
                print("ID harus berupa angka.")
                time.sleep(2)

        elif pilihan == '2':
            df_hasil = cari_produk_tertentu()
            if df_hasil.empty:
                continue
            while True:
                pilih_id = input("\nMasukkan ID produk untuk beli (atau 'batal'): ").strip()
                if pilih_id.lower() == 'batal':
                    break
                if pilih_id not in df_hasil['id_produk'].astype(str).values:
                    print("Produk tidak ditemukan.")
                    continue
                produk = df_hasil[df_hasil['id_produk'].astype(str) == pilih_id].iloc[0]
                beli_produk_langsung(produk)
                lagi = input("Ingin beli produk lain? (ya/tidak): ").strip().lower()
                if lagi != 'ya':
                    break

        elif pilihan == '3':
            print("\nApakah ingin ganti alamat sebelum checkout?")
            ganti = input("ya/tidak: ").strip().lower()
            if ganti == 'ya':
                ubah_alamat()
            
            
            df_order = read_csv(FILE_ORDER)
            if df_order.empty:
                print("Belum ada transaksi yang dilakukan.")
                input("\nTekan Enter untuk kembali...")
                break

           
            df_order['id_order'] = pd.to_numeric(df_order['id_order'], errors='coerce').fillna(0).astype(int)
            df_order['id_pembeli'] = pd.to_numeric(df_order['id_pembeli'], errors='coerce').fillna(0).astype(int)
            df_order['id_penjual'] = pd.to_numeric(df_order['id_penjual'], errors='coerce').fillna(0).astype(int)
            df_order['harga_pembelian'] = pd.to_numeric(df_order['harga_pembelian'], errors='coerce').fillna(0).astype(int)

            order_user = df_order[
                (df_order['id_pembeli'] == int(PENGGUNA_SAAT_INI['id_user'])) & 
                (df_order['id_order'] > id_awal_sesi)
            ]

            if order_user.empty:
                print("Belum ada transaksi yang dilakukan.")
            else:
                print("\n--- STRUK PEMBELIAN TERAKHIR ---")

                df_produk = read_csv(FILE_PRODUK)
                df_user = read_csv(FILE_USER)   
                df_user['id_user'] = pd.to_numeric(df_user['id_user'], errors='coerce').fillna(0).astype(int)

                total_semua = 0

                for _, item in order_user.iterrows():
                   
                    produk = df_produk[df_produk['id_produk'] == item['id_produk']]
                    if not produk.empty:
                        nama_produk = produk.iloc[0]['nama_produk']
                        harga_satuan = int(produk.iloc[0]['harga'])
                    else:
                        nama_produk = "(Produk tidak ditemukan)"
                        harga_satuan = 0

                    
                    penjual = df_user[df_user['id_user'] == int(item['id_penjual'])]
                    if not penjual.empty:
                        nama_penjual = penjual.iloc[0]['username']
                    else:
                        nama_penjual = "(Penjual tidak ditemukan)"

                    
                    subtotal = harga_satuan * int(item['kuantitas'])
                    total_semua += subtotal

                    
                    print(f"ID Order   : {item['id_order']}")
                    print(f"Produk     : {nama_produk}")
                    print(f"Harga      : Rp {harga_satuan:,}".replace(",", "."))
                    print(f"Kuantitas  : {item['kuantitas']}")
                    print(f"Subtotal   : Rp {subtotal:,}".replace(",", "."))
                    print(f"Penjual    : {nama_penjual}")
                    print(f"Waktu beli : {item.get('waktu_transaksi', '-')}")
                    print("-" * 40)

                print(f"TOTAL BELANJA: Rp {total_semua:,}".replace(",", "."))
                print("-" * 40)
            
            input("\nTekan Enter untuk kembali ke menu utama...")
            break  

        elif pilihan == '4':
            menu_pembeli()

        else:
            print("Pilihan tidak valid.")
            time.sleep(1)

def menu_utama():
    while True:
        clear_screen()
        print("--- SELAMAT DATANG DI PASAR BIBIT ---")
        print("1. Masuk sebagai Penjual")
        print("2. Masuk sebagai Pembeli")
        print("3. Keluar")
        pilihan = input("Pilihan: ")
        
        if pilihan == '1':
            menu_login('penjual')
        elif pilihan == '2':
            menu_login('pembeli')
        elif pilihan == '3':
            print("Terima kasih telah menggunakan aplikasi.")
            break
        else:
            print("Pilihan tidak valid.")
            time.sleep(1)


if __name__ == "__main__":
    inisiai_file() 
    menu_utama()