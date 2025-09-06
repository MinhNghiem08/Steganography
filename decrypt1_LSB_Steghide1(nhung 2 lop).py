import wave
import numpy as np
import os
import subprocess

def message_to_binary(message):
    """
    Chuyển đổi một chuỗi văn bản thành chuỗi nhị phân.
    Thêm một dấu hiệu kết thúc (delimiter) vào cuối thông điệp để dễ dàng trích xuất.
    """
    delimiter = "#####"
    message_with_delimiter = message + delimiter
    binary_message = ''.join(format(ord(char), '08b') for char in message_with_delimiter)
    return binary_message

def binary_to_message(binary_message):
    """Chuyển đổi một chuỗi nhị phân thành chuỗi văn bản."""
    # Sửa lỗi logic, hàm này phải tạo ra chuỗi dựa trên binary_message
    message = ""
    delimiter_binary = message_to_binary("#####")
    delimiter_len = len(delimiter_binary)
    # Loại bỏ dấu kết thúc khỏi chuỗi nhị phân trước khi chuyển đổi
    if binary_message.endswith(delimiter_binary):
        binary_message = binary_message[:-delimiter_len]
    
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        message += chr(int(byte, 2))
    return message
    
def extract_message_from_audio(audio_path):
    """Trích xuất thông điệp từ file âm thanh đã giấu tin bằng LSB."""
    try:
        with wave.open(audio_path, 'rb') as audio_file:
            n_frames = audio_file.getnframes()
            frames = audio_file.readframes(n_frames)
            audio_array = np.frombuffer(frames, dtype=np.int16)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file âm thanh tại '{audio_path}'.")
        return None
    
    print("\n--- Bắt đầu trích xuất lớp LSB Python ---")
    print("Bắt đầu trích xuất thông điệp...")
    
    binary_message = ""
    delimiter_binary = message_to_binary("#####")
    delimiter_len = len(delimiter_binary)
    
    for sample in audio_array:
        lsb = sample & 1
        binary_message += str(lsb)
        
        if len(binary_message) >= delimiter_len and binary_message.endswith(delimiter_binary):
            break
            
    if binary_message.endswith(delimiter_binary):
        binary_message = binary_message[:-delimiter_len]
        extracted_message = binary_to_message(binary_message)
        print("Trích xuất LSB thành công! Đã tìm thấy dấu hiệu kết thúc.")
        return extracted_message
    else:
        print("Lỗi: Không tìm thấy dấu hiệu kết thúc LSB. Có thể file không chứa tin hoặc tin bị hỏng.")
        return None

def run_steghide_extract(input_file, output_path, password):
    """Sử dụng Steghide để trích xuất file bí mật từ file audio."""
    print("\n--- Bắt đầu trích xuất lớp Steghide ---")
    print(f"Trích xuất file từ '{input_file}'...")

    command = ["steghide", "extract", "-sf", input_file, "-p", password, "-xf", output_path, "-f"]
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Trích xuất Steghide thành công. File bí mật được lưu tại: {output_path}")
        return True
    except FileNotFoundError:
        print("Lỗi: Steghide không được tìm thấy. Hãy đảm bảo nó đã được cài đặt và nằm trong PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chạy Steghide: {e.stderr}")
        return False

# --- Ví dụ trích xuất ---
if __name__ == '__main__':
    # Có các file đã được nhúng từ script trước
    final_stego_audio = "final_stego_audio.wav"
    output_audio_steghide = "stego_audio_steghide.wav"
    password_steghide = "supersecretpassword123"
    
    print("\n" + "#"*50)
    print("BẮT ĐẦU QUÁ TRÌNH TRÍCH XUẤT")
    print("#"*50)
    
    # 1. Trích xuất lớp LSB Python trước
    extracted_lsb_message = extract_message_from_audio(final_stego_audio)
    if extracted_lsb_message:
        print(f"Thông điệp LSB được trích xuất: '{extracted_lsb_message}'")
    
    # 2. Trích xuất lớp Steghide sau
    output_secret_file = "extracted_secret_steghide.txt"
    if run_steghide_extract(output_audio_steghide, output_secret_file, password_steghide):
        try:
            with open(output_secret_file, 'r') as f:
                extracted_steghide_text = f.read()
                print(f"Thông điệp Steghide được trích xuất: '{extracted_steghide_text}'")
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file bí mật đã trích xuất: {output_secret_file}")
