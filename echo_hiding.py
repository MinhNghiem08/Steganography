import numpy as np
from scipy.io import wavfile

def hide_message_in_wav(carrier_file, secret_message, output_file):
    """
    Giấu một chuỗi tin nhắn vào file WAV bằng kỹ thuật echo hiding 
    """
    # Đọc file WAV
    sample_rate, data = wavfile.read(carrier_file)

    # Chuyển đổi dữ liệu âm thanh về kiểu float để dễ xử lý
    data = data.astype(np.float32)

    # Mã hóa tin nhắn thành chuỗi bit
    secret_bits = ''.join(format(ord(char), '08b') for char in secret_message)
    print(f"Tin nhắn bí mật (dưới dạng bit): {secret_bits}")
    
    # Tính toán thông số echo
    # Echo '0' (delay ngắn) và Echo '1' (delay dài)
    delay_0 = int(sample_rate * 0.001)  # 1ms
    delay_1 = int(sample_rate * 0.002)  # 2ms
    decay_rate = 0.5

    # Đảm bảo có đủ không gian để giấu
    if len(secret_bits) > (len(data) - max(delay_0, delay_1)):
        print("Lỗi: File âm thanh quá nhỏ để giấu tin nhắn này.")
        return

    # Giấu từng bit
    stego_audio = np.copy(data)
    for i, bit in enumerate(secret_bits):
        # Lấy một đoạn âm thanh nhỏ để giấu bit
        start_index = i * (max(delay_0, delay_1) * 2) # Khoảng cách giữa các bit
        segment = data[start_index : start_index + max(delay_0, delay_1) * 2]

        if bit == '0':
            # Tạo echo '0' (delay ngắn)
            echo = np.zeros_like(segment)
            echo[delay_0:] = segment[:-delay_0] * decay_rate
            stego_audio[start_index : start_index + len(echo)] += echo
        else: # bit == '1'
            # Tạo echo '1' (delay dài)
            echo = np.zeros_like(segment)
            echo[delay_1:] = segment[:-delay_1] * decay_rate
            stego_audio[start_index : start_index + len(echo)] += echo

    # Chuẩn hóa lại dữ liệu và lưu
    stego_audio_int16 = np.int16(stego_audio / np.max(np.abs(stego_audio)) * 32767)
    wavfile.write(output_file, sample_rate, stego_audio_int16)
    print(f"Đã giấu tin nhắn vào file: {output_file}")


# --- Ví dụ sử dụng ---
# Tạo một file WAV mẫu 
# Tần số 44100Hz, 16bit, 2s
sample_rate = 44100
duration = 2
frequency = 440  # A4 note
t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
amplitude = np.iinfo(np.int16).max * 0.5
audio_data = amplitude * np.sin(2. * np.pi * frequency * t)
wavfile.write("carrier_file.wav", sample_rate, audio_data.astype(np.int16))

# Giấu tin nhắn
hide_message_in_wav("carrier_file.wav", "Hello world!", "stego_audio.wav")
