import numpy as np
import wave

def calculate_snr_psnr(original_audio_path, modified_audio_path):
    """
    Calculates SNR and PSNR between two WAV audio files.
    """
    try:
        # Read original audio file
        with wave.open(original_audio_path, 'r') as original_file:
            original_frames = original_file.readframes(original_file.getnframes())
            original_data = np.frombuffer(original_frames, dtype=np.int16)

        # Read modified audio file
        with wave.open(modified_audio_path, 'r') as modified_file:
            modified_frames = modified_file.readframes(modified_file.getnframes())
            modified_data = np.frombuffer(modified_frames, dtype=np.int16)

    except FileNotFoundError:
        print("Error: One or both files were not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

    # Ensure both arrays have the same length
    min_len = min(len(original_data), len(modified_data))
    original_data = original_data[:min_len]
    modified_data = modified_data[:min_len]

    # Calculate Mean Squared Error (MSE)
    mse = np.mean((original_data - modified_data) ** 2)

    if mse == 0:
        print("The files are identical. SNR and PSNR are infinite.")
        return float('inf'), float('inf')

    # Calculate Signal Power (Ps)
    signal_power = np.mean(original_data ** 2)

    # Calculate Noise Power (Pn) - equivalent to MSE
    noise_power = mse

    # Calculate SNR in dB
    snr_db = 10 * np.log10(signal_power / noise_power)

    # Calculate PSNR in dB
    max_signal_value = np.max(np.abs(original_data))
    psnr_db = 10 * np.log10((max_signal_value ** 2) / mse)

    return snr_db, psnr_db

# --- Example Usage ---
if __name__ == "__main__":
    # Replace these paths with your actual file paths
    original_file = "Audio_secret.wav"
    modified_file = "embedded_audio.wav"

    snr, psnr = calculate_snr_psnr(original_file, modified_file)

    if snr is not None and psnr is not None:
        print(f"SNR (Signal-to-Noise Ratio): {snr:.2f} dB")
        print(f"PSNR (Peak Signal-to-Noise Ratio): {psnr:.2f} dB")
