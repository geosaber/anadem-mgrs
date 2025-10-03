import streamlit as st
import folium
from streamlit_folium import st_folium
import math

def create_advanced_mgrs_map():
    """Cria mapa com grade MGRS mais precisa"""
    
    m = folium.Map(
        location=[-15, -55],
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Grade MGRS simplificada para demonstração
    # Na prática, você usaria uma biblioteca como pymgrs para cálculos precisos
    
    def create_mgrs_cell(lat, lon, size_deg=0.9):
        """Cria uma célula MGRS retangular"""
        return [
            [lat, lon],
            [lat + size_deg, lon],
            [lat + size_deg, lon + size_deg],
            [lat, lon + size_deg],
            [lat, lon]
        ]
    
    # Gerar grade para o Brasil
    features = []
    
    # Área aproximada do Brasil
    for lat in np.arange(-33, 6, 0.9):  # De sul para norte
        for lon in np.arange(-74, -33, 0.9):  # De oeste para leste
            # Simular código MGRS baseado na posição
            zone = 23 + int((lon + 48) / 6)  # Zonas 22-25
            lat_band = "KLMNP"[int((lat + 30) / 10)] if lat >= -30 else "J"
            
            # Célula 100km
            e100k = chr(65 + (int(abs(lon + 74) * 10) % 8))
            n100k = chr(65 + (int(abs(lat + 33) * 10) % 5))
            
            mgrs_code = f"{zone}{lat_band}{e100k}{n100k}"
            
            cell_coords = create_mgrs_cell(lat, lon)
            
            feature = {
                'type': 'Feature',
                'properties': {
                    'MGRS': mgrs_code,
                    'ZONE': zone,
                    'LAT': f"{lat:.1f}",
                    'LON': f"{lon:.1f}",
                    'DESCRIPTION': f"Célula {mgrs_code} - Zona {zone}"
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [cell_coords]
                }
            }
            features.append(feature)
    
    mgrs_grid = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    # Adicionar grade ao mapa
    folium.GeoJson(
        mgrs_grid,
        style_function=lambda feature: {
            'fillColor': 'transparent',
            'color': '#ff0000',
            'weight': 1,
            'fillOpacity': 0.1,
            'dashArray': '5, 5'
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['MGRS', 'ZONE', 'LAT', 'LON', 'DESCRIPTION'],
            aliases=['MGRS:', 'Zona:', 'Lat:', 'Lon:', 'Descrição:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        ),
        popup=folium.GeoJsonPopup(
            fields=['MGRS', 'DESCRIPTION'],
            aliases=['Código MGRS:', 'Descrição:'],
            localize=True
        ),
        name='Grade MGRS'
    ).add_to(m)
    
    return m

def advanced_main():
    st.title("🗺️ Grade MGRS Avançada - ANADEM")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Mapa Interativo")
        advanced_map = create_advanced_mgrs_map()
        st_folium(advanced_map, width=800, height=600)
    
    with col2:
        st.subheader("Legenda MGRS")
        st.markdown("""
        **Código MGRS:**
        - **22K** - Norte
        - **23K** - Centro-Oeste  
        - **24L** - Sudeste
        - **25L** - Sul
        
        **Cores:**
        - 🔴 Grade MGRS
        - 🟢 Célula selecionada
        """)
        
        st.subheader("Controles")
        if st.button("Zoom para Brasil"):
            st.rerun()
        
        show_labels = st.checkbox("Mostrar rótulos", value=True)
        st.info(f"Rótulos: {'✅ Ativado' if show_labels else '❌ Desativado'}")

# App principal
def main():
    st.sidebar.title("Navegação")
    app_mode = st.sidebar.selectbox(
        "Escolha o modo:",
        ["Grade Básica", "Grade Avançada"]
    )
    
    if app_mode == "Grade Básica":
        main()
    else:
        advanced_main()

if __name__ == "__main__":
    main()
