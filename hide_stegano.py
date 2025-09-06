import wave
import os

def hide_text_in_audio(audio_file_path, text_file_path, output_path):
    """
    Ẩn nội dung từ file văn bản vào file âm thanh WAV bằng kỹ thuật LSB.
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

        # 6. Giấu dữ liệu bằng cách thay đổi bit LSB
        new_frames = list(frames)
        for i, bit in enumerate(full_binary_data):
            current_byte = new_frames[i]
            # Thay đổi bit LSB của byte
            new_byte = (current_byte & 0b11111110) | int(bit)
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

# --- Ví dụ sử dụng ---
if __name__ == "__main__":
    # Tên file âm thanh gốc và file văn bản
    audio_input_file = "Audio_secret.wav"
    text_input_file = "secret_message.txt"
    output_audio_file = "stegano_output.wav"

    # Tạo file text mẫu nếu chưa có
    if not os.path.exists(text_input_file):
        with open(text_input_file, 'w') as f:
            f.write("Đây là một thông điệp bí mật.")
            print(f"Đã tạo file mẫu '{text_input_file}' để thử nghiệm.")

    # Gọi hàm để giấu tin
    hide_text_in_audio(audio_input_file, text_input_file, output_audio_file)
