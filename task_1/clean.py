with open('index.txt', 'r') as file:
    lines = file.readlines()
    unique_lines = set(lines)

with open('index.txt', 'w') as file:
    for line in unique_lines:
        file.write(line)
