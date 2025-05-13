import random
import pdb
import argparse
import datetime

ram_path = "/home/ceadeus/Main/Organization/ObsidianVaults/Introspection_und_Organisation/0_most_important_pages/RAM - List.md"
ram_path = "./test_ram_file.txt"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Script for showing, adding and checking off todos from a daily todo-list. Plus some more nice features"
    )

    parser.add_argument(
        "mode",
        help="can be type 'show' (default), 'add', 'done' or 'del'"
    )

    parser.add_argument(
        "-n", "--name",
        metavar="TASK",
        help="The task name to be added, checked off, shown or deleted"
    )
    parser.add_argument(
        "-i", "--id",
        type=int,
        metavar="TASK_ID",
        help="Instead of task name it is also possible to provide a task id for the show, done, and del modes"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (so far unused)"
    )

    args = parser.parse_args()

    #     if args.verbose:
    #         print(f"[VERBOSE] Reading from {args.input_file}")
    #         print(f"[VERBOSE] Writing to   {args.output}")

    # Your processing logic here
    # with open(args.input_file) as fin, open(args.output, "w") as fout:
    #     for line in fin:
    #     fout.write(line)

    return args


if __name__ == "__main__":
    args = parse_args()
    cur_date = datetime.datetime.now().strftime("%d.%m.%Y")

    lines = None
    tasks = []
    with open(ram_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if (line == ""):
                continue
            if (line.startswith("#") and "cur_date" not in line):
                break
            if (not line.startswith("#")):
                tasks.append(line)

    if args.id is not None:
        tasks = [task for (i, task) in enumerate(tasks) if i == args.id]

    if args.name is not None:
        tasks = [task for task in tasks if args.name.upper() in task.upper()]

    if args.mode == "show":
        print(cur_date)
        for i, task in enumerate(tasks):
            print(f"{i} {task}")

    def select_random_task(tasks):
        return random.choice(tasks)
    random_task = select_random_task(tasks)

    if args.mode == 'add':
        with open(ram_path, "w") as file:
            has_added_line = False
            for i in range(len(lines)):
                if ("txt" in lines[i] and not has_added_line):
                    lines[i] += "\t - [ ] Hello World\n"
                    has_added_line = True
                    # lines[i] = lines[i].replace("[ ]", "[x]")
            # lines.append("apples\n")
            file.writelines(lines)
