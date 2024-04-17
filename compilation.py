import re

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


def extract_number_of_comments(output):
    comment_pattern = re.compile(r'(\d+)$')  # Match digits at the end of the string
    match = comment_pattern.search(output)
    
    if match:
        return int(match.group(1))
    else:
        return None

# Read output from file
with open('output.txt', 'r') as file:
    output_text = file.read()

# Extract information
pylint_rating = extract_pylint_info(output_text)
pylint_statements = extract_pylint_statements(output_text)
radon_info = extract_radon_info(output_text)
total_class_score, avg_function_score, avg_method_score = calculate_scores(radon_info)
num_comments = extract_number_of_comments(output_text)

# Display the extracted information
print("Pylint Rating:")
print(pylint_rating)
print("\nPylint Statements:")
print(pylint_statements)
print("\nRadon Total Class Score:")
print(total_class_score)
print("\nRadon Average Function Score:")
print(avg_function_score)
print("\nRadon Average Method Score:")
print(avg_method_score)
print("\nNumber of Comments:")
print(num_comments)
