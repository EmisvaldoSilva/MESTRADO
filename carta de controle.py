
import pandas as pd
import numpy as np

# Função para monitorar a disponibilidade de CPU utilizando carta de controle
def monitor_cpu_availability(df, window_size=300, k=1.5, hysteresis_threshold=5):
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

    # Calculando os limites de controle para cada janela
    lci_list = [max(0, min(100, mu - k * sigma)) for mu, sigma in zip(mean_list, std_dev_list)]
    lcs_list = [max(0, min(100, mu + k * sigma)) for mu, sigma in zip(mean_list, std_dev_list)]

    # Inicializando variáveis para monitoramento
    current_state = "Normal"
    new_approach_state_list = []
    
    # Inicializando DataFrame para armazenar alertas
    alert_df = pd.DataFrame(columns=['Window', 'Alert_Type'])

    # Loop para monitoramento utilizando os limites de controle da janela anterior
    for i in range(1, num_windows):  # Começando de 1 para que possamos usar a janela 0 como referência inicial
        start_idx = i * window_size
        end_idx = start_idx + window_size
        window_data = df['disponibilidade em %'][start_idx:end_idx]

        # Usando os limites de controle da janela anterior (i-1)
        lci = lci_list[i-1]
        lcs = lcs_list[i-1]

        # Verificando se os valores da janela estão fora dos limites de controle
        out_of_bounds_count = sum((window_data < lci) | (window_data > lcs))

        # Um alerta é gerado se os valores estão fora dos limites
        new_state = "Normal"
        if np.mean(window_data) > lcs:
            new_state = "Alerta de Carga Alta"
        elif np.mean(window_data) < lci:
            new_state = "Alerta de Carga Baixa"

        # Verificando se o estado mudou
        if new_state != current_state:
            current_state = new_state
            # Salvando o alerta no DataFrame usando pandas.concat
            new_row = pd.DataFrame({'Window': [i], 'Alert_Type': [new_state]})
            alert_df = pd.concat([alert_df, new_row], ignore_index=True)

        new_approach_state_list.append(current_state)

    # Resultados
    state_counts = pd.Series(new_approach_state_list).value_counts()
    return state_counts, alert_df

# Exemplo de uso
df = pd.read_csv('cpu_usage_data_varying.csv')
state_counts, alert_df = monitor_cpu_availability(df)
print("Contagem de Estados:", state_counts)
print("Alertas:", alert_df)