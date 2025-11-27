import csv
import pandas as pd
import os
import time

# file csv nya
FILE_USER = 'users.csv'
FILE_PRODUK= 'produk.csv'
FILE_ORDER = 'order.csv'

# isi kolomnya
KOLOM_USER = ['id_user', 'username', 'password', 'role', 'alamat']
KOLOM_PRODUK = ['id_produk', 'id_penjual', 'nama_produk', 'deskripsi', 'harga', 'stok']
KOLOM_ORDER = ['id_order', 'id_pembeli', 'id_produk', 'id_penjual', 'kuantitas', 'harga_pembelian']

def setup_files():
    file_headers_map = {
        FILE_USER: KOLOM_USER,
        FILE_PRODUK: KOLOM_PRODUK,
        FILE_ORDER: KOLOM_ORDER
    }

# penetapan user
PENGGUNA_SAAT_INI = None

def clear_screen():
    '''fungsi hapus terminal'''
    os.system('cls' if os.name == 'nt' else 'clear')

# fungsi baca, tulis, update
def read_csv(filename):
    try:
        df = pd.read_csv(filename)
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
# pada fungsi write karena gunanya menimpa, header=True  
# sehingga header di tulis lagi
 
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
    # jika ID tidak ada di file nama, atau ada tapi gaada isinya
    inisiai_file()
    try:
        df = read_csv(filename)
        if df.empty:
            return 1
        df[nama_kolom] = pd.to_numeric(df[nama_kolom], errors='coerce')
        # pd.to_numeric ngubah angka yang str menjadi int atau angka,
        # errors='coerce' jika elemen dalam kolom itu gabisa jadi angka
        # kayak teks kosong maka diubah jadi NaN (Not a Number) 
        # artinya nilai yang hilang atau tidak valid
        df_valid_id = df.dropna(subset=[nama_kolom])
        # dropna() artinya drop NA  atau NaN,
        # guna menghapus baris atau kolom yang mengandung NaN
        # subset=[nama_kolom], parameter penentu kolom mana saja yang harus di cek
        if df_valid_id.empty:
            # Jika tidak ada baris ID yang valid di seluruh file
                return 1
        max_id = df_valid_id[nama_kolom].max()
        return int(max_id) + 1
            
    except Exception as e:
        print(f"Error saat mencari ID untuk {filename}: {e}")
        return 1

