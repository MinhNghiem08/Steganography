import wave
import numpy as np
import os
import subprocess

# Steghide đã được cài đặt và có thể chạy từ terminal/command line
# Lệnh 'steghide' sẽ được gọi thông qua subprocess.

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
    # Sửa lỗi logic, hàm này tạo ra chuỗi dựa trên binary_message
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
    
def embed_message_in_audio(audio_path, output_path, message):
    """Nhúng một thông điệp vào file âm thanh bằng LSB."""
    try:
        with wave.open(audio_path, 'rb') as audio_file:
            n_frames = audio_file.getnframes()
            n_channels = audio_file.getnchannels()
            sampwidth = audio_file.getsampwidth()
            framerate = audio_file.getframerate()
            
            frames = audio_file.readframes(n_frames)
            
            #  Tạo một bản sao có thể ghi được của mảng
            audio_array = np.frombuffer(frames, dtype=np.int16).copy()
            
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file âm thanh tại '{audio_path}'.")
        return
    
    binary_message = message_to_binary(message)
    message_len = len(binary_message)
    
    if message_len > len(audio_array):
        print("Lỗi: Thông điệp quá dài, không thể giấu trong file âm thanh này.")
        return

    print(f"\n--- Bắt đầu nhúng lớp thứ 2 (LSB Python) ---")
    print(f"Bắt đầu nhúng thông điệp có độ dài {message_len} bit...")
    
    for i in range(message_len):
        bit_message = int(binary_message[i])
        sample = audio_array[i]
        audio_array[i] = (sample & ~1) | bit_message
        
    print(f"Nhúng thành công {message_len} bit.")

    with wave.open(output_path, 'wb') as output_audio:
        output_audio.setnchannels(n_channels)
        output_audio.setsampwidth(sampwidth)
        output_audio.setframerate(framerate)
        output_audio.writeframes(audio_array.tobytes())
    
    print(f"Quá trình nhúng LSB hoàn tất. File âm thanh mới được lưu tại: {output_path}")
    return True

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

def run_steghide_embed(input_file, secret_file, output_file, password):
    """Sử dụng Steghide để nhúng một file bí mật vào file audio."""
    print("\n--- Bắt đầu nhúng lớp thứ nhất (Steghide) ---")
    print(f"Nhúng file '{secret_file}' vào file '{input_file}'...")
    
    command = ["steghide", "embed", "-cf", input_file, "-ef", secret_file, "-sf", output_file, "-p", password, "-f"]
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Nhúng Steghide thành công. File âm thanh mới được lưu tại: {output_file}")
        return True
    except FileNotFoundError:
        print("Lỗi: Steghide không được tìm thấy. Hãy đảm bảo nó đã được cài đặt và nằm trong PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chạy Steghide: {e.stderr}")
        return False

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

# --- Ví dụ sử dụng ---
if __name__ == '__main__':
    # Ta có một file âm thanh gốc tên là "carrier_file.wav"
    input_audio_file = "carrier_file.wav"
    
    # Message thứ nhất - Giấu bằng Steghide (trong một file riêng)
    secret_file_name = "secret.txt"
    secret_text_steghide = "Đây là thông điệp Cấp 1, được giấu bằng Steghide và mật khẩu mạnh."
    password_steghide = "supersecretpassword123"
    
    # Message thứ hai - Giấu bằng LSB Python
    output_audio_steghide = "stego_audio_steghide.wav"
    final_stego_audio = "final_stego_audio.wav"
    secret_text_lsb = "Đây là thông điệp Cấp 2, được giấu bằng LSB Python."

    # 1. Chuẩn bị file tin bí mật cho Steghide
    with open(secret_file_name, "w") as f:
        f.write(secret_text_steghide)
        print(f"Tạo file bí mật cho Steghide: {secret_file_name}")

    # 2. Nhúng lớp thứ nhất bằng Steghide
    if run_steghide_embed(input_audio_file, secret_file_name, output_audio_steghide, password_steghide):
        # 3. Nhúng lớp thứ hai bằng LSB Python
        if embed_message_in_audio(output_audio_steghide, final_stego_audio, secret_text_lsb):
            print("\n" + "="*50)
            print("Toàn bộ quá trình nhúng hoàn tất. File cuối cùng: final_stego_audio.wav")
            
            print("="*50)
    else:
        print("\n" + "="*50)
        print("Quá trình nhúng Steghide thất bại. Không thể tiến hành bước nhúng LSB.")
        print("="*50)
