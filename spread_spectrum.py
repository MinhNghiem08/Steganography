import numpy as np
from scipy.io import wavfile

def binary_message(message):
    """Chuyển đổi chuỗi tin nhắn thành một chuỗi bit nhị phân."""
    return ''.join(format(ord(char), '08b') for char in message)

def spread_spectrum_embed(carrier_file, secret_message, output_file):
    """
    Giấu một chuỗi tin nhắn vào file WAV bằng kỹ thuật Spread Spectrum.
    """
    try:
        sample_rate, data = wavfile.read(carrier_file)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file âm thanh {carrier_file}")
        return
    except ValueError:
        print("Lỗi: File WAV không đúng định dạng. Đảm bảo file là định dạng PCM.")
        return

    # Chuyển đổi dữ liệu âm thanh về kiểu float để xử lý
    data = data.astype(np.float64)
    
    # Mã hóa tin nhắn thành chuỗi bit
    secret_bits = binary_message(secret_message)
    print(f"Tin nhắn bí mật (dưới dạng bit): {secret_bits}")
    
    # Tạo chuỗi giả ngẫu nhiên (Pseudorandom sequence)
    # Đây là chìa khóa để giấu và trích xuất.
    np.random.seed(42)  # Dùng seed để chuỗi có thể tái tạo được
    chip_size = 1000  # Kích thước 'chip' cho mỗi bit
    
    # Kiểm tra xem file có đủ lớn để giấu tin không
    total_data_points_needed = len(secret_bits) * chip_size
    if total_data_points_needed > len(data):
        print("Lỗi: File âm thanh quá nhỏ để giấu tin nhắn này.")
        return

    # Tạo một chuỗi nhiễu giả ngẫu nhiên có cùng kích thước
    pn_sequence = np.random.randn(total_data_points_needed) * 0.1 # Biên độ nhiễu 0.1

    # Phân tán tin nhắn vào chuỗi nhiễu
    embedded_sequence = np.zeros_like(pn_sequence)
    for i, bit in enumerate(secret_bits):
        # Lấy một đoạn chuỗi ngẫu nhiên tương ứng với 1 bit tin nhắn
        start_index = i * chip_size
        end_index = start_index + chip_size
        
        # Nếu bit là '1', nhân chuỗi ngẫu nhiên với 1
        # Nếu bit là '0', nhân chuỗi ngẫu nhiên với -1
        amplitude_scale = 1 if bit == '1' else -1
        embedded_sequence[start_index:end_index] = pn_sequence[start_index:end_index] * amplitude_scale

    # Giấu tín hiệu đã phân tán vào file âm thanh
    stego_audio = np.copy(data)
    stego_audio[:total_data_points_needed] += embedded_sequence
    
    # Chuẩn hóa lại dữ liệu và lưu
    stego_audio_int16 = np.int16(stego_audio / np.max(np.abs(stego_audio)) * 32767)
    wavfile.write(output_file, sample_rate, stego_audio_int16)
    print(f"Đã giấu tin nhắn vào file: {output_file}")


def spread_spectrum_extract(stego_file, secret_message_length_bits):
    """
    Trích xuất tin nhắn từ file WAV đã giấu bằng Spread Spectrum.
    """
    try:
        sample_rate, data = wavfile.read(stego_file)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file âm thanh {stego_file}")
        return ""
    except ValueError:
        print("Lỗi: File WAV không đúng định dạng. Đảm bảo file là định dạng PCM.")
        return ""
        
    data = data.astype(np.float64)
    
    # Tái tạo chuỗi giả ngẫu nhiên giống hệt khi giấu
    np.random.seed(42)
    chip_size = 1000
    
    total_data_points = secret_message_length_bits * chip_size
    pn_sequence = np.random.randn(total_data_points) * 0.1

    extracted_bits = ""
    for i in range(secret_message_length_bits):
        start_index = i * chip_size
        end_index = start_index + chip_size
        
        # Lấy đoạn tín hiệu đã giấu
        stego_segment = data[start_index:end_index]

        # Tách tín hiệu gốc bằng cách nhân với chuỗi ngẫu nhiên ban đầu
        correlation = np.dot(stego_segment, pn_sequence[start_index:end_index])
        
        # Quyết định bit
        if correlation > 0:
            extracted_bits += '1'
        else:
            extracted_bits += '0'
    
    # Chuyển đổi chuỗi bit thành tin nhắn
    message = "".join([chr(int(extracted_bits[i:i+8], 2)) for i in range(0, len(extracted_bits), 8)])
    
    print(f"Tin nhắn đã trích xuất: {message}")
    return message


# --- Ví dụ sử dụng ---
# Tạo một file WAV mẫu 
sample_rate = 44100
duration = 10
frequency = 440
t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
amplitude = np.iinfo(np.int16).max * 0.5
audio_data = amplitude * np.sin(2. * np.pi * frequency * t)
wavfile.write("carrier_file.wav", sample_rate, audio_data.astype(np.int16))

# Giấu tin nhắn
secret_message_to_hide = "Hello World!"
spread_spectrum_embed("carrier_file.wav", secret_message_to_hide, "stego_audio.wav")

# Trích xuất tin nhắn
secret_message_length_bits = len(binary_message(secret_message_to_hide))
spread_spectrum_extract("stego_audio.wav", secret_message_length_bits)
