from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/calculate-iban', methods=['POST'])
def calculate_iban():
    """Convert UK sort code + account number to IBAN"""
    try:
        data = request.json
        sort_code = str(data.get('sort_code', '')).replace('-', '').replace(' ', '')
        account_number = str(data.get('account_number', '')).zfill(8)
        account_holder = str(data.get('account_holder_name', ''))
        
        # Validate
        if len(sort_code) != 6 or not sort_code.isdigit():
            return jsonify({'error': 'Invalid sort code. Must be 6 digits.'}), 400
        
        if len(account_number) != 8 or not account_number.isdigit():
            return jsonify({'error': 'Invalid account number. Must be 8 digits.'}), 400
        
        # Calculate IBAN check digits (MOD-97 algorithm)
        rearranged = sort_code + account_number + '1627'  # GB = 1627
        remainder = 0
        for digit in rearranged:
            remainder = (remainder * 10 + int(digit)) % 97
        
        check_digits = str(98 - remainder).zfill(2)
        iban = f'GB{check_digits}{sort_code}{account_number}'
        
        return jsonify({
            'success': True,
            'iban': iban,
            'last4': account_number[-4:],
            'account_holder': account_holder
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)