import wave
import os

def hide_text_in_audio(audio_file_path, text_file_path, output_path, bit_to_modify=0):
    """
    Ẩn nội dung từ file văn bản vào file âm thanh WAV bằng kỹ thuật LSB.
    
    Tham số:
    audio_file_path (str): Đường dẫn đến file âm thanh WAV.
    text_file_path (str): Đường dẫn đến file văn bản chứa thông điệp bí mật.
    output_path (str): Đường dẫn để lưu file âm thanh đã giấu tin.
    bit_to_modify (int): Bit thứ n (từ 0 đến 7) trong mỗi byte để giấu tin.
                         Mặc định là 0 (bit cuối cùng).
    """
    try:
        # 1. Kiểm tra sự tồn tại của các file đầu vào
        if not os.path.exists(audio_file_path) or not os.path.exists(text_file_path):
            print("❌ Lỗi: Không tìm thấy một trong các file đầu vào.")
            print(f"Vui lòng kiểm tra lại đường dẫn của '{audio_file_path}' và '{text_file_path}'.")
            return

        # 2. Đọc nội dung từ file văn bản
        with open(text_file_path, 'r', encoding='utf-8') as text_file:
            text_data = text_file.read()

        # 3. Mở và đọc dữ liệu từ file audio WAV
        with wave.open(audio_file_path, 'rb') as audio_file:
            params = audio_file.getparams()
            frames = list(audio_file.readframes(params.nframes))

        # 4. Chuyển đổi văn bản thành chuỗi bit và thêm dấu kết thúc
        end_marker = '$#*'
        binary_text = ''.join(f'{ord(char):08b}' for char in text_data)
        binary_end_marker = ''.join(f'{ord(char):08b}' for char in end_marker)
        full_binary_data = binary_text + binary_end_marker

        # 5. Kiểm tra dung lượng
        # Mỗi byte trong frames có thể chứa 1 bit dữ liệu
        if len(full_binary_data) > len(frames):
            print("❌ Lỗi: File âm thanh quá nhỏ để chứa toàn bộ dữ liệu.")
            return

        # 6. Giấu dữ liệu bằng cách thay đổi bit đã chọn
        # Tạo mask để thay đổi bit
        mask = 1 << bit_to_modify
        
        new_frames = list(frames)
        for i, bit in enumerate(full_binary_data):
            current_byte = new_frames[i]
            
            # Xóa bit cũ
            current_byte = current_byte & (~mask)

            # Đặt bit mới
            if bit == '1':
                new_byte = current_byte | mask
            else:
                new_byte = current_byte
            
            new_frames[i] = new_byte

        # 7. Ghi dữ liệu đã sửa đổi vào file WAV mới
        modified_frames = bytes(new_frames)
        with wave.open(output_path, 'wb') as output_file:
            output_file.setparams(params)
            output_file.writeframes(modified_frames)
            
        print(f"✅ Đã ẩn dữ liệu thành công vào '{output_path}'")
        print(f"📝 Nội dung đã giấu: {text_data[:30]}...")

    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

def extract_text_from_audio(audio_file_path, bit_to_modify=0):
    """
    Trích xuất nội dung từ file âm thanh WAV đã được giấu tin.
    
    Tham số:
    audio_file_path (str): Đường dẫn đến file âm thanh WAV.
    bit_to_modify (int): Bit thứ n (từ 0 đến 7) trong mỗi byte đã được dùng để giấu tin.
                         Mặc định là 0 (bit cuối cùng).
    """
    try:
        # 1. Kiểm tra sự tồn tại của file đầu vào
        if not os.path.exists(audio_file_path):
            print("❌ Lỗi: Không tìm thấy file âm thanh.")
            return None

        # 2. Mở và đọc dữ liệu từ file audio WAV
        with wave.open(audio_file_path, 'rb') as audio_file:
            frames = list(audio_file.readframes(audio_file.getnframes()))

        # 3. Trích xuất chuỗi bit từ dữ liệu âm thanh
        mask = 1 << bit_to_modify
        binary_data = ""
        for frame in frames:
            bit = (frame & mask) >> bit_to_modify
            binary_data += str(bit)

        # 4. Chuyển đổi chuỗi bit thành văn bản
        extracted_text = ""
        end_marker = '$#*'
        binary_end_marker = ''.join(f'{ord(char):08b}' for char in end_marker)

        # Lặp qua chuỗi nhị phân theo từng byte
        for i in range(0, len(binary_data), 8):
            byte_string = binary_data[i:i+8]
            
            # Kiểm tra dấu kết thúc
            if i + len(binary_end_marker) <= len(binary_data) and binary_data[i:i + len(binary_end_marker)] == binary_end_marker:
                print("✅ Đã tìm thấy dấu kết thúc, hoàn tất trích xuất.")
                break
            
            # Chuyển đổi chuỗi bit 8 ký tự thành ký tự
            extracted_text += chr(int(byte_string, 2))
            
        print(f"✅ Đã trích xuất thành công nội dung từ '{audio_file_path}'")
        return extracted_text

    except Exception as e:
        print(f"❌ Có lỗi xảy ra trong quá trình trích xuất: {e}")
        return None

# --- Ví dụ sử dụng ---
if __name__ == "__main__":
    # Tên file âm thanh gốc và file văn bản
    audio_input_file = "Audio_secret.wav"
    text_input_file = "secret_message.txt"
    output_audio_file = "stegano_output2.wav"


    # 1. Giấu tin vào bit cuối (bit 0)
    print("\n--- Giấu tin vào bit cuối (LSB) ---")
    hide_text_in_audio(audio_input_file, text_input_file, output_audio_file, bit_to_modify=0)
    
    # 2. Trích xuất tin từ file đã giấu ở bit 0
    print("\n--- Trích xuất tin từ file đã giấu ở bit cuối ---")
    extracted_message = extract_text_from_audio(output_audio_file, bit_to_modify=0)
    if extracted_message:
        print(f"📝 Nội dung trích xuất: '{extracted_message}'")
    
    # 3. Giấu tin vào bit kế cuối (bit 1)
    # Tên file mới để tránh ghi đè
    output_audio_file_2 = "stegano_output_bit1.wav"
    print("\n--- Giấu tin vào bit kế cuối ---")
    hide_text_in_audio(audio_input_file, text_input_file, output_audio_file_2, bit_to_modify=1)
    
    # 4. Trích xuất tin từ file đã giấu ở bit 1
    print("\n--- Trích xuất tin từ file đã giấu ở bit kế cuối ---")
    extracted_message_2 = extract_text_from_audio(output_audio_file_2, bit_to_modify=1)
    if extracted_message_2:
        print(f"📝 Nội dung trích xuất: '{extracted_message_2}'")
