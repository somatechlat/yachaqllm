#!/usr/bin/env python3
"""
GOVERNMENT DATA DOWNLOADER → S3
================================
Downloads documents from Ecuador government sources directly to S3.
"""

import subprocess
import os
import tempfile
import requests
from urllib.parse import urljoin

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"

# Known PDF URLs from official sources
DOCUMENTS = [
    # LOPDP - Ley de Protección de Datos
    {
        "url": "https://www.telecomunicaciones.gob.ec/wp-content/uploads/2021/06/Ley-Organica-de-Proteccion-de-Datos-Personales.pdf",
        "s3_path": "asamblea/year=2021/lopdp_ley_organica_proteccion_datos_personales.pdf",
        "name": "LOPDP 2021"
    },
    # COOTAD
    {
        "url": "https://www.defensa.gob.ec/wp-content/uploads/downloads/2015/04/COOTAD_Actualizado.pdf",
        "s3_path": "gobierno/cootad_codigo_organico_organizacion_territorial.pdf",
        "name": "COOTAD"
    },
    # COA - Código Orgánico del Ambiente
    {
        "url": "https://www.telecomunicaciones.gob.ec/wp-content/uploads/2019/05/COA.pdf",
        "s3_path": "asamblea/year=2017/coa_codigo_organico_ambiente.pdf",
        "name": "COA 2017"
    },
    # COPCI - Código de Producción, Comercio e Inversiones (Aduanas)
    {
        "url": "https://www.produccion.gob.ec/wp-content/uploads/2019/05/Literal-a1-COPCI.pdf",
        "s3_path": "gobierno/copci_codigo_produccion_comercio_inversiones.pdf",
        "name": "COPCI (Aduanas)"
    },
    # Ley de Seguridad Social (IESS)
    {
        "url": "https://www.iess.gob.ec/documents/10162/33703/Ley+de+Seguridad+Social.pdf",
        "s3_path": "iess/ley_seguridad_social.pdf",
        "name": "Ley Seguridad Social"
    },
    # Ley de Compañías (SUPERCIAS)
    {
        "url": "https://www.supercias.gob.ec/bd_supercias/descargas/lotaip/a2/Ley-Companias.pdf",
        "s3_path": "supercias/ley_companias.pdf",
        "name": "Ley de Compañías"
    },
    # Código del Trabajo
    {
        "url": "https://www.trabajo.gob.ec/wp-content/uploads/2012/10/C%C3%B3digo-del-Trabajo.pdf",
        "s3_path": "laboral/codigo_trabajo.pdf",
        "name": "Código del Trabajo"
    },
    # LRTI - Ley de Régimen Tributario Interno
    {
        "url": "https://www.sri.gob.ec/o/sri-tax-service-portlet/documentos/LEY_DE_REGIMEN_TRIBUTARIO_INTERNO.pdf",
        "s3_path": "tributario/lrti_ley_regimen_tributario_interno.pdf",
        "name": "LRTI"
    },
    # LOSNCP - Ley de Contratación Pública
    {
        "url": "https://portal.compraspublicas.gob.ec/sercop/wp-content/uploads/2019/03/LOSNCP.pdf",
        "s3_path": "contratacion/losncp_ley_contratacion_publica.pdf",
        "name": "LOSNCP"
    },
    # Constitución 2008
    {
        "url": "https://www.asambleanacional.gob.ec/sites/default/files/documents/old/constitucion_de_bolsillo.pdf",
        "s3_path": "asamblea/constitucion_ecuador_2008.pdf",
        "name": "Constitución 2008"
    },
    # COIP - Código Penal
    {
        "url": "https://www.defensa.gob.ec/wp-content/uploads/downloads/2018/03/COIP_feb2018.pdf",
        "s3_path": "asamblea/coip_codigo_integral_penal.pdf",
        "name": "COIP"
    },
    # Código Civil
    {
        "url": "https://www.registrosdelpropiedad.gob.ec/wp-content/uploads/2015/08/CODIGO-CIVIL1.pdf",
        "s3_path": "asamblea/codigo_civil_ecuador.pdf",
        "name": "Código Civil"
    },
]

def download_and_upload(doc):
    """Download PDF and upload to S3"""
    print(f"\n📥 Downloading: {doc['name']}")
    print(f"   From: {doc['url'][:60]}...")
    
    try:
        # Download to temp file
        response = requests.get(doc['url'], timeout=60, verify=False)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        file_size = len(response.content) / 1024  # KB
        print(f"   Size: {file_size:.0f} KB")
        
        # Upload to S3
        s3_full_path = f"{S3_BUCKET}/{doc['s3_path']}"
        print(f"   Uploading to: {s3_full_path}")
        
        result = subprocess.run(
            ['aws', 's3', 'cp', tmp_path, s3_full_path, '--region', 'us-east-1'],
            capture_output=True, text=True
        )
        
        # Cleanup
        os.unlink(tmp_path)
        
        if result.returncode == 0:
            print(f"   ✅ SUCCESS")
            return True
        else:
            print(f"   ❌ S3 upload failed: {result.stderr}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Download failed: {str(e)[:50]}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:50]}")
        return False

def main():
    print("=" * 60)
    print("  🏛️ GOVERNMENT DATA DOWNLOADER → S3")
    print("=" * 60)
    print(f"  Target bucket: {S3_BUCKET}")
    print(f"  Documents to download: {len(DOCUMENTS)}")
    print("=" * 60)
    
    success = 0
    failed = 0
    
    for doc in DOCUMENTS:
        if download_and_upload(doc):
            success += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print("  📊 DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"  ✅ Success: {success}")
    print(f"  ❌ Failed: {failed}")
    print("=" * 60)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
