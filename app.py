# ==============================================================================
# V_FINAL_LENGUAJE_DIDACTICO CON HOMOLOGACIÓN DE SITUACIONES HEMODINÁMICAS (ICG)
# Corrección de reconocimiento: unifica Acostado/Cinta/Spot vs Parado
# ==============================================================================

def homologar_posiciones_hemodinamicas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza y unifica los términos de situación clínica basales 
    (Acostado, Cinta, Spot, Basal) en una etiqueta consistente ("ACOSTADO/CINTA/SPOT")
    para asegurar que el motor ortostático calcule correctamente los deltas contra "PARADO".
    """
    if df is None or df.empty:
        return df
        
    df_clean = df.copy()
    
    # Identificamos dinámicamente la columna que define la situación o posición
    col_posicion = None
    for col in df_clean.columns:
        col_norm = normalizar_txt(col)
        if col_norm in ["situacion", "posicion", "estado", "fase"]:
            col_posicion = col
            break
            
    if not col_posicion and len(df_clean.columns) > 0:
        # Fallback: asumimos que la primera columna podría ser el descriptor
        col_posicion = df_clean.columns[0]
        
    if col_posicion:
        # Mapeo estricto para unificar criterios clínicos basales y de ortostatismo
        def mapear_valor(val: Any) -> str:
            v_norm = normalizar_txt(val)
            if any(p in v_norm for p in ["acostado", "cinta", "spot", "basal", "supino", "reposo"]):
                return "ACOSTADO/CINTA/SPOT"
            if any(p in v_norm for p in ["parado", "bipedestacion", "pie", "orto"]):
                return "PARADO"
            return str(val).strip()
            
        df_clean[col_posicion] = df_clean[col_posicion].apply(mapear_valor)
        
    return df_clean


try:
    # Interceptamos la generación de informe aplicando primero la homologación de variables
    _generar_informe_texto_pre_lenguaje_didactico = generar_informe_texto
    
    def generar_informe_texto(df: pd.DataFrame, contexto_embarazo: Optional[Dict[str, Any]] = None) -> str:
        df_homologado = homologar_posiciones_hemodinamicas(df)
        return limpiar_patrones_prohibidos(_generar_informe_texto_pre_lenguaje_didactico(df_homologado, contexto_embarazo))
except Exception:
    pass


try:
    # Interceptamos la validación hemodinámica inteligente para que los deltas no fallen
    _validar_hemodinamica_inteligente_pre_vcrit_final = validar_hemodinamica_inteligente
    
    def validar_hemodinamica_inteligente(df: pd.DataFrame, contexto_embarazo: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        df_homologado = homologar_posiciones_hemodinamicas(df)
        return _validar_hemodinamica_inteligente_pre_vcrit_final(df_homologado, contexto_embarazo)
except Exception:
    pass


try:
    # Interceptamos el cálculo de delta ortostático para que reconozca los estados unificados
    _calcular_delta_ortostatico_pre_ic_final = calcular_delta_ortostatico
    
    def calcular_delta_ortostatico(df: pd.DataFrame) -> Dict[str, Any]:
        df_homologado = homologar_posiciones_hemodinamicas(df)
        return _calcular_delta_ortostatico_pre_ic_final(df_homologado)
except Exception:
    pass
