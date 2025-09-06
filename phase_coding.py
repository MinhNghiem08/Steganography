import numpy as np
from scipy.io import wavfile

def hide_message_phase_coding(carrier_file, secret_message, output_file):
    """
    Giấu một chuỗi tin nhắn vào file WAV bằng kỹ thuật phase coding đơn giản.
    """
    try:
        sample_rate, data = wavfile.read(carrier_file)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file âm thanh {carrier_file}")
        return
    except ValueError:
        print("Lỗi: File WAV không đúng định dạng. Đảm bảo file là định dạng PCM.")
        return

    # Chuyển đổi dữ liệu âm thanh về dạng float để xử lý
    data = data.astype(np.float64)

    # Chuyển đổi tin nhắn thành chuỗi bit
    secret_bits = ''.join(format(ord(char), '08b') for char in secret_message)
    print(f"Tin nhắn bí mật (dưới dạng bit): {secret_bits}")
    
    # Chia dữ liệu thành các khối để mã hóa
    # Kích thước khối phải đủ lớn để giấu 1 bit
    block_size = 512  
    num_blocks = len(data) // block_size

    if len(secret_bits) > num_blocks:
        print("Lỗi: File âm thanh quá nhỏ để giấu tin nhắn này.")
        return

    # Thực hiện biến đổi Fourier cho từng khối
    stego_data = np.copy(data)

    for i, bit in enumerate(secret_bits):
        start_index = i * block_size
        end_index = start_index + block_size

        # Lấy một khối âm thanh
        block = data[start_index:end_index]

        # Biến đổi Fourier để lấy thông tin về pha
        fft_block = np.fft.fft(block)
        
        # Lấy pha của tần số thấp (thường là tần số đầu tiên)
        phase_low_freq = np.angle(fft_block[1]) 

        # Mã hóa bit vào pha
        if bit == '0':
            # Giữ nguyên pha (mã hóa '0')
            target_phase = phase_low_freq
        else: # bit == '1'
            # Đảo pha (mã hóa '1')
            target_phase = phase_low_freq + np.pi  

        # Thay đổi pha của khối đó
        fft_block[1] = np.abs(fft_block[1]) * np.exp(1j * target_phase)
        
        # Chuyển đổi ngược về miền thời gian
        stego_block = np.fft.ifft(fft_block)
        stego_data[start_index:end_index] = np.real(stego_block)

    # Chuẩn hóa lại dữ liệu và lưu
    stego_data_int16 = np.int16(stego_data / np.max(np.abs(stego_data)) * 32767)
    wavfile.write(output_file, sample_rate, stego_data_int16)
    print(f"Đã giấu tin nhắn vào file: {output_file}")


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
hide_message_phase_coding("carrier_file.wav", "Hello world!", "stego_audio.wav")
