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
    
    # URL do arquivo GeoJSON no GitHub (substitua pela sua URL)
    GITHUB_GEOJSON_URL = "https://raw.githubusercontent.com/seu-usuario/seu-repositorio/main/mgrs_grid.geojson"
    
    try:
        response = requests.get(GITHUB_GEOJSON_URL)
        response.raise_for_status()
        
        geojson_data = response.json()
        return geojson_data
        
    except Exception as e:
        st.error(f"Erro ao carregar GeoJSON: {e}")
        return None

def create_mgrs_map(geojson_data):
    """Cria mapa com grade MGRS do GeoJSON"""
    
    # Centro do Brasil
    m = folium.Map(
        location=[-15, -55],
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    if geojson_data:
        # Encontrar campos disponíveis para tooltip
        sample_feature = geojson_data['features'][0] if geojson_data['features'] else {}
        properties = sample_feature.get('properties', {})
        
        # Campos para tooltip (até 4 campos)
        tooltip_fields = []
        field_aliases = {
            'MGRS': 'Código MGRS:',
            'ZONE': 'Zona UTM:',
            'LAT': 'Latitude:',
            'LON': 'Longitude:',
            'FID': 'ID:',
            'id': 'ID:',
            'name': 'Nome:'
        }
        
        for field in properties.keys():
            if len(tooltip_fields) < 4:  # Limitar a 4 campos
                tooltip_fields.append(field)
        
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
            ) if tooltip_fields else None,
            name='Grade MGRS',
            zoom_on_click=True
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
    Visualização da grade MGRS (Military Grid Reference System) com dados reais do projeto ANADEM.
    **Carregando dados do GeoJSON no GitHub** ✅
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        st.subheader("🎨 Estilo da Grade")
        line_color = st.color_picker("Cor da linha", "#FF0000")
        line_weight = st.slider("Espessura", 1, 3, 1)
        show_labels = st.toggle("Mostrar tooltips", True)
        
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
        st.subheader("🗺️ Mapa Interativo - Grade MGRS Real")
        mgrs_map = create_mgrs_map(geojson_data)
        
        map_data = st_folium(
            mgrs_map, 
            width=1200, 
            height=600,
            returned_objects=['last_clicked', 'bounds']
        )
        
        # Informações da célula clicada
        if map_data and map_data.get('last_clicked'):
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lng = map_data['last_clicked']['lng']
            
            st.sidebar.subheader("📍 Célula Clicada")
            st.sidebar.write(f"Lat: {clicked_lat:.4f}")
            st.sidebar.write(f"Lon: {clicked_lng:.4f}")
    
    else:
        st.error("""
        ❌ Não foi possível carregar os dados da grade MGRS.
        
        **Solução:**
        1. Converta seu shapefile para GeoJSON
        2. Faça upload do arquivo `mgrs_grid.geojson` no GitHub
        3. Atualize a URL no código acima
        """)
        
        st.info("""
        **Como converter para GeoJSON:**
        
        **Com QGIS:**
        - Abra o shapefile no QGIS
        - Clique direito → Exportar → Salvar Feições Como
        - Formato: GeoJSON
        - Salve como `mgrs_grid.geojson`
        
        **Com Python:**
        ```python
        import geopandas as gpd
        gdf = gpd.read_file("anadem_mgrs.shp")
        gdf.to_file("mgrs_grid.geojson", driver='GeoJSON')
        ```
        """)
    
    # Informações
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Sobre os Dados")
        st.markdown("""
        **Fonte:** Grade MGRS do ANADEM
        **Formato:** GeoJSON
        **Armazenamento:** GitHub
        **Atualização:** Automática
        """)
    
    with col2:
        st.subheader("🔧 Tecnologias")
        st.markdown("""
        - **Streamlit** - Interface web
        - **Folium** - Mapas interativos  
        - **GeoJSON** - Dados espaciais
        - **GitHub** - Hospedagem de dados
        """)

if __name__ == "__main__":
    main()
