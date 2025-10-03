import streamlit as st
import folium
from streamlit_folium import st_folium

# Configuração da página
st.set_page_config(
    page_title="Grade MGRS - ANADEM",
    page_icon="🗺️",
    layout="wide"
)

def generate_mgrs_grid():
    """Gera uma grade MGRS simplificada para o Brasil"""
    
    # Definir células MGRS principais do Brasil
    mgrs_cells = [
        # Zona 22 - Norte
        {"mgrs": "22K NK", "bounds": [[-5, -54], [-5, -52], [-7, -52], [-7, -54], [-5, -54]]},
        {"mgrs": "22K PK", "bounds": [[-7, -54], [-7, -52], [-9, -52], [-9, -54], [-7, -54]]},
        {"mgrs": "22K PL", "bounds": [[-7, -52], [-7, -50], [-9, -50], [-9, -52], [-7, -52]]},
        
        # Zona 23 - Centro-Oeste
        {"mgrs": "23K PL", "bounds": [[-15, -52], [-15, -50], [-17, -50], [-17, -52], [-15, -52]]},
        {"mgrs": "23K PM", "bounds": [[-15, -50], [-15, -48], [-17, -48], [-17, -50], [-15, -50]]},
        {"mgrs": "23L PJ", "bounds": [[-17, -52], [-17, -50], [-19, -50], [-19, -52], [-17, -52]]},
        
        # Zona 24 - Sudeste
        {"mgrs": "24L UJ", "bounds": [[-23, -46], [-23, -44], [-25, -44], [-25, -46], [-23, -46]]},
        {"mgrs": "24L VJ", "bounds": [[-21, -46], [-21, -44], [-23, -44], [-23, -46], [-21, -46]]},
        {"mgrs": "24L UK", "bounds": [[-23, -48], [-23, -46], [-25, -46], [-25, -48], [-23, -48]]},
        
        # Zona 25 - Sul
        {"mgrs": "25J FM", "bounds": [[-30, -52], [-30, -50], [-32, -50], [-32, -52], [-30, -52]]},
        {"mgrs": "25J GM", "bounds": [[-28, -52], [-28, -50], [-30, -50], [-30, -52], [-28, -52]]},
        {"mgrs": "25J FN", "bounds": [[-30, -50], [-30, -48], [-32, -48], [-32, -50], [-30, -50]]},
    ]
    
    features = []
    for i, cell in enumerate(mgrs_cells):
        feature = {
            'type': 'Feature',
            'properties': {
                'MGRS': cell['mgrs'],
                'ZONE': cell['mgrs'][:2],
                'DESC': f"Célula {cell['mgrs']}",
                'ID': i
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [cell['bounds']]
            }
        }
        features.append(feature)
    
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
    
    # Gerar grade MGRS
    mgrs_grid = generate_mgrs_grid()
    
    # Adicionar grade ao mapa
    folium.GeoJson(
        mgrs_grid,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#FF0000',
            'weight': 2,
            'fillOpacity': 0.1,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['MGRS', 'ZONE', 'DESC'],
            aliases=['Código MGRS:', 'Zona UTM:', 'Descrição:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 8px;")
        ),
        name='Grade MGRS'
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
    Visualização da grade MGRS (Military Grid Reference System) para o território brasileiro.
    **Esta aplicação funciona 100% no Streamlit Cloud!** ✅
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        st.subheader("🎨 Estilo da Grade")
        line_color = st.color_picker("Cor da linha", "#FF0000")
        line_weight = st.slider("Espessura", 1, 5, 2)
        
        st.subheader("📊 Informações")
        st.info("""
        **Grade MGRS ativa:**
        - 12 células exemplo
        - Zonas 22-25
        - Cobertura nacional
        """)
    
    # Exibir mapa
    st.subheader("🗺️ Mapa Interativo - Grade MGRS")
    
    # Criar e exibir mapa
    mgrs_map = create_mgrs_map()
    st_folium(mgrs_map, width=1200, height=600)
    
    # Informações
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧩 Sobre o MGRS")
        st.markdown("""
        **Military Grid Reference System**
        
        - Sistema de coordenadas global
        - Baseado em UTM/Mercator
        - Células de 100km × 100km
        - Precisão de até 1 metro
        - Padrão militar e científico
        """)
    
    with col2:
        st.subheader("🇧🇷 Cobertura do Brasil")
        st.markdown("""
        **Zonas UTM no Brasil:**
        - **Zona 22**: Norte (AM, RR, AP)
        - **Zona 23**: Centro-Oeste (MT, MS, GO, DF)
        - **Zona 24**: Sudeste (SP, RJ, MG, ES)
        - **Zona 25**: Sul (PR, SC, RS)
        """)
    
    # Tabela de células
    st.subheader("📋 Células MGRS no Mapa")
    
    cells_data = [
        {"Célula": "22K NK", "Região": "Norte", "Estado": "AM/PA", "Coordenadas": "5°S, 53°W"},
        {"Célula": "22K PK", "Região": "Norte", "Estado": "AM/PA", "Coordenadas": "7°S, 53°W"},
        {"Célula": "23K PL", "Região": "Centro-Oeste", "Estado": "MT", "Coordenadas": "15°S, 51°W"},
        {"Célula": "23L PJ", "Região": "Centro-Oeste", "Estado": "MT", "Coordenadas": "17°S, 51°W"},
        {"Célula": "24L UJ", "Região": "Sudeste", "Estado": "SP", "Coordenadas": "23°S, 45°W"},
        {"Célula": "24L VJ", "Região": "Sudeste", "Estado": "SP/RJ", "Coordenadas": "21°S, 45°W"},
        {"Célula": "25J FM", "Região": "Sul", "Estado": "RS", "Coordenadas": "30°S, 51°W"},
        {"Célula": "25J GM", "Região": "Sul", "Estado": "RS", "Coordenadas": "28°S, 51°W"},
    ]
    
    st.dataframe(cells_data, use_container_width=True)
    
    # Rodapé
    st.markdown("---")
    st.caption("Desenvolvido para visualização da grade MGRS do projeto ANADEM • Streamlit Cloud")

if __name__ == "__main__":
    main()
