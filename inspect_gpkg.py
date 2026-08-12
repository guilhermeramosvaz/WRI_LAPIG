import sqlite3
import struct
import json

conn = sqlite3.connect('documentos_de_base/visual/amostras_ilpf_inspecionadas_4326.gpkg')
cursor = conn.cursor()

def parse_gpkg_geometry(blob):
    if blob is None:
        return None, None
    magic = blob[0:2]
    if magic != b'GP':
        return None, None
    flags = blob[3]
    envelope_type = (flags >> 1) & 0x07
    byte_order = flags & 0x01
    bo = '<' if byte_order == 1 else '>'
    offset = 8
    if envelope_type == 1:
        env = struct.unpack(bo + '4d', blob[offset:offset+32])
        return (env[0] + env[1]) / 2, (env[2] + env[3]) / 2
    elif envelope_type in (2, 3):
        env = struct.unpack(bo + '6d', blob[offset:offset+48])
        return (env[0] + env[1]) / 2, (env[2] + env[3]) / 2
    elif envelope_type == 4:
        env = struct.unpack(bo + '8d', blob[offset:offset+64])
        return (env[0] + env[1]) / 2, (env[2] + env[3]) / 2
    return None, None

tipo_integ_map = {
    '1': 'Pastagem',
    '2': 'Agricultura',
    '3': 'ILPF',
    '4': 'ILP',
    '5': 'IPF',
    '7': 'ILF',
    '8': 'Outros',
    '0': 'Agrofloresta'
}

cursor.execute("""SELECT fid, IDs, geom, tipo_integ, glebe_name, area_ha, tipo_amostra, cropYear
    FROM amostras_ilpf_inspecionadas_4326""")

features = []
for row in cursor.fetchall():
    fid, ids, geom, tipo_integ, glebe_name, area_ha, tipo_amostra, cropYear = row
    lng, lat = parse_gpkg_geometry(geom)
    if lng is not None and lat is not None:
        ti = str(tipo_integ).strip() if tipo_integ else 'N/A'
        classe = tipo_integ_map.get(ti, 'Outros')
        features.append({
            'fid': fid,
            'id': ids if ids is not None else fid,
            'lng': round(lng, 6),
            'lat': round(lat, 6),
            'classe': classe,
            'nome': glebe_name if glebe_name else '',
            'area': round(area_ha, 2) if area_ha else 0,
            'ano': cropYear if cropYear else ''
        })

conn.close()

with open('assets/amostras_data.json', 'w', encoding='utf-8') as f:
    json.dump(features, f, ensure_ascii=False)
print(f"Saved {len(features)} features to assets/amostras_data.json")

# Checando sobreposicoes exatas
coords = {}
for f in features:
    coord = (f['lat'], f['lng'])
    if coord not in coords:
        coords[coord] = []
    coords[coord].append(f)

sobrepostos = {k: v for k, v in coords.items() if len(v) > 1}
print(f"Total de pontos únicos: {len(coords)}")
print(f"Total de coordenadas com mais de 1 amostra: {len(sobrepostos)}")
for k, v in list(sobrepostos.items())[:5]:
    print(f"Coord {k} tem {len(v)} pontos: {[p['classe'] for p in v]}")
