import pandas as pd
import numpy as np

# Carregando o conjunto de dados
file_path = 'dataset.csv'
df = pd.read_csv(file_path)

# Exibindo as primeiras linhas do conjunto de dados para inspeção
df.head()

# Definindo o tamanho da janela de observações[ ]
[6]

window_size = 300

# Calculando o número de janelas possíveis
num_windows = len(df) // window_size

# Inicializando listas para armazenar as métricas calculadas
mean_list = []
std_dev_list = []

# Loop para calcular as métricas para cada janela de observação
for i in range(num_windows):
    start_idx = i * window_size
    end_idx = start_idx + window_size
    window_data = df['disponibilidade em %'][start_idx:end_idx]

    # Calculando a média e o desvio padrão
    mean_value = np.mean(window_data)
    std_dev_value = np.std(window_data)

    # Armazenando os resultados nas listas
    mean_list.append(mean_value)
    std_dev_list.append(std_dev_value)

# Exibindo as métricas calculadas para as primeiras 5 janelas como um exemplo
mean_list[:5], std_dev_list[:5]

# Definindo o valor de k
k = 1.5

# Calculando os limites de controle para cada janela
lci_list = [mu - k * sigma for mu, sigma in zip(mean_list, std_dev_list)]
lcs_list = [mu + k * sigma for mu, sigma in zip(mean_list, std_dev_list)]

# Restringindo os limites de controle para estarem entre 0 e 100
lci_list = [max(0, min(100, lci)) for lci in lci_list]
lcs_list = [max(0, min(100, lcs)) for lcs in lcs_list]

# Exibindo os limites de controle calculados para as primeiras 5 janelas como um exemplo
lci_list[:5], lcs_list[:5]

# Definindo o limiar de histerese (número de observações consecutivas para confirmar o alerta)
hysteresis_threshold = 5

# Inicializando variáveis para monitoramento
current_state = "Normal"
consecutive_count = 0

# Lista para armazenar o estado do sistema para cada janela de observação
state_list = []

# Loop para monitoramento
for i in range(num_windows):
    start_idx = i * window_size
    end_idx = start_idx + window_size
    window_data = df['disponibilidade em %'][start_idx:end_idx]

    lci = lci_list[i]
    lcs = lcs_list[i]

    # Verificando se os valores da janela estão fora dos limites de controle
    out_of_bounds_count = sum((window_data < lci) | (window_data > lcs))

    if out_of_bounds_count >= hysteresis_threshold:
        # Um alerta é gerado, mas só é confirmado se continuar por 'hysteresis_threshold' observações
        new_state = "Alerta de Carga Alta" if np.mean(window_data) > lcs else "Alerta de Carga Baixa"

        # Verificando se o estado mudou
        if new_state != current_state:
            consecutive_count += 1
            if consecutive_count >= hysteresis_threshold:
                current_state = new_state
                consecutive_count = 0  # Resetando o contador
        else:
            consecutive_count = 0  # Resetando o contador se voltou ao estado normal
    else:
        new_state = "Normal"

        # Verificando se o estado mudou para normal
        if new_state != current_state:
            consecutive_count += 1
            if consecutive_count >= hysteresis_threshold:
                current_state = new_state
                consecutive_count = 0  # Resetando o contador
        else:
            consecutive_count = 0  # Resetando o contador se permaneceu no estado normal

    state_list.append(current_state)

# Exibindo o estado do sistema para as primeiras 5 janelas como um exemplo
state_list[:5]
