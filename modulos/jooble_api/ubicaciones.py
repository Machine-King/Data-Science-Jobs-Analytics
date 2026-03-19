import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# ================================
# Desde localizaciones.py
# ================================
COMUNIDADES_AUTONOMAS = {
    "Andalucía": {
        "provincias": ["Sevilla", "Málaga", "Granada", "Córdoba", "Cádiz", "Jaén", "Huelva", "Almería"],
        "ciudades": ["Sevilla", "Málaga", "Granada", "Córdoba", "Cádiz", "Jaén", "Huelva", "Almería", "Jerez de la Frontera", "Marbella", "Dos Hermanas", "Algeciras", "Alcalá de Guadaíra", "Fuengirola", "Mijas", "Vélez-Málaga", "Torremolinos", "Chiclana de la Frontera"],
        "alternativas": ["Andalucía", "Andalusia"]
    },
    "Aragón": {
        "provincias": ["Zaragoza", "Huesca", "Teruel"],
        "ciudades": ["Zaragoza", "Huesca", "Teruel", "Calatayud", "Barbastro", "Ejea de los Caballeros"],
        "alternativas": ["Aragón"]
    },
    "Asturias": {
        "provincias": ["Asturias"],
        "ciudades": ["Oviedo", "Gijón", "Avilés", "Mieres", "Langreo"],
        "alternativas": ["Asturias", "Principado de Asturias"]
    },
    "Islas Baleares": {
        "provincias": ["Islas Baleares"],
        "ciudades": ["Palma", "Ibiza", "Mahón", "Inca", "Manacor"],
        "alternativas": ["Islas Baleares", "Baleares", "Illes Balears"]
    },
    "Canarias": {
        "provincias": ["Las Palmas", "Santa Cruz de Tenerife"],
        "ciudades": ["Las Palmas de Gran Canaria", "Santa Cruz de Tenerife", "San Cristóbal de La Laguna", "Telde", "Arrecife", "Puerto del Rosario", "Arona", "La Orotava"],
        "alternativas": ["Canarias", "Islas Canarias"]
    },
    "Cantabria": {
        "provincias": ["Cantabria"],
        "ciudades": ["Santander", "Torrelavega", "Castro-Urdiales", "Camargo"],
        "alternativas": ["Cantabria"]
    },
    "Castilla y León": {
        "provincias": ["Ávila", "Burgos", "León", "Palencia", "Salamanca", "Segovia", "Soria", "Valladolid", "Zamora"],
        "ciudades": ["Valladolid", "León", "Burgos", "Salamanca", "Ponferrada", "Palencia", "Ávila", "Zamora", "Segovia", "Soria"],
        "alternativas": ["Castilla y León"]
    },
    "Castilla-La Mancha": {
        "provincias": ["Albacete", "Ciudad Real", "Cuenca", "Guadalajara", "Toledo"],
        "ciudades": ["Albacete", "Ciudad Real", "Cuenca", "Guadalajara", "Toledo", "Talavera de la Reina", "Puertollano", "Alcázar de San Juan"],
        "alternativas": ["Castilla-La Mancha"]
    },
    "Cataluña": {
        "provincias": ["Barcelona", "Girona", "Lleida", "Tarragona"],
        "ciudades": ["Barcelona", "Hospitalet de Llobregat", "Badalona", "Terrassa", "Sabadell", "Mataró", "Santa Coloma de Gramenet", "Cornellà de Llobregat", "Sant Boi de Llobregat", "Manresa", "Granollers", "Vilanova i la Geltrú", "Girona", "Figueres", "Blanes", "Lloret de Mar", "Olot", "Lleida", "Tàrrega", "Mollerussa", "Balaguer", "Tarragona", "Reus", "Tortosa", "El Vendrell", "Cambrils"],
        "alternativas": ["Catalunya", "Cataluña", "Catalonia"]
    },
    "Comunidad Valenciana": {
        "provincias": ["Valencia", "Alicante", "Castellón", "Castelló"],
        "ciudades": ["Valencia", "Sagunto", "Xàtiva", "Gandia", "Alzira", "Cullera", "Torrente", "Paterna", "Burjassot", "Mislata", "Xirivella", "Catarroja", "Algemesí", "Chiva", "Sueca", "Carlet", "Alicante", "Elche", "Benidorm", "Alcoy", "Elda", "Orihuela", "Torrevieja", "Denia", "Villena", "San Vicente del Raspeig", "Calpe", "Altea", "Javea", "Xàbia", "Crevillent", "Petrer", "Castellón", "Castelló", "Vila-real", "Burriana", "Vinaròs", "Onda", "Almassora", "Benicàssim", "La Vall d'Uixó", "Segorbe", "Nules", "Borriol"],
        "alternativas": ["Valencia", "Comunitat Valenciana", "País Valencià"]
    },
    "Extremadura": {
        "provincias": ["Badajoz", "Cáceres"],
        "ciudades": ["Badajoz", "Cáceres", "Mérida", "Plasencia", "Don Benito"],
        "alternativas": ["Extremadura"]
    },
    "Galicia": {
        "provincias": ["A Coruña", "Lugo", "Ourense", "Pontevedra"],
        "ciudades": ["A Coruña", "Santiago de Compostela", "Lugo", "Ourense", "Pontevedra", "Vigo", "Ferrol", "Vilagarcía de Arousa"],
        "alternativas": ["Galicia"]
    },
    "Comunidad de Madrid": {
        "provincias": ["Madrid"],
        "ciudades": ["Madrid", "Móstoles", "Alcalá de Henares", "Fuenlabrada", "Leganés", "Getafe", "Alcorcón", "Torrejón de Ardoz", "Parla", "Alcobendas", "Las Rozas", "Pozuelo de Alarcón", "San Sebastián de los Reyes", "Rivas-Vaciamadrid", "Coslada", "Valdemoro", "Collado Villalba", "Majadahonda", "Arganda del Rey"],
        "alternativas": ["Madrid", "Comunidad de Madrid"]
    },
    "Murcia": {
        "provincias": ["Murcia"],
        "ciudades": ["Murcia", "Cartagena", "Lorca", "Molina de Segura", "Cieza"],
        "alternativas": ["Murcia", "Región de Murcia"]
    },
    "Navarra": {
        "provincias": ["Navarra"],
        "ciudades": ["Pamplona", "Tudela", "Barañáin", "Burlada"],
        "alternativas": ["Navarra", "Comunidad Foral de Navarra"]
    },
    "País Vasco": {
        "provincias": ["Álava", "Bizkaia", "Guipúzcoa", "Vizcaya", "Guipuzkoa"],
        "ciudades": ["Vitoria-Gasteiz", "Bilbao", "San Sebastián", "Barakaldo", "Getxo", "Portugalete", "Irún", "Santurtzi"],
        "alternativas": ["País Vasco", "Euskadi", "Basque Country"]
    },
    "La Rioja": {
        "provincias": ["La Rioja"],
        "ciudades": ["Logroño", "Calahorra", "Arnedo"],
        "alternativas": ["La Rioja"]
    },
    "Ceuta": {
        "provincias": ["Ceuta"],
        "ciudades": ["Ceuta"],
        "alternativas": ["Ceuta"]
    },
    "Melilla": {
        "provincias": ["Melilla"],
        "ciudades": ["Melilla"],
        "alternativas": ["Melilla"]
    }
}

