#!/usr/bin/env python3
"""
🌐 Frontend Web para o Agente de IA
Servidor Flask com interface de chat
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import sys
import os

from src.my_agent import invoke

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Página principal do chat"""
    return render_template('chat.html')

@app.route('/download/<filename>')
def download_pdf(filename):
    """Endpoint para download de PDFs"""
    try:
        pdf_path = os.path.join('results', filename)
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True)
        else:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint para chat com o agente"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Chamar o agente de IA
        payload = {"prompt": user_message}
        response = invoke(payload)
        
        # Processar resposta
        if response.get('status') == 'conversational':
            return jsonify({
                'response': response.get('response'),
                'type': 'conversational'
            })
        elif response.get('status') == 'success':
            result = {
                'response': response.get('ai_insights', 'Análise concluída!'),
                'type': 'analysis',
                'pdf_filename': response.get('pdf_filename'),
                'email_sent': response.get('email_sent', False)
            }
            
            if response.get('email_message'):
                result['email_message'] = response.get('email_message')
                
            return jsonify(result)
        else:
            return jsonify({
                'response': f"Erro: {response.get('result', 'Erro desconhecido')}",
                'type': 'error'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 INICIANDO FRONTEND WEB - AGENTE IA SICREDI")
    print("=" * 50)
    print("🚀 Servidor iniciando em: http://localhost:5000")
    print("💬 Interface de chat disponível no navegador")
    print("🤖 Agente de IA integrado")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
