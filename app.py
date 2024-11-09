from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace with your Hugging Face API key
API_KEY = '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'
HEADERS = {
    'Authorization': f'Bearer {API_KEY}'
}

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    action = data.get('action', '')
    
    if action == 'generate':
        keywords = data.get('keywords', '')
        
        # Send request to Hugging Face Inference API for generation
        response = requests.post(
            'https://api-inference.huggingface.co/models/openai-community/gpt2',
            headers=HEADERS,
            json={'inputs': keywords, 'parameters': {'max_length': 1500, 'min_length': 1024, 'num_return_sequences': 1,'temperature': 0.3, 'top_p': 0.9,'top_k': 50,'repetition_penalty': 1.2}}
        )
        
        if response.status_code == 200:
            # Safely handle the response
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                generated_text = response_data[0].get('generated_text', '')
                
                # Post-process the generated text to remove duplicate sections
                if generated_text:
                    # Simple way to remove duplicates based on sentence-level comparison
                    lines = generated_text.split('\n')
                    seen = set()
                    cleaned_lines = []
                    for line in lines:
                        if line not in seen:
                            cleaned_lines.append(line)
                            seen.add(line)
                    cleaned_text = "\n".join(cleaned_lines)
                else:
                    cleaned_text = generated_text
                
                return jsonify({'article': cleaned_text})
            else:
                return jsonify({'error': 'No generated text found'}), 500
        else:
            return jsonify({'error': 'Request failed', 'details': response.text}), response.status_code


    elif action == 'summarize':
        article = data.get('article', '')
        # Send request to Hugging Face Inference API for summarization
        response = requests.post(
            'https://api-inference.huggingface.co/models/facebook/bart-large-cnn',
            headers=HEADERS,
            json={'inputs': article, 'parameters': {'max_length': 300, 'min_length': 100, 'do_sample': False}}
        )
        
        if response.status_code == 200:
            response_data = response.json()
            summary = response_data[0].get('summary_text', '')
            return jsonify({'summary': summary})
        else:
            return jsonify({'error': 'Request failed', 'details': response.text}), response.status_code

    else:
        return jsonify({'error': 'Invalid action. Use "generate" or "summarize".'}), 400

if __name__ == '__main__':
    app.run(debug=True)
