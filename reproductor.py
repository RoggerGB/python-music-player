import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
import vlc
import yt_dlp

# Archivo donde se guardarán las credenciales
TOKEN_FILE = "token.json"
CLIENT_SECRETS_FILE = "client_secret.json"

def cargar_credenciales():
    """Carga las credenciales desde un archivo local, o solicita nuevas si no existen."""
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    credentials = None
    if os.path.exists(TOKEN_FILE):
        # Intenta cargar las credenciales desde el archivo
        with open(TOKEN_FILE, "r") as token:
            creds_data = json.load(token)
            credentials = Credentials.from_authorized_user_info(creds_data, scopes)

    # Si no hay credenciales válidas, solicita nuevas
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            # Intenta renovar las credenciales si han expirado
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            # Solicita nuevas credenciales y guarda en el archivo
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, scopes
            )
            credentials = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "w") as token:
                token.write(credentials.to_json())

    return credentials

def buscar_musica(query, max_results=10):
    """Busca música en YouTube utilizando la API."""
    credentials = cargar_credenciales()
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials
    )

    # Realizar la búsqueda
    request = youtube.search().list(
        part="snippet",
        maxResults=max_results,
        q=query,
        type="video",  # Solo busca videos
        videoCategoryId="10",  # Categoría 10 es para música
    )
    response = request.execute()

    # Procesar y devolver los resultados
    resultados = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        titulo = item["snippet"]["title"]
        canal = item["snippet"]["channelTitle"]
        resultados.append({
            "titulo": titulo,
            "canal": canal,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })

    return resultados

def obtener_url_stream(url):
    """Usa yt-dlp para obtener la URL del stream."""
    ydl_opts = {
        'format': 'bestaudio/best',  # Obtén la mejor calidad de audio
        'quiet': True  # Silenciar los logs de yt-dlp
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        stream_url = info_dict['url']
    return stream_url

def reproducir_video(url):
    """Reproduce un video en VLC usando yt-dlp para obtener el stream."""
    try:
        stream_url = obtener_url_stream(url)
        print(f"Reproduciendo: {stream_url}")
        instancia = vlc.Instance()
        player = instancia.media_player_new()
        media = instancia.media_new(stream_url)
        player.set_media(media)
        player.play()

        input("Presiona Enter para detener la reproducción.")
        player.stop()
    except Exception as e:
        print(f"Error al reproducir el video: {e}")

if __name__ == "__main__":
    while(True):
        consulta = input("¿Qué música deseas buscar?: ")
        resultados = buscar_musica(consulta)

        for idx, resultado in enumerate(resultados, start=1):
            print(f"{idx}. {resultado['titulo']} - {resultado['url']}")

        opcion = int(input("Selecciona un video para reproducir (número): "))
        seleccion = resultados[opcion - 1]
        reproducir_video(seleccion["url"])