TERMINOS_ESPANA = [
    "España", "Spain", "Espanya", "Remoto España", "Remote Spain",
    "Teletrabajo España", "Nacional", "Todo el país"
]

# ================================
# Desde limpieza.py
# ================================
class LimpiadorUbicaciones:
    """
    Clase para limpiar y organizar ofertas por ubicación geográfica.
    """
    
    def __init__(self):
        self.comunidades_autonomas = COMUNIDADES_AUTONOMAS
        self.terminos_espana = TERMINOS_ESPANA
    
    def normalizar_ubicacion(self, ubicacion):
        if not ubicacion:
            return ""

        ubicacion = ubicacion.strip()
        ubicacion = re.sub(r'\s+', ' ', ubicacion)
        if ',' in ubicacion:
            return ubicacion

        ubicacion_simple = ubicacion.replace(',', '').replace('(', '').replace(')', '').replace('  ', ' ').strip()

        for comunidad, datos in self.comunidades_autonomas.items():
            if ubicacion_simple in datos['ciudades']:
                return f"{ubicacion_simple}, {comunidad}"

        return ubicacion_simple
    
    def detectar_comunidad(self, ubicacion):
        if not ubicacion:
            return None, 0
        
        ubicacion_norm = self.normalizar_ubicacion(ubicacion)
        ubicacion_lower = ubicacion_norm.lower()
        
        for comunidad, datos in self.comunidades_autonomas.items():
            if any(alt.lower() in ubicacion_lower for alt in datos["alternativas"]):
                return comunidad, 1.0
            if any(prov.lower() in ubicacion_lower for prov in datos["provincias"]):
                return comunidad, 0.9
            if any(ciu.lower() in ubicacion_lower for ciu in datos["ciudades"]):
                return comunidad, 0.8
        
        if any(term.lower() in ubicacion_lower for term in self.terminos_espana):
            return "España (genérico)", 0.5
        
        return None, 0
    
    def limpiar_ofertas(self, ofertas, mostrar_estadisticas=True):
        ofertas_organizadas = {}
        ofertas_sin_clasificar = []
        estadisticas = {
            "total_procesadas": 0,
            "reclasificadas": 0,
            "duplicados_eliminados": 0,
            "sin_clasificar": 0
        }
        
        ofertas_vistas = set()
        
        for oferta in ofertas:
            estadisticas["total_procesadas"] += 1
            
            oferta_id = self._crear_id_unico(oferta)
            
            if oferta_id in ofertas_vistas:
                estadisticas["duplicados_eliminados"] += 1
                continue
            
            ofertas_vistas.add(oferta_id)
            
            ubicacion_original = oferta.get('location', '').strip()
            
            comunidad, confianza = self.detectar_comunidad(ubicacion_original)
            
            if comunidad and confianza >= 0.8:
                if comunidad != ubicacion_original:
                    estadisticas["reclasificadas"] += 1
                
                if comunidad not in ofertas_organizadas:
                    ofertas_organizadas[comunidad] = []
                
                oferta_copia = oferta.copy()
                oferta_copia['ubicacion_original'] = ubicacion_original
                oferta_copia['ubicacion_corregida'] = f'{ubicacion_original}, {comunidad}'
                if len(oferta_copia['ubicacion_corregida'].split(',')) > 2:
                    oferta_copia['ubicacion_corregida'] = oferta_copia['ubicacion_corregida'].split(',')[0].strip()+', '+comunidad
                oferta_copia['confianza_clasificacion'] = confianza
                
                ofertas_organizadas[comunidad].append(oferta_copia)
            else:
                estadisticas["sin_clasificar"] += 1
                ofertas_sin_clasificar.append({
                    **oferta,
                    'ubicacion_original': ubicacion_original,
                    'razon_sin_clasificar': f'Confianza insuficiente: {confianza}'
                })
        
        if mostrar_estadisticas:
            self._mostrar_estadisticas(estadisticas, ofertas_organizadas, ofertas_sin_clasificar)
        
        return {
            'ofertas_organizadas': ofertas_organizadas,
            'ofertas_sin_clasificar': ofertas_sin_clasificar,
            'estadisticas': estadisticas
        }
    
    def _crear_id_unico(self, oferta):
        titulo = oferta.get('title', '').lower().strip()
        empresa = oferta.get('company', '').lower().strip()
        ubicacion = oferta.get('location', '').lower().strip()
        fecha = oferta.get('created', '').strip()
        
        return f"{titulo}|{empresa}|{ubicacion}|{fecha}"
    
    def _mostrar_estadisticas(self, estadisticas, ofertas_organizadas, ofertas_sin_clasificar):
        logger.info("=" * 60)
        logger.info("ESTADÍSTICAS DE LIMPIEZA DE UBICACIONES")
        logger.info("=" * 60)
        
        logger.info(f"Total de ofertas procesadas: {estadisticas['total_procesadas']}")
        logger.info(f"Ofertas reclasificadas: {estadisticas['reclasificadas']}")
        logger.info(f"Duplicados eliminados: {estadisticas['duplicados_eliminados']}")
        logger.info(f"Ofertas sin clasificar: {estadisticas['sin_clasificar']}")
        
        logger.info("-" * 40)
        logger.info("DISTRIBUCIÓN POR COMUNIDADES:")
        logger.info("-" * 40)
        
        for comunidad, ofertas in sorted(ofertas_organizadas.items()):
            logger.info(f"{comunidad}: {len(ofertas)} ofertas")
        
        if ofertas_sin_clasificar:
            logger.info(f"Ofertas sin clasificar: {len(ofertas_sin_clasificar)}")
            logger.info("Ejemplos de ubicaciones sin clasificar:")
            for oferta in ofertas_sin_clasificar[:5]:
                logger.info(f"  - {oferta.get('ubicacion_original', 'N/A')}")
        
        logger.info("=" * 60)
    
    def exportar_resultados(self, resultado_limpieza, archivo_base="ofertas_limpias"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        archivo_organizadas = f"{archivo_base}_{timestamp}.json"
        with open(archivo_organizadas, 'w', encoding='utf-8') as f:
            json.dump(resultado_limpieza['ofertas_organizadas'], f, ensure_ascii=False, indent=2)
        
        archivo_sin_clasificar = None
        if resultado_limpieza['ofertas_sin_clasificar']:
            archivo_sin_clasificar = f"{archivo_base}_sin_clasificar_{timestamp}.json"
            with open(archivo_sin_clasificar, 'w', encoding='utf-8') as f:
                json.dump(resultado_limpieza['ofertas_sin_clasificar'], f, ensure_ascii=False, indent=2)
        
        archivo_stats = f"{archivo_base}_estadisticas_{timestamp}.json"
        with open(archivo_stats, 'w', encoding='utf-8') as f:
            json.dump(resultado_limpieza['estadisticas'], f, ensure_ascii=False, indent=2)
        
        return {
            'organizadas': archivo_organizadas,
            'sin_clasificar': archivo_sin_clasificar,
            'estadisticas': archivo_stats
        }
