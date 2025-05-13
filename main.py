import random
import pdb

ram_path = "/home/ceadeus/Main/Organization/ObsidianVaults/Introspection_und_Organisation/0_most_important_pages/RAM - List.md"
ram_path = "./test_ram_file.txt"

if __name__ == "__main__":
    lines = None
    tasks = []
    with open(ram_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if (line == ""):
                continue
            if (line.startswith("#") and "01.05.2025" not in line):
                break
            if (not line.startswith("#")):
                tasks.append(line)
            print(line)

    def select_random_task(tasks):
        return random.choice(tasks)
    random_task = select_random_task(tasks)

