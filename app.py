import io
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# APP CGI - INFORME HEMODINÁMICO INTEGRADO
# Corrección: importación real de PDF Z-Logic/CGI
# Autor: Ricardo Daniel Olano
# =========================================================

st.set_page_config(
    page_title="APP CGI - Informe Hemodinámico Integrado",
    page_icon="❤️",
    layout="wide",
)

AUTOR_APP = "Ricardo Daniel Olano - Especialista en Cardiología e Hipertensión Arterial"
TITULO_MODULO_NO_EMBARAZADA = "MODULO DE EVALUACION HEMODINAMICA NO INVASIVA POR CARDIOGRAFIA DE IMPEDANCIA"


# =========================================================
# ESTILO
# =========================================================

def aplicar_estilos() -> None:
    """Diseño profesional - paleta médica, contraste WCAG AA, responsive.

    El bloque va dentro de un único <style> sin tags <link> (algunas versiones
    de Streamlit filtran <link> y eso rompe el parser, dejando el CSS visible
    como texto en pantalla). Las fuentes se cargan con @import.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700;800&display=swap');
        :root {
            --brand-primary: #0066cc;
            --brand-secondary: #004d99;
            --bg-canvas: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #475569;
            --border-color: #e2e8f0;
            --accent-alert: #ef4444;
            --accent-success: #10b981;
            --accent-warning: #f59e0b;
        }

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', -apple-system, sans-serif !important;
            background-color: var(--bg-canvas) !important;
            color: var(--text-main) !important;
        }

        h1, h2, h3, h4 {
            color: var(--brand-secondary) !important;
            font-weight: 700 !important;
        }

        .stAlert {
            border-left: 5px solid var(--brand-primary) !important;
            background-color: var(--bg-card) !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
            border-radius: 6px !important;
        }

        /* Botones estilizados */
        .stButton>button {
            background-color: var(--brand-primary) !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 0.5rem 1.5rem !important;
            transition: background-color 0.2s ease !important;
        }
        .stButton>button:hover {
            background-color: var(--brand-secondary) !important;
        }

        /* Contenedores de reportes y tablas */
        div[data-testid="stExpander"] {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        }
        
        .report-box {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# LÓGICA DE DETECCIÓN Y PARSEO EXTENDIDO (Z-Logic / CGI)
# =========================================================

def normalizar_txt(t: Any) -> str:
    """Sanitiza strings removiendo acentos, eñes y caracteres extraños para comparaciones seguras."""
    if not isinstance(t, str):
        t = str(t) if t is not None else ""
    t = t.lower().strip()
    t = re.sub(r'[áàäâ]', 'a', t)
    t = re.sub(r'[éèëê]', 'e', t)
    t = re.sub(r'[íìïî]', 'i', t)
    t = re.sub(r'[óòöô]', 'o', t)
    t = re.sub(r'[úùüû]', 'u', t)
    t = re.sub(r'[ñ]', 'n', t)
    return t


def parsear_archivo_estudio(contenido: bytes, extension: str) -> Optional[pd.DataFrame]:
    """
    Intenta extraer la tabla de variables hemodinámicas desde archivos CSV, Excel,
    o volcados de texto plano provenientes del software Z-Logic / CGI.
    """
    df_resultado = None

    if extension in [".csv", ".txt"]:
        try:
            texto = contenido.decode("utf-8", errors="ignore")
            if "situacion" in texto.lower() or "fase" in texto.lower() or "fc" in texto.lower():
                sep = ";" if ";" in texto else ","
                df_resultado = pd.read_csv(io.StringIO(texto), sep=sep)
        except Exception:
            try:
                texto = contenido.decode("latin-1", errors="ignore")
                sep = ";" if ";" in texto else ","
                df_resultado = pd.read_csv(io.StringIO(texto), sep=sep)
            except Exception:
                pass
                
    elif extension in [".xls", ".xlsx"]:
        try:
            df_resultado = pd.read_excel(io.BytesIO(contenido))
        except Exception:
            pass

    if df_resultado is not None and not df_resultado.empty:
        df_resultado.columns = [c.strip() for c in df_resultado.columns]
        return df_resultado

    return None


# =========================================================
# COMPONENTES AUXILIARES DEL MODELO DE INFORME CLÍNICO
# =========================================================

REFERENCIAS_BIBLIOGRAFICAS = [
    "Van De Water JM, et al. Impedance cardiography: the next step in noninvasive hemodynamic monitoring. J Clin Monit. 2003.",
    "Albert NM, et al. Impedance cardiography: an integral part of advanced practice nursing in heart failure. AACN Clin Issues. 2004.",
    "Ferrario CM, et al. Use of impedance cardiography in the management of hypertension. Curr Hypertens Rep. 2007.",
    "Sanford MR, et al. Noninvasive hemodynamic monitoring in hypertension: a review of impedance cardiography. J Clin Hypertens. 2011."
]

SOPORTE_BIBLIOGRAFICO_APP = """
Esta aplicación procesa datos derivados de sistemas de cardiografía de impedancia (ICG),
utilizando algoritmos estandarizados basados en guías internacionales de evaluación hemodinámica 
no invasiva y el análisis de la onda de pulso aórtica.
""".strip()


def limpiar_patrones_prohibidos(texto: str) -> str:
    """Remueve modismos de IA o frases redundantes para un informe de nivel institucional."""
    patrones = [
        r"aquí está su informe",
        r"claro, con gusto",
        r"de acuerdo al análisis de los datos",
        r"este es el reporte generado",
    ]
    for p in patrones:
        texto = re.sub(p, "", texto, flags=re.IGNORECASE)
    return texto.strip()


def obtener_resumen
