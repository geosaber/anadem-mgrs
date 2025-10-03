import streamlit as st
import folium
from streamlit_folium import st_folium
import math

# Configuração da página
st.set_page_config(
    page_title="Grade MGRS - ANADEM",
    page_icon="🗺️",
    layout="wide"
)

def generate_mgrs_grid(bounds, cell_size_deg=1.0):
    """Gera uma grade MGRS simplificada para visualização"""
    features = []
    
    south, west, north, east = bounds
    
    # Gerar grade
    lat = south
    cell_id = 0
    
    while lat < north:
        lon = west
        while lon < east:
            # Criar célula retangular
            cell_coords = [
                [lat, lon],
                [lat + cell_size_deg, lon],
                [lat + cell_size_deg, lon + cell_size_deg],
                [lat, lon + cell_size_deg],
                [lat, lon]
            ]
            
            # Gerar código MGRS simulado baseado na posição
            zone = 22 + int((lon + 54) / 6)  # Zonas 22-25 para Brasil
            zone = max(22, min(25, zone))  # Limitar às zonas do Brasil
            
            # Bandas de latitude (K, L, M para Brasil)
            if lat >= -30:
                lat_band = "L"
            elif lat >= -40:
                lat_band = "M" 
            else:
                lat_band = "N"
            
            # Células 100km (A-V)
            easting_idx = int((lon - west) / cell_size_deg) % 20
            northing_idx = int((lat - south) / cell_size_deg) % 20
            
            e100k = chr(65 + easting_idx)  # A-T
            n100k = chr(65 + northing_idx)  # A-T
            
            mgrs_code = f"{zone:02d}{lat_band}{e100k}{n100k}"
            
            feature = {
                'type': 'Feature',
                'properties': {
                    'MGRS': mgrs_code,
                    'ZONE': zone,
                    'LAT': f"{lat:.2f}°",
                    'LON': f"{lon:.2f}°",
                    'CELL_ID': cell_id
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [cell_coords]
                }
            }
            features.append(feature)
            
            cell_id += 1
            lon += cell_size_deg
        lat += cell_size_deg
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }

def create_mgrs_map():
    """Cria mapa com grade MGRS"""
    
    # Centro do Brasil
    m = folium.Map(
        location=[-15, -55],
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Limites do Brasil
    brazil_bounds = (-33.0, -74.0, 5.0, -34.0)  # sul, oeste, norte, leste
    
    # Gerar grade MGRS
    mgrs_grid = generate_mgrs_grid(brazil_bounds, cell_size_deg=2.0)
    
    # Adicionar grade ao mapa
    folium.GeoJson(
        mgrs_grid,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#0066cc',
            'weight': 1,
            'fillOpacity': 0.05,
            'dashArray': '5, 5'
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['MGRS', 'ZONE', 'LAT', 'LON'],
            aliases=['Código MGRS:', 'Zona UTM:', 'Latitude:', 'Longitude:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 8px;")
        ),
        popup=folium.GeoJsonPopup(
            fields=['MGRS', 'ZONE', 'LAT', 'LON'],
            aliases=['MGRS:', 'Zona:', 'Lat:', 'Lon:'],
            localize=True
        ),
        name='Grade MGRS'
    ).add_to(m)
    
    # Adicionar camadas base alternativas
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='OpenTopoMap',
        name='OpenTopoMap'
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB positron',
        attr='CartoDB',
        name='CartoDB Positron'
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB dark_matter',
        attr='CartoDB',
        name='CartoDB Dark'
    ).add_to(m)
    
    # Controle de camadas
    folium.LayerControl().add_to(m)
    
    return m

def main():
    st.title("🗺️ Grade MGRS - ANADEM")
    st.markdown("""
    Visualização da grade MGRS (Military Grid Reference System) para o território brasileiro.
    Esta grade é utilizada como referência para os dados do projeto ANADEM.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        st.subheader("🎨 Estilo da Grade")
        line_color = st.color_picker("Cor da linha", "#0066cc")
        line_weight = st.slider("Espessura da linha", 1, 3, 1)
        show_grid = st.toggle("Mostrar grade", value=True)
        
        st.subheader("📊 Informações")
        st.info("""
        **Sobre a grade MGRS:**
        - Células de ~100km × 100km
        - Cobertura nacional do Brasil
        - Zonas UTM 22-25
        - Bandas de latitude K, L, M, N
        """)
        
        if st.button("ℹ️ Sobre o ANADEM"):
            st.session_state.show_info = True
    
    # Gerar e exibir mapa
    if show_grid:
        with st.spinner("Gerando grade MGRS..."):
            mgrs_map = create_mgrs_map()
        
        # Exibir mapa
        st.subheader("🗺️ Mapa Interativo")
        map_data = st_folium(
            mgrs_map, 
            width=1200, 
            height=600,
            returned_objects=[]
        )
    else:
        # Mapa sem grade
        m = folium.Map(location=[-15, -55], zoom_start=4)
        st_folium(m, width=1200, height=600)
        st.info("Grade MGRS desativada. Ative na sidebar para visualizar.")
    
    # Seção informativa
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🧩 Sistema MGRS")
        st.markdown("""
        - **Zona UTM**: 22-25 (Brasil)
        - **Bandas**: K, L, M, N  
        - **Células**: 100km × 100km
        - **Precisão**: Até 1 metro
        """)
    
    with col2:
        st.subheader("🇧🇷 Cobertura Nacional")
        st.markdown("""
        - **Norte**: Zona 22
        - **Centro-Oeste**: Zona 23
        - **Sudeste**: Zona 24  
        - **Sul**: Zona 25
        - **Total**: ~8.5M km²
        """)
    
    with col3:
        st.subheader("📈 Dados ANADEM")
        st.markdown("""
        - Modelos Digitais de Elevação
        - Dados de alta precisão
        - Cobertura nacional
        - Acesso gratuito
        """)
    
    # Exemplos de códigos MGRS
    st.subheader("📋 Exemplos de Células MGRS no Brasil")
    
    example_data = {
        "Região": ["Amazônia", "Cerrado", "São Paulo", "Rio Grande do Sul"],
        "Código MGRS": ["22M NK", "23L PL", "24L UJ", "25J FM"], 
        "Zona UTM": ["22", "23", "24", "25"],
        "Coordenadas": ["3°S, 60°W", "15°S, 50°W", "23°S, 46°W", "30°S, 51°W"]
    }
    
    st.dataframe(example_data, use_container_width=True)
    
    # Modal de informações sobre ANADEM
    if st.session_state.get('show_info', False):
        with st.expander("ℹ️ Sobre o Projeto ANADEM", expanded=True):
            st.markdown("""
            **ANADEM - Altitude Nacional Digital de Elevação do Brasil**
            
            O projeto ANADEM tem como objetivo fornecer modelos digitais de elevação 
            de alta precisão para todo o território nacional, utilizando a grade MGRS 
            como sistema de referência para organização dos dados.
            
            **Características:**
            - Resolução espacial variável
            - Dados altimétricos precisos
            - Cobertura nacional contínua
            - Padrão MGRS para indexação
            
            **Aplicações:**
            - Planejamento territorial
            - Estudos ambientais
            - Engenharia e infraestrutura
            - Pesquisa científica
            """)
            
            if st.button("Fechar"):
                st.session_state.show_info = False
                st.rerun()

if __name__ == "__main__":
    main()