# PART LOGIN
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
            hasil_login = login(role)
            if hasil_login:
                if PENGGUNA_SAAT_INI['role'] != role:
                    print(f"Anda login sebagai {PENGGUNA_SAAT_INI['role']}")
                    time.sleep(2)
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
    username = input("Masukkan Username (Kode Unik): ")
    # username gaboleh kosong
    if not username:
        print("Username tidak boleh kosong")
        time.sleep(2)
        return
    # Cek apakah username sudah ada
    df_users = read_csv(FILE_USER)
    if username in df_users['username'].values:
        print("\nUsername sudah digunakan. Silakan pilih nama lain.")
        time.sleep(2)
        return

    password = input("Masukkan Password: ")
    alamat = input("Masukkan Alamat Anda: ")
    
    # Dataframe untuk data baru
    user_baru = pd.DataFrame({
        'id_user': [id_baru(FILE_USER, 'id_user')],
        'username': [username],
        'password': [password],
        'role': [role],
        'alamat': [alamat]
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
    username = input("Username: ")
    password = input("Password: ")

    df_users = read_csv(FILE_USER)
    if df_users.empty:
        print("Login gagal, belum ada pengguna terdaftar")
        return None
    
    filter_mask = (df_users['username'].astype(str) == username) & (df_users['password'].astype(str) == password)
    df_cocok = df_users[filter_mask]
    if len(df_cocok) == 1:
        # login berhasil
        PENGGUNA_SAAT_INI = df_cocok.iloc[0].to_dict()

        # cek role
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

# PART PENJUAL
def menu_penjual():
    global PENGGUNA_SAAT_INI
    while True:
        clear_screen()
        print(f"--- MENU UTAMA PENJUAL: {PENGGUNA_SAAT_INI['username']} ---")
        print("1. Data Produk Saya")
        print("2. Tambah Barang")
        print("3. Update Barang")
        print("4. Hapus Barang")
        # print("5. Statistik Penjualan")
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
        # elif pilihan == '5':
        #     statistik_penjualan()
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
    
    # Logika filter: Hanya tampilkan produk dengan id_penjual yang cocok
    df_produk['id_penjual'] = pd.to_numeric(df_produk['id_penjual'], errors='coerce').fillna(0).astype(int)
    mask_produk_saya = (df_produk['id_penjual'] == id_penjual_saat_ini)
    df_tampil_produk = df_produk[mask_produk_saya]
            
    # 5. Tampilkan hasil (jika ada)
    if df_tampil_produk.empty:
        print("Anda belum memiliki produk yang terdaftar.")
    else:
        # Sortir data berdasarkan ID Produk
        df_tampil_produk = df_tampil_produk.sort_values(by='id_produk')
                
        # Iterasi dan format tampilan
        for i, produk in df_tampil_produk.iterrows():
            # Format data untuk tampilan
            id_produk_val = int(produk['id_produk'])
            # Tambahkan penanganan NaN yang lebih kuat
            harga_val = int(produk['harga']) if not pd.isna(produk['harga']) else 0
            stok_val = int(produk['stok']) if not pd.isna(produk['stok']) else 0
                        
            # Formatting harga dengan titik sebagai pemisah ribuan (konvensi ID)
            harga_formatted = f"Rp {harga_val:,}".replace(",", ".")
                        
            print(f"\nID Produk: {id_produk_val}")
            print(f"    Nama: {produk['nama_produk']}")
            print(f"    Harga: {harga_formatted}")
            print(f"    Stok: {stok_val}")
            print(f"    Deskripsi: {produk['deskripsi']}")
                
    # 6. Jeda akhir
    if jeda:
        input("\nTekan Enter untuk kembali...")

def tambah_produk():
    clear_screen()
    print("--- TAMBAH BARANG BARU ---")
    # Loop untuk input Nama Produk (memastikan tidak kosong)
    while True:
        nama_produk = input("Nama Bibit: ").strip()
        if nama_produk:
            break
        print("Nama produk tidak boleh kosong. Silakan masukkan kembali.")

    deskripsi = input("Deskripsi: ").strip() # Gunakan .strip() untuk membersihkan spasi ekstra

    # Loop untuk input Harga dan Stok (Memastikan bilangan bulat positif)
    while True:
        try:
            # Menggunakan .replace untuk menerima format Rp 10.000 atau 10.000
            input_harga = input("Harga (contoh: 50000): ").replace('.', '').replace('Rp', '').strip()
            harga = int(input_harga)
            
            input_stok = input("Stok Awal: ").strip()
            stok = int(input_stok)
            
            # Pengecekan nilai harus positif
            if harga < 0 or stok < 0:
                 print("\nHarga dan Stok harus bernilai positif (≥ 0).")
                 continue # Kembali ke awal loop
            
            break # Keluar dari loop jika input valid
            
        except ValueError:
            print("\nKesalahan Input: Harga dan Stok harus berupa angka bilangan bulat.")
            # time.sleep(1) # Tidak perlu jeda di dalam loop
            continue
            
    produk_baru_dict = {
        'id_produk': [id_baru(FILE_PRODUK, 'id_produk')],
        'id_penjual': [PENGGUNA_SAAT_INI['id_user']],
        'nama_produk': [nama_produk],
        'deskripsi': [deskripsi],
        'harga': [harga],
        'stok': [stok]
    }
    
    # PENTING: Ubah Dictionary menjadi DataFrame
    df_baru = pd.DataFrame(produk_baru_dict, columns=KOLOM_PRODUK)
    
    # 3. Simpan data dan berikan konfirmasi
    if append_csv(df_baru, FILE_PRODUK): # append_csv sekarang menerima DataFrame
        print(f"\nProduk '{nama_produk}' berhasil ditambahkan ke inventaris Anda.")
    else:
        print("\nProduk gagal ditambahkan karena error penulisan file.")
        
    time.sleep(2)

def update_produk():
    '''Memperbarui informasi produk menggunakan pandas DataFrame'''
    clear_screen()
    
    # 1. Tampilkan daftar produk penjual tanpa jeda akhir
    lihat_produk(jeda=False) 
    
    id_penjual_saat_ini = int(PENGGUNA_SAAT_INI['id_user'])
    
    # 2. Input ID Produk
    print("\n--- UPDATE DATA PRODUK ---")
    id_produk_input = input("Masukkan ID Produk yang ingin di-update (atau 'batal'): ").strip()
    
    if id_produk_input.lower() == 'batal':
        return

    # 3. Baca data
    df_produk = read_csv(FILE_PRODUK) 
    
    # 4. Cari produk berdasarkan ID dan kepemilikan
    # Mask untuk mencari produk milik user saat ini dengan ID yang cocok
    df_produk['id_penjual'] = pd.to_numeric(df_produk['id_penjual'], errors='coerce').fillna(0).astype(int)
    df_produk['id_produk'] = pd.to_numeric(df_produk['id_produk'], errors='coerce').fillna(0).astype(int)
    mask_produk = (df_produk['id_produk'] == id_produk_input) & \
                  (df_produk['id_penjual'] == id_penjual_saat_ini)
    
    # Dapatkan indeks dari produk yang cocok (seharusnya hanya satu)
    indeks_update = df_produk.index[mask_produk]

    if indeks_update.empty:
        print(f"\nProduk dengan ID {id_produk_input} tidak ditemukan atau bukan milik Anda.")
        time.sleep(2)
        return
    
    # Ambil index dari baris yang akan diupdate
    idx = indeks_update[0]
    produk_nama_lama = df_produk.at[idx, 'nama_produk']
    
    print(f"\nProduk yang Diupdate: '{produk_nama_lama}' (ID: {id_produk_input})")
    print(">>> Kosongkan input jika tidak ingin diubah.")
    
    # --- Input dan Update Data Tekstual ---
    
    nama_lama = df_produk.at[idx, 'nama_produk']
    deskripsi_lama = df_produk.at[idx, 'deskripsi']
    
    nama_baru = input(f"Nama Baru (saat ini: {nama_lama}): ").strip()
    deskripsi_baru = input(f"Deskripsi Baru (saat ini: {deskripsi_lama}): ").strip()
    
    # Update jika input tidak kosong
    if nama_baru: 
        df_produk.at[idx, 'nama_produk'] = nama_baru
    if deskripsi_baru: 
        df_produk.at[idx, 'deskripsi'] = deskripsi_baru
        
    # --- Input dan Validasi Data Numerik (Harga & Stok) ---
    
    harga_lama = df_produk.at[idx, 'harga']
    stok_lama = df_produk.at[idx, 'stok']
    
    harga_baru_input = input(f"Harga Baru (saat ini: {harga_lama}): ").strip()
    stok_baru_input = input(f"Stok Baru (saat ini: {stok_lama}): ").strip()

    # Validasi Harga
    if harga_baru_input:
        try:
            # Hapus pemisah ribuan (titik) sebelum konversi (sesuai logika di tambah_produk)
            harga_bersih = harga_baru_input.replace('.', '').replace('Rp', '').strip()
            harga_val = int(harga_bersih)
            if harga_val < 0:
                print("Peringatan: Harga harus positif. Nilai diabaikan.")
            else:
                df_produk.at[idx, 'harga'] = harga_val
        except ValueError:
            print("Error: Input harga tidak valid (bukan angka). Nilai diabaikan.")

    # Validasi Stok
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
    
    # 5. Penulisan dan Feedback
    write_csv(df_produk, FILE_PRODUK)
    time.sleep(2)

def hapus_produk():
    '''Menghapus produk menggunakan pandas DataFrame'''
    clear_screen()
    
    # Tampilkan daftar produk penjual tanpa jeda
    lihat_produk(jeda=False) 

    id_penjual_saat_ini = int(PENGGUNA_SAAT_INI['id_user'])

    # 2. Input ID Produk
    print("\n--- HAPUS DATA PRODUK ---")
    id_produk_input = input("Masukkan ID Produk yang ingin dihapus (atau 'batal'): ").strip()

    if id_produk_input.lower() == 'batal':
        return

    # 3. Baca data
    df_produk = read_csv(FILE_PRODUK)
    
    # 4. Cari produk berdasarkan ID dan kepemilikan
    df_produk['id_penjual'] = pd.to_numeric(df_produk['id_penjual'], errors='coerce').fillna(0).astype(int)
    df_produk['id_produk'] = pd.to_numeric(df_produk['id_produk'], errors='coerce').fillna(0).astype(int)
    mask_target = (df_produk['id_produk'] == id_produk_input) & \
                  (df_produk['id_penjual'] == id_penjual_saat_ini)

    if mask_target.any():
        # Produk ditemukan dan milik penjual
        # Ambil nama produk untuk konfirmasi
        produk_dihapus_nama = df_produk.loc[mask_target, 'nama_produk'].iloc[0]
        
        # Konfirmasi penghapusan
        konfirmasi = input(f"Anda yakin ingin menghapus '{produk_dihapus_nama}'? (ya/tidak): ").lower().strip()
        
        if konfirmasi == 'ya':
            # Ambil index dari baris yang akan dihapus
            indeks_hapus = df_produk[mask_target].index
            # Hapus baris yang sesuai dari DataFrame
            df_produk = df_produk.drop(index=indeks_hapus)
            
            # Tulis ulang data ke file
            if write_csv(df_produk, FILE_PRODUK):
                print(f"\nProduk '{produk_dihapus_nama}' berhasil dihapus secara permanen.")
            else:
                print("\nError: Produk gagal dihapus karena kesalahan penulisan file.")
        else:
            print("Penghapusan dibatalkan oleh pengguna.")
    else:
        # Produk tidak ditemukan atau bukan milik user
        print(f"\nProduk dengan ID {id_produk_input} tidak ditemukan atau bukan milik Anda.")
        
    time.sleep(2)

# PART PEMBELI
def menu_pembeli():
    global PENGGUNA_SAAT_INI
    '''menu utama pembeli'''
    while True:
        clear_screen()
        print(f"--- SELAMAT DATANG, {PENGGUNA_SAAT_INI['username']} ---")
        print("1. Menu Belanja")
        print("2. Ubah Alamat")
        print("3. Logout")
        pilihan = input("Pilihan: ").strip()

        if pilihan == '1':
            menu_belanja()
        elif pilihan == '2':
            ubah_alamat()
        elif pilihan == '3':
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
    # Update di DataFrame users
    df_users = read_csv(FILE_USER)
    idx = df_users.index[df_users['id_user'] == PENGGUNA_SAAT_INI['id_user']][0]
    df_users.at[idx, 'alamat'] = alamat_baru
    write_csv(df_users, FILE_USER)
    # Update session
    PENGGUNA_SAAT_INI['alamat'] = alamat_baru
    print("Alamat berhasil diperbarui.")
    time.sleep(2)

def lihat_semua_bibit():
    df_produk = read_csv(FILE_PRODUK)
    if df_produk.empty:
        print("Belum ada bibit di sistem.")
        return pd.DataFrame()  # Mengembalikan DataFrame kosong
    
    print("--- SEMUA BIBIT TERSEDIA ---")
   # Hanya tampilkan produk dengan stok > 0
    df_produk['stok'] = pd.to_numeric(df_produk['stok'], errors='coerce').fillna(0).astype(int)
    df_tersedia = df_produk[df_produk['stok'] > 0]
    
    if df_tersedia.empty:
        print("Semua stok bibit saat ini habis.")
        return pd.DataFrame()

    for _, produk in df_tersedia.iterrows():
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
        
    # input("\nTekan Enter untuk melanjutkan...") # Dihapus agar user langsung bisa input ID produk di menu_belanja
    return df_tersedia # Mengembalikan data yang tersedia

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

    # Filter produk berdasarkan nama
    df_hasil = df_produk[df_produk['nama_produk'].str.contains(kata_kunci, case=False, na=False)]

    if df_hasil.empty:
        print(f"Tidak ada produk yang cocok dengan '{kata_kunci}'")
        time.sleep(2)
        return pd.DataFrame()

    # Tampilkan hasil pencarian
    for i, produk in df_hasil.iterrows():
        print(f"ID: {int(produk['id_produk'])}")
        print(f"Nama: {produk['nama_produk']}")
        print(f"Harga: Rp {int(produk['harga']):,}".replace(",", "."))
        print(f" Stok: {int(produk['stok'])}")
    return df_hasil

def beli_produk_langsung(produk):
    """Fungsi beli 1 produk langsung, update stok dan simpan order"""
    df_produk = read_csv(FILE_PRODUK)
    df_order = read_csv(FILE_ORDER)
    
    idx_produk = df_produk.index[df_produk['id_produk'] == produk['id_produk']][0]
    
    # Validasi stok
    if int(df_produk.at[idx_produk, 'stok']) <= 0:
        print("Stok habis, tidak bisa dibeli.")
        time.sleep(2)
        return
    
    while True:
        try:
            qty = int(input(f"Masukkan jumlah yang ingin dibeli (max {int(df_produk.at[idx_produk, 'stok'])}): "))
            if qty <= 0 or qty > int(df_produk.at[idx_produk, 'stok']):
                print("Jumlah tidak valid.")
                continue
            break
        except ValueError:
            print("Harus angka!")
    
    # Update stok
    df_produk.at[idx_produk, 'stok'] -= qty
    
    # Buat ID order
    new_id_order = id_baru(FILE_ORDER, 'id_order')
    
    # Simpan order
    new_row = {
        'id_order': new_id_order,
        'id_pembeli': PENGGUNA_SAAT_INI['id_user'],
        'id_produk': produk['id_produk'],
        'id_penjual': produk['id_penjual'],
        'kuantitas': qty,
        'harga_pembelian': produk['harga'] * qty
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
    
    while True:
        clear_screen()
        print("------CARI BIBIT ------")
        print("1. Lihat semua bibit")
        print("2. Cari bibit tertentu")
        print("3. Selesai belanja / Checkout")
        pilihan = input("pilihan: ").strip()

        if pilihan == '1':
            df_semua = lihat_semua_bibit()
            if df_semua.empty:
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
            # Cetak struk pembelian terakhir
            df_order = read_csv(FILE_ORDER)
            order_user = df_order[df_order['id_pembeli'] == PENGGUNA_SAAT_INI['id_user']].tail(10)  # 10 terakhir saja
            if order_user.empty:
                print("Belum ada transaksi yang dilakukan.")
            else:
                print("\n--- STRUK PEMBELIAN TERAKHIR ---")
                for _, item in order_user.iterrows():
                    print(f"ID Order: {item['id_order']}")
                    print(f"Produk  : {item['id_produk']} x {item['kuantitas']} - Rp {item['harga_pembelian']:,}".replace(",", "."))
                    print("---")
            input("\nTekan Enter untuk kembali ke menu utama...")
            break
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

# --- Titik Mulai Program ---
if __name__ == "__main__":
    inisiai_file() # Pastikan semua file CSV ada
    menu_utama()