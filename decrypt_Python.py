import os
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

# Hàm giải mã file
def decrypt_file(encrypted_file_path, key):
    """
    Giải mã một tệp tin đã được mã hóa bằng AES.

    Args:
        encrypted_file_path (str): Đường dẫn đến tệp tin đã mã hóa.
        key (bytes): Khóa mã hóa (độ dài 32 byte).

    Returns:
        str: Đường dẫn đến tệp tin đã giải mã.
    """
    try:
        # Đọc IV(intial vector) và dữ liệu đã mã hóa
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
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy tệp tin {encrypted_file_path}.")
        return None
    except ValueError as e:
        print(f"Lỗi giải mã: Vui lòng kiểm tra lại khóa (key). Lỗi: {e}")
        return None
    except Exception as e:
        print(f"Đã xảy ra lỗi không xác định: {e}")
        return None

# --- Ví dụ sử dụng để giải mã tệp đã trích xuất ---
if __name__ == "__main__":
    # Tên của file đã được trích xuất từ Steghide
    encrypted_file = "secret.txt.enc"

    # Đọc khóa mã hóa từ file key.bin
    # LƯU Ý: Khóa này phải giống với khóa được sử dụng để mã hóa file ban đầu.
    try:
        with open('key.bin', 'rb') as f:
            key = f.read()
            print("Đã đọc khóa mã hóa từ file key.bin.")
            
            # Kiểm tra độ dài khóa
            if len(key) != 32:
                print("Lỗi: Độ dài của khóa không hợp lệ. Khóa phải có độ dài 32 byte (256 bit).")
            else:
                # Giải mã tệp tin
                decrypted_file = decrypt_file(encrypted_file, key)
                if decrypted_file:
                    print(f"File đã được giải mã thành công: {decrypted_file}")
                else:
                    print("Không thể giải mã file.")

    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'key.bin'. Vui lòng đảm bảo file khóa nằm trong cùng thư mục.")
    except Exception as e:
        print(f"Đã xảy ra lỗi khi đọc khóa: {e}")
