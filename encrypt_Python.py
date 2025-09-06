import os
# Cài đặt PyCryptodome: pip install pycryptodomex
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad

# Hàm mã hóa file
def encrypt_file(file_path, key):
    # Đọc nội dung file
    with open(file_path, 'rb') as f:
        data = f.read()

    # Tạo đối tượng cipher AES
    cipher = AES.new(key, AES.MODE_CBC)
    
    # Mã hóa dữ liệu và thêm padding
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))

    # Ghi dữ liệu đã mã hóa ra file mới
    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as f:
        f.write(cipher.iv)  # Ghi IV (Initial Vector)
        f.write(encrypted_data)
    
    return encrypted_file_path

# Hàm giải mã file
def decrypt_file(encrypted_file_path, key):
    # Đọc IV và dữ liệu đã mã hóa
    with open(encrypted_file_path, 'rb') as f:
        iv = f.read(AES.block_size)
        encrypted_data = f.read()

    # Tạo đối tượng cipher AES
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Giải mã dữ liệu và xóa padding
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    # Ghi dữ liệu đã giải mã ra file mới
    decrypted_file_path = encrypted_file_path.replace('.enc', '.dec')
    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)
        
    return decrypted_file_path

# --- Ví dụ sử dụng ---
if __name__ == "__main__":
    # Tạo một file văn bản mẫu
    with open('secret.txt', 'w') as f:
        f.write('Đây là thông tin bí mật cần được ẩn đi.')

    # Tạo một khóa AES ngẫu nhiên (dài 32 byte = 256 bit)
    key = get_random_bytes(32)
    
    # Ghi khóa này ra file key.bin
    with open('key.bin', 'wb') as f:
        f.write(key)
    print("Khóa mã hóa đã được lưu vào file key.bin.")

    # Mã hóa file
    encrypted_file = encrypt_file('secret.txt', key)
    print(f"File đã được mã hóa: {encrypted_file}")

    # Giải mã file (chỉ để kiểm tra)
    decrypted_file = decrypt_file(encrypted_file, key)
    print(f"File đã được giải mã: {decrypted_file}")
