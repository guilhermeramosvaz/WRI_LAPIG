import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 1. Connect to the geopackage database
gpkg_path = 'amostras_ilpf_inspecionadas_4326.gpkg'
conn = sqlite3.connect(gpkg_path)

# 2. Read the tipo_integ column
df = pd.read_sql_query("SELECT tipo_integ FROM amostras_ilpf_inspecionadas_4326", conn)
conn.close()

# 3. Clean up the data
# Strip whitespace and convert to string
df['tipo_integ'] = df['tipo_integ'].astype(str).str.strip()

# Map values to their classes
class_mapping = {
    '1': 'Pastagem',
    '2': 'Agricultura',
    '3': 'ILPF',
    '4': 'ILP',
    '5': 'IPF',
    '6': 'Agrofloresta',
    '7': 'ILF',
    '8': 'Outros'
}

color_mapping = {
    'Pastagem': '#eddc4b',
    'Agricultura': '#2fc912',
    'ILPF': '#3c4d0a',
    'ILP': '#b2f323',
    'IPF': '#f02907',
    'Agrofloresta': '#d67910',
    'ILF': '#bcb915',
    'Outros': '#000000'
}

# Value counts
counts = df['tipo_integ'].value_counts()

# Prepare a list of classes in order 1 to 8
classes_ordered = ['1', '2', '3', '4', '5', '6', '7', '8']
data_to_plot = []
for val in classes_ordered:
    class_name = class_mapping[val]
    count = counts.get(val, 0)
    data_to_plot.append({
        'val': val,
        'class': class_name,
        'count': count,
        'color': color_mapping[class_name]
    })

plot_df = pd.DataFrame(data_to_plot)

# 4. Plotting using Matplotlib with premium design
plt.figure(figsize=(10, 6))

# Custom styles
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']

# Create bars
bars = plt.bar(
    plot_df['class'],
    plot_df['count'],
    color=plot_df['color'],
    edgecolor='gray',
    linewidth=0.5,
    width=0.6,
    zorder=3
)

# Customize title and labels
plt.title('Distribuição de Amostras por Classe de Integração (tipo_integ)', fontsize=16, fontweight='bold', pad=20, color='#333333')
plt.xlabel('Classe de Integração', fontsize=12, labelpad=10, fontweight='semibold', color='#555555')
plt.ylabel('Número de Amostras', fontsize=12, labelpad=10, fontweight='semibold', color='#555555')

# Add values on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2.0,
        height + (max(plot_df['count']) * 0.01) if height > 0 else 2,
        f'{int(height)}',
        ha='center',
        va='bottom',
        fontsize=10,
        fontweight='bold',
        color='#333333',
        zorder=4
    )

# Add grid lines (horizontal only, behind bars)
plt.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
plt.gca().set_axisbelow(True)

# Adjust y-axis limit to leave space for labels
plt.ylim(0, max(plot_df['count']) * 1.1)

# Remove top and right spines
for spine in ['top', 'right']:
    plt.gca().spines[spine].set_visible(False)

# Adjust layout and save
plt.tight_layout()
plt.savefig('grafico_tipo_integracao.png', dpi=300)
print("Graph saved successfully as 'grafico_tipo_integracao.png'")
