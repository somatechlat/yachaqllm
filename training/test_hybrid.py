#!/usr/bin/env python3
from groq import Groq
import json
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

prompt = """Genera 5 preguntas sobre tributación Ecuador similares a: ¿Cuál es la tarifa del IVA?

JSON format:
[{"instruction": "pregunta", "input": "", "output": "respuesta detallada", "category": "tributacion", "type": "multiple_choice"}]

Solo JSON:"""

response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': 'Respondes SOLO con JSON válido.'},
        {'role': 'user', 'content': prompt}
    ],
    model='llama-3.3-70b-versatile',
    temperature=0.9,
    max_tokens=2000,
)

text = response.choices[0].message.content
if '```' in text:
    text = '\n'.join(text.split('\n')[1:-1])

start = text.find('[')
end = text.rfind(']') + 1
if start != -1:
    qa = json.loads(text[start:end])
    print(f'✅ Generated {len(qa)} questions\n')
    for i, q in enumerate(qa, 1):
        print(f"{i}. Q: {q['instruction']}")
        print(f"   A: {q['output'][:100]}...\n")
