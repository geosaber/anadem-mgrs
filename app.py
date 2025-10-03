import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="Grade MGRS - ANADEM",
    page_icon="🗺️",
    layout="wide"
)

@st.cache_data
def load_mgrs_geojson():
    """Carrega o GeoJSON da grade MGRS do GitHub"""
    
    # URL do arquivo GeoJSON no GitHub (SUBSTITUA pela sua URL)
    GITHUB_GEOJSON_URL = "https://raw.githubusercontent.com/geosaber/anadem-mgrs/main/mgrs_grid.geojson"
    
    try:
        response = requests.get(GITHUB_GEOJSON_URL)
        response.raise_for_status()
        
        geojson_data = response.json()
        return geojson_data
        
    except Exception as e:
        st.error(f"Erro ao carregar GeoJSON: {e}")
        return None

def find_clicked_mgrs(geojson_data, clicked_lat, clicked_lng):
    """Encontra o código MGRS da célula clicada"""
    if not geojson_data:
        return None
    
    for feature in geojson_data['features']:
        # Verificar se o ponto clicado está dentro do polígono
        geometry = feature['geometry']
        properties = feature['properties']
        
        if geometry['type'] == 'Polygon':
            # Verificação simplificada - em produção use uma lib como shapely
            coordinates = geometry['coordinates'][0]  # Primeiro anel do polígono
            if is_point_in_polygon(clicked_lng, clicked_lat, coordinates):
                return properties.get('mgrs')  # Ajuste o nome do campo conforme seu GeoJSON
    
    return None

def is_point_in_polygon(x, y, poly):
    """Verifica se um ponto está dentro de um polígono (algoritmo ray casting)"""
    n = len(poly)
    inside = False
    
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def create_mgrs_map(geojson_data):
    """Cria mapa com grade MGRS do GeoJSON"""
    
    # Centro do Brasil
    m = folium.Map(
        location=[-15, -55],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    if geojson_data:
        # Campos específicos para tooltip (mgrs, wr2, utm)
        tooltip_fields = []
        
        # Verificar quais campos existem no GeoJSON
        sample_feature = geojson_data['features'][0] if geojson_data['features'] else {}
        properties = sample_feature.get('properties', {})
        
        # Priorizar os campos solicitados
        preferred_fields = ['mgrs', 'wr2', 'utm', 'MGRS', 'WR2', 'UTM', 'zone']
        
        for field in preferred_fields:
            if field in properties and len(tooltip_fields) < 3:
                tooltip_fields.append(field)
        
        # Se não encontrou os campos preferidos, pega os 3 primeiros disponíveis
        if not tooltip_fields:
            tooltip_fields = list(properties.keys())[:3]
        
        # Aliases para os campos
        field_aliases = {
            'mgrs': 'MGRS:',
            'MGRS': 'MGRS:',
            'wr2': 'WR2:',
            'WR2': 'WR2:',
            'utm': 'UTM:',
            'UTM': 'UTM:',
            'zone': 'Zona:',
            'ZONE': 'Zona:'
        }
        
        # Adicionar grade MGRS ao mapa
        folium.GeoJson(
            geojson_data,
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#FF0000',
                'weight': 1,
                'fillOpacity': 0.1,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=tooltip_fields,
                aliases=[field_aliases.get(field, field) for field in tooltip_fields],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 8px;")
            ),
            name='Grade MGRS',
            zoom_on_click=False
        ).add_to(m)
    
    # Adicionar camadas base
    folium.TileLayer(
        tiles='CartoDB positron',
        attr='CartoDB',
        name='Mapa Claro'
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB dark_matter', 
        attr='CartoDB',
        name='Mapa Escuro'
    ).add_to(m)
    
    # Controle de camadas
    folium.LayerControl().add_to(m)
    
    return m

def main():
    st.title("🗺️ Grade MGRS - ANADEM")
    st.markdown("""
    Visualização da grade MGRS (Military Grid Reference System) com dados do projeto ANADEM.
    **Clique em qualquer célula para ver o código MGRS** ✅
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        st.subheader("🎨 Estilo da Grade")
        line_color = st.color_picker("Cor da linha", "#FF0000")
        line_weight = st.slider("Espessura", 1, 3, 1)
        
        st.subheader("📊 Estatísticas")
    
    # Carregar dados
    with st.spinner("Carregando grade MGRS..."):
        geojson_data = load_mgrs_geojson()
    
    if geojson_data:
        # Estatísticas
        num_features = len(geojson_data['features'])
        
        with st.sidebar:
            st.info(f"""
            **Dados carregados:**
            - Células: {num_features}
            - Fonte: GitHub GeoJSON
            """)
        
        # Criar e exibir mapa
        st.subheader("🗺️ Mapa Interativo - Grade MGRS")
        mgrs_map = create_mgrs_map(geojson_data)
        
        map_data = st_folium(
            mgrs_map, 
            width=1200, 
            height=600,
            returned_objects=['last_clicked', 'last_active_drawing']
        )
        
        # Informações da célula clicada
        if map_data and map_data.get('last_clicked'):
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lng = map_data['last_clicked']['lng']
            
            # Encontrar código MGRS da célula clicada
            clicked_mgrs = find_clicked_mgrs(geojson_data, clicked_lat, clicked_lng)
            
            st.sidebar.subheader("📍 Célula Clicada")
            st.sidebar.write(f"**Latitude:** {clicked_lat:.4f}")
            st.sidebar.write(f"**Longitude:** {clicked_lng:.4f}")
            
            if clicked_mgrs:
                st.sidebar.success(f"**Código MGRS:** {clicked_mgrs}")
            else:
                st.sidebar.warning("Célula MGRS não identificada")
        
        # Mostrar informações do GeoJSON
        with st.expander("📋 Informações da Grade MGRS"):
            if geojson_data['features']:
                sample_properties = geojson_data['features'][0]['properties']
                st.write("**Campos disponíveis no GeoJSON:**")
                for key, value in sample_properties.items():
                    st.write(f"- `{key}`: {value}")
    
    else:
        st.error("""
        ❌ Não foi possível carregar os dados da grade MGRS.
        
        **Solução:**
        1. Converta seu shapefile para GeoJSON
        2. Faça upload do arquivo `mgrs_grid.geojson` no GitHub
        3. Atualize a URL no código
        """)
        
        # Instruções detalhadas
        with st.expander("🔧 Como configurar"):
            st.markdown("""
            **1. Converter shapefile para GeoJSON:**
            ```python
            import geopandas as gpd
            gdf = gpd.read_file("anadem_mgrs.shp")
            gdf.to_file("mgrs_grid.geojson", driver='GeoJSON')
            ```
            
            **2. Fazer upload no GitHub:**
            - Vá no seu repositório
            - Clique em "Add file" → "Upload files"
            - Arraste o `mgrs_grid.geojson`
            
            **3. Obter URL raw:**
            - Clique no arquivo no GitHub
            - Clique em "Raw"
            - Copie a URL
            
            **4. Atualizar o app:**
            ```python
            GITHUB_GEOJSON_URL = "sua_url_aqui"
            ```
            """)
    
if __name__ == "__main__":
    main()
