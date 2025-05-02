ram_path = "/home/ceadeus/Main/Organization/ObsidianVaults/Introspection_und_Organisation/0_most_important_pages/RAM - List.md"

if __name__ == "__main__":
    with open(ram_path, 'r') as file:
        tasks = []
        for line in file:
            line = line.strip()
            if (line == ""):
                continue
            if (line.startswith("#") and "01.05.2025" not in line):
                break
            if (not line.startswith("#")):
                tasks.append(line)
            print(line)
