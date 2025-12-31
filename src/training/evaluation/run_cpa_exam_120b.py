import json
import boto3
import time

# "Official" Accountant Certification Benchmark (Ecuador 2024)
EXAM_QUESTIONS = [
    {
        "id": 1,
        "category": "Tributario",
        "question": "A partir del 1 de abril de 2024, ¿cuál es la tarifa general del Impuesto al Valor Agregado (IVA) en Ecuador y qué decreto/ley lo estableció?",
        "answer_key": "15%. Establecido por la Ley Orgánica para Enfrentar el Conflicto Armado Interno."
    },
    {
        "id": 2,
        "category": "Tributario",
        "question": "Explique el régimen RIMPE (Régimen Simplificado para Emprendedores y Negocios Populares). ¿Cuál es el límite de ingresos brutos anuales para ser considerado 'Negocio Popular'?",
        "answer_key": "Hasta $20,000.00 USD anuales."
    },
    {
        "id": 3,
        "category": "Laboral",
        "question": "Calcule la bonificación por desahucio para un trabajador con 8 años de servicio cuyo último sueldo fue de $800. Cite la base legal.",
        "answer_key": "Art. 185 Código del Trabajo. 25% de la última remuneración por cada año. $800 * 0.25 * 8 = $1,600."
    },
    {
        "id": 4,
        "category": "Societario",
        "question": "¿Cuál es el monto mínimo de capital suscrito para constituir una Compañía de Responsabilidad Limitada (Cía. Ltda.) en Ecuador según la Ley de Compañías?",
        "answer_key": "$400.00 USD."
    },
    {
        "id": 5,
        "category": "Tributario",
        "question": "Según la normativa de bancarización, ¿a partir de qué monto es obligatorio utilizar el sistema financiero para que un gasto sea deducible?",
        "answer_key": "$1,000.00 USD (o superior)."
    },
    {
        "id": 6,
        "category": "Tributario",
        "question": "¿Cuál es el porcentaje de retención en la fuente del Impuesto a la Renta para honorarios profesionales (personas naturales) en 2024?",
        "answer_key": "10% (generalmente)."
    },
    {
        "id": 7,
        "category": "Laboral",
        "question": "¿Cómo se calcula el pago de la décima tercera remuneración y cuál es la fecha máxima de pago en el régimen de la Costa?",
        "answer_key": "Total ganado en el año dividido para 12. Fecha máxima: 24 de diciembre (aunque se acumule o mensualice, el cálculo base es ese)."
    },
    {
        "id": 8,
        "category": "Tributario",
        "question": "Una sociedad distribuye dividendos a una persona natural residente en Ecuador. ¿Están gravados estos dividendos? ¿Existe retención?",
        "answer_key": "Sí, están gravados como ingreso. Retención hasta el 25% según la tabla progresiva (Art. 39 LRTI)."
    },
    {
        "id": 9,
        "category": "Contable",
        "question": "Bajo NIIF, ¿cómo se deben valorar inicialmente los inventarios?",
        "answer_key": "Al costo de adquisición o producción."
    },
    {
        "id": 10,
        "category": "Tributario",
        "question": "¿Qué formulario se utiliza para la declaración del Impuesto a la Renta de Personas Naturales y Sucesiones Indivisas?",
        "answer_key": "Formulario 102 (obligados a llevar contabilidad) o 102A (no obligados)."
    }
]

REGION = "us-east-1"
MODEL_ID = "openai.gpt-oss-120b-1:0"

def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=REGION)

def ask_model(client, question):
    # Retry with Chat Completions format (standard OpenAI style often used in Bedrock proxies)
    messages = [
        {
            "role": "system",
            "content": "ERES YACHAQ, EL EXPERTO CONTABLE Y LEGAL DE ECUADOR. Tu objetivo es aprobar el EXAMEN DE CERTIFICACIÓN CPA (Contador Público Autorizado). Responde con precisión absoluta, citando leyes vigentes (2024) y realizando cálculos exactos."
        },
        {
            "role": "user",
            "content": f"PREGUNTA DE EXAMEN: {question}"
        }
    ]

    # Try format 1: "messages" key
    body_chat = json.dumps({
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.0
    })
    
    try:
        response = client.invoke_model(modelId=MODEL_ID, body=body_chat)
        response_body = json.loads(response.get("body").read())
        # Try finding content in standard places
        if "choices" in response_body and len(response_body["choices"]) > 0:
             return response_body["choices"][0]["message"]["content"].strip()
        elif "content" in response_body:
             return response_body["content"]
        else:
             return str(response_body)
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=========================================================")
    print(f"  EJECUTANDO EXAMEN CPA (Model: {MODEL_ID}) - ATTEMPT 2")
    print("=========================================================")
    client = get_bedrock_client()
    
    passed = 0
    results_log = []

    for item in EXAM_QUESTIONS:
        print(f"\nPregunta {item['id']} ({item['category']}):")
        print(f"Q: {item['question']}")
        
        answer = ask_model(client, item['question'])
        print(f"Yachaq-120B: {answer}")
        
        results_log.append({
            "q": item['question'],
            "a": answer,
            "key": item['answer_key']
        })
        time.sleep(1)

    print("\n=========================================================")
    print("EXAMEN COMPLETADO (ATTEMPT 2)")
    print("=========================================================")

if __name__ == "__main__":
    main()
