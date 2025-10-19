#!/usr/bin/env python3
"""
BASELINE TEST - Test BEFORE training
We'll test the same questions AFTER training to measure improvement
"""
import json
from datetime import datetime

# Test questions from the real exam
TEST_QUESTIONS = [
    {
        "id": 1,
        "question": "¿Cuál es la tarifa del IVA en Ecuador?",
        "correct_answer": "12% para bienes gravados y 0% para bienes exentos",
        "category": "tributacion"
    },
    {
        "id": 2,
        "question": "¿Quién es el sujeto activo en materia tributaria?",
        "correct_answer": "El Estado",
        "category": "tributacion"
    },
    {
        "id": 3,
        "question": "¿Cuál es la tarifa del Impuesto a la Salida de Divisas?",
        "correct_answer": "5%",
        "category": "tributacion"
    },
    {
        "id": 4,
        "question": "¿Cuándo una empresa está obligada a llevar contabilidad?",
        "correct_answer": "Cuando supera $100,000 en ingresos, $80,000 en gastos o $60,000 en capital",
        "category": "contabilidad"
    },
    {
        "id": 5,
        "question": "¿Qué es el control interno en auditoría?",
        "correct_answer": "Proceso diseñado para proporcionar seguridad razonable sobre el logro de objetivos",
        "category": "auditoria"
    },
    {
        "id": 6,
        "question": "¿Qué es el punto de equilibrio?",
        "correct_answer": "Punto donde los ingresos totales igualan los costos totales",
        "category": "costos"
    },
    {
        "id": 7,
        "question": "¿Qué es el principio de devengado?",
        "correct_answer": "Registro de transacciones cuando ocurren, independiente del movimiento de dinero",
        "category": "contabilidad"
    },
    {
        "id": 8,
        "question": "¿Qué tipo de impuesto es el Impuesto a la Renta?",
        "correct_answer": "Directo y progresivo",
        "category": "tributacion"
    },
    {
        "id": 9,
        "question": "¿Qué son las normas de auditoría?",
        "correct_answer": "Guías que establecen requisitos y procedimientos para realizar auditorías",
        "category": "auditoria"
    },
    {
        "id": 10,
        "question": "¿Qué es el costeo ABC?",
        "correct_answer": "Método que asigna costos indirectos basándose en actividades",
        "category": "costos"
    }
]

def save_baseline():
    """Save baseline test for later comparison"""
    baseline = {
        "timestamp": datetime.now().isoformat(),
        "model": "UNTRAINED (Qwen2.5-7B base)",
        "test_questions": TEST_QUESTIONS,
        "note": "This is BEFORE training. We'll test same questions AFTER."
    }
    
    with open('baseline_test.json', 'w', encoding='utf-8') as f:
        json.dump(baseline, f, indent=2, ensure_ascii=False)
    
    print("✅ BASELINE TEST SAVED")
    print(f"📊 {len(TEST_QUESTIONS)} test questions")
    print(f"📁 File: baseline_test.json")
    print()
    print("After training, we'll test the model on these SAME questions")
    print("to measure improvement!")

if __name__ == "__main__":
    save_baseline()
