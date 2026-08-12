import re

file_path = r"c:\Users\windows\Documents\github\WRI_LAPIG\index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update colors
new_colors = """    :root {
      --color-bg: #ffffff;
      --color-fg: #1a1a1a;
      --color-muted: #6b6b6b;
      --color-rule: #e5e5e5;
      --color-accent: #129912;
      --color-accent-soft: #33a633;
      --color-accent-glow: rgba(18, 153, 18, 0.08);
      --color-yellow: #ffd700;"""
content = re.sub(r'    :root \{.*?--color-accent-glow: rgba\(45, 106, 63, 0\.08\);', new_colors, content, flags=re.DOTALL)

# 2. Add Leaflet Side-by-Side script
script_tag = """  <!-- Leaflet Side-by-Side -->
  <script src="https://cdn.jsdelivr.net/gh/digidem/leaflet-side-by-side/leaflet-side-by-side.min.js"></script>"""
content = content.replace('  <!-- Chart.js -->', script_tag + '\n  <!-- Chart.js -->')

# 3. Add CSS for Split Map
css_add = """    /* ──────────────────────────────────────────────────────────
       SPLIT MAP & DASHBOARDS
    ────────────────────────────────────────────────────────── */
    .split-map-wrapper {
      position: relative;
      height: 400px;
      border-radius: var(--radius);
      overflow: hidden;
      border: 1px solid var(--color-rule);
      box-shadow: var(--shadow-md);
      margin-bottom: 1.5rem;
    }
    #split-map {
      width: 100%;
      height: 100%;
      z-index: 1;
    }
    .split-dashboards {
      display: flex;
      gap: 1.5rem;
    }
    .split-dashboard {
      flex: 1;
      background: var(--color-card-bg);
      border: 1px solid var(--color-rule);
      border-radius: var(--radius);
      padding: 1rem;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
    }
    .dashboard-title {
      font-size: 0.9rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--color-accent);
      text-align: center;
    }
    .dashboard-legend {
      display: flex;
      justify-content: center;
      gap: 1rem;
      font-size: 0.75rem;
      flex-wrap: wrap;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }
    .legend-color {
      width: 12px;
      height: 12px;
      border-radius: 2px;
      border: 1px solid rgba(0,0,0,0.1);
    }
    .dashboard-chart {
      position: relative;
      width: 100%;
      height: 150px;
    }
    
    @media (max-width: 800px) {
      .split-dashboards {
        flex-direction: column;
      }
    }
</style>"""
content = content.replace('</style>', css_add)

# 4. Add HTML Section
html_add = """  <!-- ═══════════════════════════════════════════════════════
       COMPARAÇÃO DE MAPAS (SPLIT PANEL)
  ═══════════════════════════════════════════════════════ -->
  <section class="section reveal" id="comparacao">
    <div class="section__eyebrow">Análise Comparativa</div>
    <h2 class="section__title">Comparação de Cenários (Raster)</h2>
    <p class="section__desc">Arraste o divisor para comparar as camadas lado a lado sobre o mapa base.</p>

    <div class="split-map-wrapper">
      <div id="split-map"></div>
    </div>
    
    <div class="split-dashboards">
      <!-- Lado Esquerdo -->
      <div class="split-dashboard left-dashboard">
        <h3 class="dashboard-title">Cenário A (Esquerda)</h3>
        <div class="dashboard-legend">
          <div class="legend-item"><span class="legend-color" style="background:#129912"></span> Floresta</div>
          <div class="legend-item"><span class="legend-color" style="background:#ffd700"></span> Pastagem</div>
        </div>
        <div class="dashboard-chart">
          <canvas id="chart-left"></canvas>
        </div>
      </div>
      
      <!-- Lado Direito -->
      <div class="split-dashboard right-dashboard">
        <h3 class="dashboard-title">Cenário B (Direita)</h3>
        <div class="dashboard-legend">
          <div class="legend-item"><span class="legend-color" style="background:#129912"></span> Floresta</div>
          <div class="legend-item"><span class="legend-color" style="background:#ffd700"></span> Pastagem</div>
        </div>
        <div class="dashboard-chart">
          <canvas id="chart-right"></canvas>
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════
       DELIVERABLES"""
content = content.replace('  <!-- ═══════════════════════════════════════════════════════\n       DELIVERABLES', html_add)

# 5. Add JS for Split Map and Charts at the end of the script block
js_add = """    // ──────────────────────────────────────────────────────────
    //  SPLIT MAP & CHARTS LOGIC
    // ──────────────────────────────────────────────────────────
    (function () {
      'use strict';
      
      const splitMap = L.map('split-map', {
        center: [-15.0, -49.0],
        zoom: 5,
        zoomControl: true,
        scrollWheelZoom: false
      });
      
      // 1. Basemap comum (Fundo) igual ao mapa superior
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(splitMap);
      
      // 2. Camadas Raster para Comparação (Dummies)
      // Ajustando opacidade para que o mapa base fique visível
      const leftLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        opacity: 0.6,
        attribution: 'Cenário A'
      }).addTo(splitMap);
      
      const rightLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        opacity: 0.6,
        attribution: 'Cenário B'
      }).addTo(splitMap);
      
      // Add Side-by-Side control
      L.control.sideBySide(leftLayer, rightLayer).addTo(splitMap);
      
      // Setup Charts
      const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.parsed.y + '%';
              }
            }
          }
        },
        scales: {
          y: { 
            beginAtZero: true, 
            max: 100,
            grid: { color: 'rgba(0,0,0,0.05)' },
            ticks: { font: { size: 10 } }
          },
          x: { 
            grid: { display: false },
            ticks: { font: { size: 10 } }
          }
        }
      };
      
      const ctxLeft = document.getElementById('chart-left').getContext('2d');
      new Chart(ctxLeft, {
        type: 'bar',
        data: {
          labels: ['Floresta', 'Pastagem', 'Outros'],
          datasets: [{
            data: [65, 25, 10],
            backgroundColor: ['#129912', '#ffd700', '#aaaaaa'],
            borderRadius: 4
          }]
        },
        options: commonOptions
      });
      
      const ctxRight = document.getElementById('chart-right').getContext('2d');
      new Chart(ctxRight, {
        type: 'bar',
        data: {
          labels: ['Floresta', 'Pastagem', 'Outros'],
          datasets: [{
            data: [40, 50, 10],
            backgroundColor: ['#129912', '#ffd700', '#aaaaaa'],
            borderRadius: 4
          }]
        },
        options: commonOptions
      });
      
    })();
  </script>
</body>"""

content = content.replace('  </script>\n</body>', js_add)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Update complete")
