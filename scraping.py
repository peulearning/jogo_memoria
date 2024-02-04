import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pickle
from concurrent.futures import ThreadPoolExecutor

def baixar_imagens():
    # Crie um diretório para salvar as imagens
    if not os.path.exists('pokemons_img'):
        os.makedirs('pokemons_img')
        url = 'https://pokemondb.net/pokedex/shiny'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

        try:
            resposta = requests.get(url, headers=headers)
            resposta.raise_for_status()  # Verifica se houve um erro na requisição HTTP

            bs = BeautifulSoup(resposta.text, 'html.parser')

            # Encontrar todos os links <img> com a classe "shinydex-sprite-shiny"
            imagens = bs.find_all('img', class_='shinydex-sprite-shiny')

            # Lista para armazenar os caminhos das imagens
            image_paths = []

            # Função para baixar uma imagem e adicionar à lista
            def baixar_e_adicionar(img_tag):
                caminho = img_tag['src']
                img_url = urljoin(url, caminho)
                local_path = os.path.join('pokemons_img', os.path.basename(img_url))

                with open(local_path, 'wb') as img_file:
                    img_data = requests.get(img_url).content
                    img_file.write(img_data)

                # Adicionar o caminho da imagem à lista
                image_paths.append(local_path)

            # Usar ThreadPoolExecutor para baixar imagens de forma concorrente
            with ThreadPoolExecutor() as executor:
                executor.map(baixar_e_adicionar, imagens)

            # Verificar se foram baixadas imagens
            if not image_paths:
                print("Erro: Não foi possível encontrar imagens de Pokémons.")
                return None

            # Criar o diretório 'pokemons' se não existir
            if not os.path.exists('pokemons'):
                os.makedirs('pokemons')

            # Salvar os caminhos das imagens em um arquivo pickle
            with open(os.path.join('pokemons', 'image_paths.pkl'), 'wb') as file:
                pickle.dump(image_paths, file)

            return image_paths

        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar o site: {e}")
            return None


def obter_caminhos_imagens():
    image_paths_file = os.path.join('pokemons', 'image_paths.pkl')

    if os.path.exists(image_paths_file):
        with open(image_paths_file, 'rb') as file:
            image_paths = pickle.load(file)
            return image_paths

    return None

def realizar_scraping_e_baixar_imagens():
    image_paths = baixar_imagens()
    return image_paths

if __name__ == "__main__":
    image_paths = realizar_scraping_e_baixar_imagens()