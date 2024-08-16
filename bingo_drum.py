import random
import pygame
import threading
import time
import requests
import os

# pygameを初期化
pygame.init()
pygame.mixer.init()

# ロックを作成
audio_lock = threading.Lock()
current_audio_thread = None
# current_audio_thread というグローバル変数を導入し、現在再生中の音声スレッドを追跡します。

def bingo():
    """
    オープンキャンパス用ビンゴゲーム

    Enterキーを押すたびに、1から18までの数字からランダムに当選番号を選び、
    それまでの当選番号と合わせて表示します。
    """
    # URLとローカルファイル名を指定: https://github.com/okana2ki/intro-to-DS/blob/main/drum_roll.mp3
    url = 'https://raw.githubusercontent.com/okana2ki/intro-to-DS/main/drum_roll.mp3'
    local_filename = "local_drum_roll.mp3"

    # ファイルをダウンロードしてローカルに保存
    # response = requests.get(url)
    # with open(local_filename, 'wb') as file:
        # file.write(response.content)
    response = requests.get(url, stream=True)
    with open(local_filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    numbers = list(range(1, 19))  # 1から18までの数字のリスト
    drawn_numbers = []  # 当選番号を記録するリスト
    remaining_numbers = numbers

    while remaining_numbers:
        input("Enterキーを押して次の当選番号を選んでね！")

        try:
            # Enterが押されたら、前のドラム再生を停止し、新しいドラム再生を開始
            stop_current_audio()  # 現在再生中の音声を停止; 前の音声再生が終わってなくても新しい音声再生を即座に開始できるよう。
            play_mp3_with_timer(local_filename, 3.5)
            # 3.5秒経ったら（シンバル音の後）当選番号を発表；音声再生は最後まで続く       
        except Exception as e:
            print(f"音声再生エラー: {e}")

        # まだ選ばれていない数字からランダムに選ぶ
        drawn_number = random.choice(remaining_numbers)
        drawn_numbers.append(drawn_number)
        remaining_numbers.remove(drawn_number)

        print("当選番号:", drawn_number)
        print("これまでの当選番号:", drawn_numbers)

    print("すべての番号が出ました！ビンゴゲーム終了！")
    # ドラム再生が終わるころまでメインプログラムの終了を遅らせる（2秒待機）
    time.sleep(2)

def play_mp3(file_path):
    try:
        with audio_lock:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # 音楽の再生が終わるまで待機
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
    except pygame.error as e:
        print(f"音声再生エラー: {e}")

def play_mp3_with_timer(file_path, wait_time):
    global current_audio_thread  # グローバル変数を関数内で使うために宣言
    # 音声再生を別スレッドで開始; 音声再生スレッドを current_audio_thread に割り当てる
    current_audio_thread = threading.Thread(target=play_mp3, args=(file_path,))
    current_audio_thread.start()
    
    # 指定時間待機
    time.sleep(wait_time)

def stop_current_audio():  # 現在再生中の音声を停止し、そのスレッドの終了を待ちます。
    global current_audio_thread  # グローバル変数を関数内で使うために宣言
    if current_audio_thread and current_audio_thread.is_alive():
        pygame.mixer.music.stop()
        current_audio_thread.join(timeout=1)  # 最大1秒待機

# メインプログラム
if __name__ == '__main__':
    try:
        bingo()
    finally:
        stop_current_audio()  # プログラム終了時に音声再生を停止
        pygame.quit()