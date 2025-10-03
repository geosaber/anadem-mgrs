import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
import requests
import zipfile
import os
import tempfile
import numpy as np
from io import BytesIO
import base64

# Configuração da página
st.set_page_config(
    page_title="ANADEM MGRS Grid",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache para melhor performance
@st.cache_data(show_spinner="Carregando dados MGRS...")
def load_mgrs_data():
    """Carrega os dados MGRS com tratamento de erro robusto"""
    try:
        MGRS_URL = "https://www.ufrgs.br/hge/wp-content/uploads/2024/04/anadem_mgrs.zip"
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Fazer download do arquivo
            response = requests.get(MGRS_URL, timeout=30)
            response.raise_for_status()
            
            zip_path = os.path.join(tmp_dir, "anadem_mgrs.zip")
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extrair arquivo
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)
            
            # Encontrar arquivo shapefile
            shp_files = [f for f in os.listdir(tmp_dir) if f.endswith('.shp')]
            if not shp_files:
                st.error("Nenhum arquivo shapefile encontrado no ZIP")
                return None
            
            shp_path = os.path.join(tmp_dir, shp_files[0])
            gdf = gpd.read_file(shp_path)
            
            # Converter para WGS84 se necessário
            if gdf.crs and gdf.crs != 'EPSG:4326':
                gdf = gdf.to_crs('EPSG:4326')
            
            return gdf
            
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {e}")
        return None
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        return None

def create_base_map(center=[-15, -55], zoom_start=4):
    """Cria mapa base"""
    return folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles='OpenStreetMap',
        control_scale=True
    )

