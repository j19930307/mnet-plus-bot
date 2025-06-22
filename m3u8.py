import subprocess


def download_m3u8_to_mp4(m3u8_url: str, output_path: str):
    command = [
        'ffmpeg',
        '-i', m3u8_url,
        '-c', 'copy',  # 直接複製 codec，不重新編碼
        '-bsf:a', 'aac_adtstoasc',  # 修正音訊格式
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print("下載完成:", output_path)
        return output_path
    except subprocess.CalledProcessError as e:
        print("下載失敗:", e)
        return None
