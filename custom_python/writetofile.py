# write out the input to text file

def write_to_file(file_name, input_to_write):
    with open(file_name, 'w') as file:
        file.write(str(input_to_write))
