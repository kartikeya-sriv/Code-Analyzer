from flask import Flask, request, jsonify
import subprocess
import os
import re
import sys
from io import StringIO
from pythonds.basic import *
from flask_cors import CORS
from math import *


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Dummy data (replace with your actual data)
student_list = {}

# Global arrays to store extracted information
pylint_ratings = []
total_class_scores = []
avg_function_scores = []
avg_method_scores = []
comments =[]

@app.route('/', methods=['GET', 'POST'])
def handler1():
    global pylint_ratings, total_class_scores, avg_function_scores, avg_method_scores

    folder_path = 'input'

    delete_python_files(folder_path)
    # Retrieve student_id from the request body
    request_data = request.get_json()
    student_id = request_data.get('student_id')
    file_to_run = f"c:/Stuff/CPP/.vscode/py/data/{student_id}.txt"
    extract_script = 'extract.py'
    command = ["python", extract_script, file_to_run]
    subprocess.run(command, check=True)

    

    # Replace 'path/to/your/python_script.py' with the actual path to your Python script
    python_script_path = 'base.py'
    counter = 0
    # Iterate through files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file has a .py extension (you can modify this condition as needed)
        if filename.endswith('.py'):
            counter += 1
            # Build the full path to the Python script for each file
            file_path = os.path.join(folder_path, filename)

            # Run the Python script for each file
            command = ['python', python_script_path, file_path]
            completed_process = subprocess.run(command, check=True)
            with open('output.txt', 'r') as file:
                output= file.read()
            # Extract the information
            pylint_rating = extract_pylint_info(output)
            radon_info = extract_radon_info(output)
            total_class_score, avg_function_score, avg_method_score = calculate_scores(radon_info)
            num_comments = extract_number_of_comments(output)
            comments.append(num_comments)
            # Append the extracted information to the global arrays
            pylint_ratings.append(pylint_rating)
            total_class_scores.append(total_class_score)
            avg_function_scores.append(avg_function_score)
            avg_method_scores.append(avg_method_score)

    return jsonify({
        'pylint_ratings': pylint_ratings,
        'total_class_scores': total_class_scores,
        'avg_function_scores': avg_function_scores,
        'avg_method_scores': avg_method_scores,
        'num_comments':comments,
        'num_of_buttons': counter
    })


@app.route('/codeblock', methods=['GET', 'POST'])
def handler():
    request_data = request.get_json()
    code_block_id = request_data.get('code_block_id')
    file_to_run = f"c:/Stuff/CPP/.vscode/py/input/code_block_{code_block_id}.py"
    output = run_python_file(file_to_run)
    with open(file_to_run, 'r') as file:
        code = file.read()
    pylint_output = check_code_quality(file_to_run)
    rating = extract_pylint_info(pylint_output)
    statements = extract_pylint_statements(pylint_output)
    return jsonify({
        'Pylint_Rating':rating,
        'Statements':statements,
        'Output':output,
        'Code': code
    })


def check_code_quality(file_path):
    # Static code analysis with pylint
    pylint_output = run_command(['pylint', file_path])
    return pylint_output

def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()

def run_python_file(file_path):
    # Capture the current sys.stdout
    original_stdout = sys.stdout

    # Redirect sys.stdout to capture the output
    sys.stdout = StringIO()

    try:
        # Run the Python file using exec
        with open(file_path, 'r') as file:
            code = file.read()
            exec(code)
    except Exception as e:
        # Handle exceptions if needed
        output = f"Error: {str(e)}"
    else:
        # Get the captured output
        output = sys.stdout.getvalue()

    finally:
        # Restore the original sys.stdout
        sys.stdout = original_stdout

    return output

def delete_python_files(directory_path):
        try:
            # List all files in the directory
            files = os.listdir(directory_path)

            # Iterate through the files
            for file in files:
                # Check if the file ends with '.py'
                if file.endswith(".py"):
                    # Construct the full file path
                    file_path = os.path.join(directory_path, file)

                    # Delete the file
                    os.remove(file_path)

        except Exception as e:
            print(f"An error occurred: {e}")

def extract_number_of_comments(output):
    comment_pattern = re.compile(r'(\d+)$')  # Match digits at the end of the string
    match = comment_pattern.search(output)
    
    if match:
        return int(match.group(1))
    else:
        return None

def extract_pylint_info(output):
    pylint_rating_pattern = re.compile(r'Your code has been rated at (\S+)/\S+')
    pylint_rating_match = pylint_rating_pattern.search(output)
    
    if pylint_rating_match:
        pylint_rating = pylint_rating_match.group(1)
        return pylint_rating
    else:
        return None

def extract_pylint_statements(output):
    pylint_pattern = re.compile(r'\d:\d: (\S+: .+)')
    statements = pylint_pattern.findall(output)
    
    if statements:
        # Remove the numeric part at the start in each statement
        statements = [re.sub(r'^\S+: ', '', statement) for statement in statements]
        return statements
    else:
        return None

def extract_radon_info(output):
    radon_pattern = re.compile(r'(\S+\s+\d+:\d+ .+? - . \(\d+\))')

    matches = radon_pattern.findall(output)
    
    if matches:
        return matches
    else:
        return None

def calculate_scores(radon_info):
    if radon_info is None:
        return 0, 0, 0
    class_scores = []
    function_scores = []
    method_scores = []

    for entry in radon_info:
        score = int(re.search(r'\(\d+\)', entry).group(0)[1:-1])  # Extracting the score from the entry
        if entry.startswith('C'):
            class_scores.append(score)
        elif entry.startswith('F'):
            function_scores.append(score)
        elif entry.startswith('M'):
            method_scores.append(score)

    total_class_score = sum(class_scores)
    avg_function_score = sum(function_scores) / len(function_scores) if len(function_scores) > 0 else 0
    avg_method_score = sum(method_scores) / len(method_scores) if len(method_scores) > 0 else 0

    return total_class_score, avg_function_score, avg_method_score
# Read output from file

# Extract information




        #return jsonify(student_info)
    #else:
     #   return jsonify({'error': 'Student not found'}), 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
