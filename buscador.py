import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import vlc
import yt_dlp  # Asegúrate de instalar yt-dlp con `pip install yt-dlp`

def buscar_musica(query, max_results=10):
    # Permitir transporte inseguro (solo para pruebas locales)
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Configura los parámetros de la API
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_1077952959923-u48t2p2u3tcqb34i7s3e75j3h21nb4vv.apps.googleusercontent.com.json"

    # Define los permisos requeridos
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # Carga las credenciales y crea el cliente de la API
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes
    )
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials
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

        # Esperar a que el usuario cierre el reproductor
        input("Presiona Enter para detener la reproducción.")
        player.stop()
    except Exception as e:
        print(f"Error al reproducir el video: {e}")

if __name__ == "__main__":
    consulta = input("¿Qué música deseas buscar?: ")
    resultados = buscar_musica(consulta)

    for idx, resultado in enumerate(resultados, start=1):
        print(f"{idx}. {resultado['titulo']} - {resultado['url']}")

    opcion = int(input("Selecciona un video para reproducir (número): "))
    seleccion = resultados[opcion - 1]
    reproducir_video(seleccion["url"])