def main():
    # Header
    st.title("🗺️ Grade MGRS - ANADEM")
    st.markdown("""
    Visualização interativa da grade MGRS (Military Grid Reference System) 
    com dados do projeto ANADEM (Altitude Nacional Digital de Elevação do Brasil)
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        st.info("""
        **Sobre os dados:**
        - Grade MGRS para organização dos dados
        - Modelos Digitais de Elevação
        - Cobertura nacional do Brasil
        """)
    
    # Carregar dados
    mgrs_gdf = load_mgrs_data()
    
    if mgrs_gdf is None:
        st.error("""
        ❌ Não foi possível carregar os dados MGRS. 
        
        Possíveis causas:
        - Problema de conexão com a internet
        - Arquivo temporariamente indisponível
        - Formato dos dados incompatível
        """)
        
        # Opção para carregar arquivo local
        st.subheader("📁 Alternativa: Carregar arquivo local")
        uploaded_file = st.file_uploader(
            "Faça upload do arquivo shapefile (ZIP)", 
            type=['zip'],
            help="Faça upload do arquivo anadem_mgrs.zip"
        )
        
        if uploaded_file is not None:
            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    # Salvar arquivo upload
                    zip_path = os.path.join(tmp_dir, "uploaded_mgrs.zip")
                    with open(zip_path, 'wb') as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Extrair
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(tmp_dir)
                    
                    # Carregar shapefile
                    shp_files = [f for f in os.listdir(tmp_dir) if f.endswith('.shp')]
                    if shp_files:
                        shp_path = os.path.join(tmp_dir, shp_files[0])
                        mgrs_gdf = gpd.read_file(shp_path)
                        if mgrs_gdf.crs and mgrs_gdf.crs != 'EPSG:4326':
                            mgrs_gdf = mgrs_gdf.to_crs('EPSG:4326')
                        st.success("✅ Dados carregados com sucesso!")
                    else:
                        st.error("Nenhum shapefile encontrado no arquivo ZIP")
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")
        return
    
    # Controles na sidebar
    with st.sidebar:
        st.subheader("🎛️ Controles do Mapa")
        
        # Filtro por código MGRS
        if 'MGRS' in mgrs_gdf.columns:
            mgrs_codes = sorted(mgrs_gdf['MGRS'].unique())
            selected_mgrs = st.multiselect(
                "Filtrar por código MGRS:",
                options=mgrs_codes,
                default=mgrs_codes[:3] if len(mgrs_codes) > 3 else mgrs_codes,
                help="Selecione as células MGRS para visualizar"
            )
            
            if selected_mgrs:
                filtered_gdf = mgrs_gdf[mgrs_gdf['MGRS'].isin(selected_mgrs)]
            else:
                filtered_gdf = mgrs_gdf
        else:
            filtered_gdf = mgrs_gdf
            st.warning("Coluna 'MGRS' não encontrada nos dados")
        
        # Estilo da grade
        st.subheader("🎨 Estilo da Grade")
        line_color = st.color_picker("Cor da linha", "#0066cc")
        line_weight = st.slider("Espessura da linha", 1, 5, 2)
        
        # Informações
        st.subheader("📊 Informações")
        st.write(f"**Células carregadas:** {len(filtered_gdf)}")
        st.write(f"**Sistema de coordenadas:** {filtered_gdf.crs}")
    
    # Layout principal
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🗺️ Mapa Interativo")
        
        # Criar mapa
        m = create_base_map()
        
        # Adicionar grade MGRS
        if not filtered_gdf.empty:
            # Estilo para a grade
            style_function = lambda x: {
                'fillColor': 'transparent',
                'color': line_color,
                'weight': line_weight,
                'fillOpacity': 0.05
            }
            
            # Tooltip
            tooltip_fields = []
            for col in filtered_gdf.columns:
                if col not in ['geometry'] and filtered_gdf[col].dtype in [object, 'string']:
                    tooltip_fields.append(col)
                    if len(tooltip_fields) >= 3:  # Limitar a 3 campos no tooltip
                        break
            
            if tooltip_fields:
                tooltip = folium.GeoJsonTooltip(
                    fields=tooltip_fields,
                    aliases=[f"{field}:" for field in tooltip_fields],
                    localize=True
                )
            else:
                tooltip = None
            
            folium.GeoJson(
                filtered_gdf.to_json(),
                style_function=style_function,
                tooltip=tooltip,
                name='Grade MGRS'
            ).add_to(m)
        
        # Adicionar controle de camadas
        folium.LayerControl().add_to(m)
        
        # Exibir mapa
        map_data = st_folium(m, width=800, height=600, key="mgrs_map")
    
    with col2:
        st.subheader("📋 Dados")
        
        # Mostrar preview dos dados
        if not filtered_gdf.empty:
            display_cols = [col for col in filtered_gdf.columns if col != 'geometry']
            st.dataframe(
                filtered_gdf[display_cols].head(10),
                use_container_width=True,
                height=300
            )
            
            # Estatísticas
            st.subheader("📈 Estatísticas")
            st.write(f"Total de células: **{len(filtered_gdf)}**")
            
            # Download
            st.subheader("💾 Exportar")
            if st.button("Baixar dados filtrados (CSV)"):
                csv_data = filtered_gdf[display_cols].to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="mgrs_grid.csv",
                    mime="text/csv"
                )
    
    # Seção de informações
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.subheader("ℹ️ Sobre o MGRS")
        st.markdown("""
        O **Military Grid Reference System (MGRS)** é um sistema de coordenadas
        usado para referenciar locais na Terra com alta precisão.
        """)
    
    with col_info2:
        st.subheader("📚 Sobre o ANADEM")
        st.markdown("""
        **ANADEM** - Altitude Nacional Digital de Elevação do Brasil
        fornece modelos digitais de elevação de alta qualidade para todo o território nacional.
        """)
    
    with col_info3:
        st.subheader("🔧 Tecnologias")
        st.markdown("""
        Desenvolvido com:
        - **Streamlit** - Interface web
        - **Folium** - Mapas interativos
        - **GeoPandas** - Processamento geoespacial
        - **Python** - Lógica da aplicação
        """)

if __name__ == "__main__":
    main()
