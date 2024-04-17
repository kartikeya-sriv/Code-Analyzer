import os
import sys

def separate_code_blocks(file_path, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(file_path, 'r') as file:
        rst_content = file.read()

    # Split the RST content into blocks based on the '.. activecode::' marker
    code_blocks = rst_content.split('.. activecode::')[1:]

    # Extract the code content from each block
    for index, code_block in enumerate(code_blocks, start=1):
        code_start = code_block.find(':code:')
        if code_start != -1:
            code_content = code_block[code_start + len(':code:'):].strip()

            # Remove three spaces at the start of each line
            code_content_with_removed_spaces = '\n'.join(line[3:] if line.startswith('   ') else line for line in code_content.split('\n'))

            # Save the code content to a separate file
            output_file_path = os.path.join(output_directory, f'code_block_{index}.py')
            with open(output_file_path, 'w') as output_file:
                output_file.write(code_content_with_removed_spaces)

            print(f"\nCode Block {index} saved to: {output_file_path}")

if __name__ == "__main__":

    rst_file_path = sys.argv[1]
    
    output_directory = 'c:/Stuff/CPP/.vscode/py/input'

    separate_code_blocks(rst_file_path, output_directory)
