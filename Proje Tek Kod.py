from pytube import YouTube
from PIL import Image
from io import BytesIO
import requests
import cv2, os
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip


def download_thumbnail(youtube_url, filename="photo.png", resolution=(1366, 768)):                     #Resim Oluşturma
    try:
        # YouTube videosunu indir
        youtube = YouTube(youtube_url)
        thumbnail_url = youtube.thumbnail_url

        # Resmi indir
        response = requests.get(thumbnail_url)
        img = Image.open(BytesIO(response.content))

        # Resmi istenen çözünürlüğe boyutlandır
        img_resized = img.resize(resolution)

        # Resmi kaydet
        img_resized.save(filename)

        print(f"Thumbnail başarıyla indirildi ve kaydedildi: {filename}")

    except Exception as e:
        print(f"Hata: {e}")

def indir(youtube_linki):                                                                              #Youtube Videosunu İndirme
    try:
        # YouTube videosunu indir
        video = YouTube(youtube_linki)
        video.streams.filter(file_extension='mp4').first().download()
        video_uzunlugu = video.length

        print("Video başarıyla indirildi.")
        return video_uzunlugu
    except Exception as e:
        print(f"Hata: {e}")

def video_olustur(video_adi, arka_plan_resim, uzunluk_saniye, genislik=1366, yukseklik=768, fps=15):    #Arkaplanlı Video Oluşturma
    # VideoWriter objesi oluştur
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Video codec'i
    video = cv2.VideoWriter(video_adi, fourcc, fps, (genislik, yukseklik))

    # Arka plan resmini yükle ve boyutlandır
    arka_plan = cv2.imread(arka_plan_resim)
    arka_plan = cv2.resize(arka_plan, (genislik, yukseklik))

    # Videoyu oluştur
    for _ in tqdm(range(int(fps * uzunluk_saniye)), desc="Video Oluşturuluyor"):
        video.write(arka_plan)

    # Videoyu kapat
    video.release()
    
def altyazi_indir(video_url, dosya_adi="altyazi.txt"):                                                  #Altyazı Dosyasını İndirme
    try:
        # YouTube video ID'sini çıkarma
        video_id = video_url.split("v=")[1]

        # Altyazıları çekme
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Altyazıları dosyaya yazma
        with open(dosya_adi, "w", encoding="utf-8") as file:
            for entry in transcript:
                file.write(f"{entry['start']} - {entry['start'] + entry['duration']}: {entry['text']}\n")

        print(f"Altyazılar başarıyla kaydedildi. Dosya adı: {dosya_adi}")
    except Exception as e:
        print(f"Hata: {e}")
        
        
def altyazi_duzenle(girdi_dosya="altyazi.txt", cikti_dosya="subtitle.txt"):                             #Altyazı Dosyasını Düzenleme
    with open(girdi_dosya, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    modified_lines = []

    for i, line in enumerate(lines):
        if "-" not in line:
            # Eğer "-" ibaresi yoksa, bir önceki satırın sonuna ekle
            modified_lines[-1] = modified_lines[-1].rstrip('\n') + ' ' + line.lstrip()
        else:
            modified_lines.append(line)

    # Düzenlenmiş satırları yazdır veya başka bir dosyaya kaydet
    with open(cikti_dosya, 'w', encoding='utf-8') as output_file:
        for line in modified_lines:
            output_file.write(line)
            
            
def altyazi_ekle_ve_kaydet(video_adi="Videonuz.mp4", altyazi_dosya="subtitle.txt", cikti_adi="video_altyazi.mp4", font_size=24, bg_color='black', text_color='white', fps=15):
    # Videoyu yükle
    video = VideoFileClip(video_adi)

    # "subtitle.txt" dosyasını oku ve altyazi_dizisi listesine ekle
    with open(altyazi_dosya, 'r', encoding='utf-8') as file:
        altyazi_dizisi = file.readlines()

    # Altyazıları içeren liste
    altyazi_clips = []

    # Videoya altyazıları ekleyerek birleştir
    for altyazi_satiri in altyazi_dizisi:
        # Satırı süre ve altyazı olarak ayır
        zaman_altyazi = altyazi_satiri.split(':')

        # Zaman bilgisini ayır ve float'a çevir
        zaman = [float(z) for z in zaman_altyazi[0].replace(' ', '').split('-')]

        # Altyazı metnini belirlenen süre aralığına yerleştir
        altyazi_clip = TextClip(zaman_altyazi[1].strip(), fontsize=font_size, color=text_color, bg_color=bg_color, size=(video.size[0], 50))
        altyazi_clip = altyazi_clip.set_position(('center', 'bottom')).set_start(zaman[0]).set_end(zaman[1])

        # Altyazıyı listeye ekle
        altyazi_clips.append(altyazi_clip)

    # Videoya altyazıları ekleyerek birleştir
    video = CompositeVideoClip([video] + altyazi_clips)

    # Çıkış dosyasını kaydet
    video.write_videofile(cikti_adi, codec='libx264', audio_codec='aac', fps=fps)
    

def video_ismi(video_url):
    try:
        # YouTube videosunu al
        video = YouTube(video_url)

        # Video başlığını döndür
        return video.title + ".mp4"
    except Exception as e:
        print(f"Hata: {e}")
        return None


def mp4_to_wav(input_mp4, output_wav="Output.wav"):
    video_clip = VideoFileClip(input_mp4)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(output_wav, codec='pcm_s16le', ffmpeg_params=["-ac", "2"])


def add_audio_to_video(video_path="video_altyazi.mp4", audio_path="Output.wav", output_path="final.mp4"):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    
    # Videoya ses eklemek
    video_clip = video_clip.set_audio(audio_clip)

    # Yeni videoyu kaydetmek
    video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')


def silme(dosyalar):
    for dosya in dosyalar:
        try:
            os.remove(dosya)
            print(f"{dosya} başarıyla silindi.")
        except FileNotFoundError:
            print(f"{dosya} bulunamadı.")
        except Exception as e:
            print(f"{dosya} silinirken bir hata oluştu: {e}")


# Kullanım örneği
video_url = "https://www.youtube.com/watch?v=7wtfhZwyrcc"  # Kullanıcıdan input video linki

#Metotların Çağrılması

download_thumbnail(video_url)   #RESİM İNDİRME
indir(video_url)                #Video İndirme
video_olustur("Videonuz.mp4", "photo.png", indir(video_url))
altyazi_indir(video_url)
altyazi_duzenle()
altyazi_ekle_ve_kaydet()
isim = video_ismi(video_url)
str(isim)
mp4_to_wav(isim)
add_audio_to_video()
silme("altyazi.txt", "photo.png", "subtitle.txt", "video_altyazi.mp4","Output.wav", "Videonuz.mp4", isim)


