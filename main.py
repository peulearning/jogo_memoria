import os
import pickle
import random
from PySimpleGUI import Window, Button, Column, Image, Text, Input, Checkbox
from PIL import Image as PILImage, ImageTk, UnidentifiedImageError
from io import BytesIO
from scraping import obter_caminhos_imagens, realizar_scraping_e_baixar_imagens

def criar_layout_selecao_jogadores():
    layout = [
        [Text('Seleção de Jogadores')],
        [Checkbox('Servidor', key='-SERVIDOR-'), Input(key='-ENDERECO-SERVIDOR-', size=(15, 1), disabled=True)],
        [Checkbox('Cliente', key='-CLIENTE-'), Input(key='-ENDERECO-CLIENTE-', size=(15, 1), disabled=True)],
        [Button('Iniciar Jogo', key='-INICIAR-JOGO-')]
    ]
    return layout

def exibir_espera_download():
    print("O Scraper está INICIANDO... AGUARDE")

def obter_endereco_ip_servidor():
    ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
    print(f"Endereço IP do Servidor: {ip}")
    return ip

def main_selecao_jogadores():
    exibir_espera_download()

    # Realizar scraping e baixar imagens
    realizar_scraping_e_baixar_imagens()

    if not os.path.exists('pokemons_img'):
        os.makedirs('pokemons_img')

    layout_selecao_jogadores = criar_layout_selecao_jogadores()
    window_selecao_jogadores = Window('Seleção de Jogadores', layout=layout_selecao_jogadores, resizable=True)
    janela_aberta = True

    try:
        while janela_aberta:
            event_selecao_jogadores, values_selecao_jogadores = window_selecao_jogadores.read()

            if event_selecao_jogadores == 'EXIT':
                janela_aberta = False
                break

            if values_selecao_jogadores and values_selecao_jogadores['-SERVIDOR-']:
                window_selecao_jogadores['-ENDERECO-SERVIDOR-'].update(disabled=False, value=obter_endereco_ip_servidor())
            else:
                window_selecao_jogadores['-ENDERECO-SERVIDOR-'].update(disabled=True, value='')

            if values_selecao_jogadores and values_selecao_jogadores['-CLIENTE-']:
                window_selecao_jogadores['-ENDERECO-CLIENTE-'].update(disabled=False)
            else:
                window_selecao_jogadores['-ENDERECO-CLIENTE-'].update(disabled=True, value='')

            if event_selecao_jogadores == '-INICIAR-JOGO-':
                endereco_ip_servidor = window_selecao_jogadores['-ENDERECO-SERVIDOR-'].get() if values_selecao_jogadores.get('-SERVIDOR-') else None
                endereco_ip_cliente = window_selecao_jogadores['-ENDERECO-CLIENTE-'].get() if values_selecao_jogadores.get('-CLIENTE-') else None

                janela_aberta = False
                window_selecao_jogadores.close()
                main_jogo(endereco_ip_servidor, endereco_ip_cliente)

    except Exception as e:
        # Tratamento para quando a janela é fechada
        print(f"Erro durante a execução: {e}")

    finally:
        window_selecao_jogadores.close()

def criar_layout_jogo(image_paths, endereco_ip_servidor, endereco_ip_cliente):
    # Seleciona aleatoriamente 8 imagens de Pokémons para formar pares
    random.shuffle(image_paths)
    image_paths = image_paths[:8] * 2

    layout_grid = [
        [Button(f'{i * 4 + j}', key=i * 4 + j, size=(4, 2), image_filename='', image_size=(100, 100), pad=(5, 5)) for j in range(1, 5)]
        for i in range(4)
    ]

    layout_imagens = [
        [Image(filename='', key='-IMAGEM1-', size=(100, 100)), Image(filename='', key='-IMAGEM2-', size=(100, 100))]
    ]

    if endereco_ip_servidor:
        layout_servidor_cliente = [
            [Text(f'Servidor: {endereco_ip_servidor}')],
            [Text(f'Cliente: {endereco_ip_cliente}')]
        ]
    else:
        layout_servidor_cliente = [
            [Text('Servidor:')],
            [Text('Cliente:'), Text('', key='-ENDERECO-')]
        ]

    layout = [
        [Column(layout_servidor_cliente), Column(layout_grid), Column(layout_imagens)]
    ]

    return layout

def main_jogo(endereco_ip_servidor, endereco_ip_cliente):
    image_paths = obter_caminhos_imagens()

    if not image_paths:
        print("Erro: Não foi possível carregar os caminhos das imagens.")
        return

    layout_jogo = criar_layout_jogo(image_paths, endereco_ip_servidor, endereco_ip_cliente)
    window_jogo = Window('Sua Memória e Boa ?', layout=layout_jogo, resizable=True)
    janela_aberta = True

    is_servidor = endereco_ip_servidor is not None
    endereco_ip = endereco_ip_servidor if is_servidor else endereco_ip_cliente

    imagem_selecionada = None
    imagem1_key = '-IMAGEM1-'
    imagem2_key = '-IMAGEM2-'

    pontuacao_cliente = 0
    pontuacao_servidor = 0

    try:
        while janela_aberta:
            event_jogo, values_jogo = window_jogo.read()

            if event_jogo in (None, 'EXIT'):
                janela_aberta = False
                break

            if event_jogo in range(1, 17):
                if imagem_selecionada is None:
                    imagem_selecionada = event_jogo
                    imagem_path = image_paths[event_jogo - 1]
                    try:
                        with open(imagem_path, 'rb') as img_file:
                            PILImage.open(img_file).verify()
                        image_data = BytesIO()
                        PILImage.open(imagem_path).resize((100, 100)).save(image_data, format="PNG")
                        window_jogo[imagem1_key].update(data=image_data.getvalue())
                    except (UnidentifiedImageError, IOError) as e:
                        print(f"Erro ao abrir a imagem {imagem_path}: {e}")
                else:
                    imagem_path = image_paths[event_jogo - 1]
                    try:
                        with open(imagem_path, 'rb') as img_file:
                            PILImage.open(img_file).verify()
                        image_data = BytesIO()
                        PILImage.open(imagem_path).resize((100, 100)).save(image_data, format="PNG")
                        window_jogo[imagem2_key].update(data=image_data.getvalue())
                    except (UnidentifiedImageError, IOError) as e:
                        print(f"Erro ao abrir a imagem {imagem_path}: {e}")

                    if imagem_selecionada is not None and image_paths[event_jogo - 1] == image_paths[imagem_selecionada - 1]:
                        if is_servidor:
                            pontuacao_servidor += 1
                        else:
                            pontuacao_cliente += 1

                        print(f"\nPontuação: Cliente {pontuacao_cliente} - {pontuacao_servidor} Servidor")

                        window_jogo[event_jogo].update(disabled=True)
                        window_jogo[imagem_selecionada].update(disabled=True)

                        imagem_selecionada = None

                    else:
                        print("\nErrou! As imagens não são iguais.")
                        window_jogo[imagem1_key].update(data=b'')
                        window_jogo[imagem2_key].update(data=b'')
                        imagem_selecionada = None

    except Exception as e:
        # Tratamento para quando a janela é fechada
        print(f"Erro durante a execução: {e}")

    finally:
        window_jogo.close()

if __name__ == "__main__":
    main_selecao_jogadores()
