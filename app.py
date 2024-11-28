from flask import Flask, request, Response, jsonify, send_from_directory
import subprocess
import os
from tempfile import NamedTemporaryFile

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'homepage.html')

@app.route('/api/align', methods=['POST'])
def align_sequences():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']

    # if not file.filename.endswith('.txt'):
    #     return jsonify({"error": "Invalid file format. Please upload a FASTA file."}), 400

    input_file = NamedTemporaryFile(delete=False, suffix='.fasta')
    output_file = NamedTemporaryFile(delete=False, suffix='.fasta')

    try:
        input_path = input_file.name
        output_path = output_file.name

        file.save(input_path)

        # MAFFT
        # command = f"mafft --auto {input_path} > {output_path}"
        # subprocess.run(command, shell=True, check=True)

        with open(input_path, 'r') as f:
            aligned_data = f.read()

        FASTADict = {}
        FASTALabel = ""
        for line in aligned_data.splitlines():
            if '>' in line:
                FASTALabel = line.strip()
                FASTADict[FASTALabel] = ""
            else:
                FASTADict[FASTALabel] += line.strip().upper()

        sequences = list(FASTADict.values())
        rows = len(sequences)
        cols = len(sequences[0]) if rows > 0 else 0

        # find differing columns    
        mismatched_indices = []
        for col in range(cols):
            ref = sequences[0][col]  # compare with first line
            for row in range(1, rows):
                if sequences[row][col] != ref:
                    mismatched_indices.append(col)
                    break
        # -------------------------------------------------------------------

        results = []
        for label, sequence in FASTADict.items():
            highlighted_sequence = ""
            for i, char in enumerate(sequence):
                if i in mismatched_indices:
                    highlighted_sequence += f"*{char}*"
                else:
                    highlighted_sequence += char
            results.append({"label": label, "sequence": highlighted_sequence})
        # -------------------------------------------------------------------
                    
        print("sent")
        return jsonify(results)
    
    except subprocess.CalledProcessError:
        return jsonify({"error": "MAFFT execution failed."}), 500

    finally:
        os.remove(input_path)
        os.remove(output_path)

if __name__ == '__main__':
    app.run(debug=True)
