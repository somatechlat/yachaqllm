#!/usr/bin/env python3
"""
BATCH 2 - More Verified Documents → S3
=======================================
"""

import subprocess
import os

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"

# New verified documents
DOCS = [
    # From OAS (verified working)
    ("Ley Anticorrupcion", "https://www.oas.org/juridico/spanish/mesicic2_ecu_anexo2.pdf", "asamblea/ley_anticorrupcion.pdf"),
    
    # More from SUPERCIAS
    ("Reglamento Companias", "https://www.supercias.gob.ec/bd_supercias/descargas/ss/REGLAMENTO_A_LEY_DE_COMPANIAS.pdf", "supercias/reglamento_ley_companias.pdf"),
    
    # From Defensoría Pública
    ("COFJ", "https://www.defensoria.gob.ec/images/defensoria/pdfs/lotaip2015/enero/a2/CODIGO_ORGANICO_FUNCION_JUDICIAL.pdf", "asamblea/cofj_funcion_judicial.pdf"),
    
    # From Registro Civil
    ("Ley Registro Civil", "https://www.registrocivil.gob.ec/wp-content/uploads/downloads/2017/05/LEY_DE_REGISTRO_CIVIL_IDENTIFICACION_Y_CEDULACION.pdf", "gobierno/ley_registro_civil.pdf"),
    
    # From SNI
    ("LOPPM", "https://www.gob.ec/sites/default/files/regulations/2020-03/CONSTITUCION_2008.pdf", "asamblea/constitucion_gob_ec.pdf"),
]

def download_upload(name, url, s3_path):
    print(f"\n📥 {name}")
    
    # Test URL
    test = subprocess.run(['curl', '-sI', '--max-time', '10', url], capture_output=True, text=True)
    if '200' not in test.stdout and '302' not in test.stdout:
        print(f"   ❌ URL not accessible")
        return False
    
    # Download
    tmp = f"/tmp/{name.replace(' ', '_')}.pdf"
    subprocess.run(['curl', '-sL', '--max-time', '60', '-o', tmp, url], capture_output=True)
    
    if not os.path.exists(tmp) or os.path.getsize(tmp) < 1000:
        print(f"   ❌ Download failed")
        return False
    
    print(f"   ✓ Downloaded: {os.path.getsize(tmp)//1024} KB")
    
    # Upload
    result = subprocess.run(['aws', 's3', 'cp', tmp, f"{S3_BUCKET}/{s3_path}", '--region', 'us-east-1'], capture_output=True)
    os.unlink(tmp)
    
    if result.returncode == 0:
        print(f"   ✅ Uploaded: {s3_path}")
        return True
    return False

def main():
    print("=" * 60)
    print("  📋 BATCH 2 - More Documents → S3")
    print("=" * 60)
    
    success = sum(1 for d in DOCS if download_upload(*d))
    print(f"\n✅ Uploaded: {success}/{len(DOCS)}")

if __name__ == "__main__":
    main()
