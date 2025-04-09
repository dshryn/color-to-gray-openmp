import matplotlib.pyplot as plt
import subprocess
import re
import os

IMAGE_FILE = "image.png"  

def run_cpp_program():
    try:
        # take image
        result = subprocess.run(
            ["parallel_gray.exe"],
            input=IMAGE_FILE + "\n",         
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout

        data_match = re.search(r'-------Data Start-------\n(.*?)\n-------Data End-------', output, re.DOTALL)
        if not data_match:
            print("Error: Could not find data markers in output")
            return None

        data_lines = [line.strip() for line in data_match.group(1).split('\n') if line.strip()]
        if len(data_lines) != 11:
            print(f"Error: Expected 11 data points, got {len(data_lines)}")
            return None

        return {
            'initial_mem': float(data_lines[0]),
            'width': int(data_lines[1]),
            'height': int(data_lines[2]),
            'channels': int(data_lines[3]),
            'seq_before': float(data_lines[4]),
            'seq_after': float(data_lines[5]),
            'seq_time': float(data_lines[6]),
            'par_before': float(data_lines[7]),
            'par_after': float(data_lines[8]),
            'par_time': float(data_lines[9]),
            'final_mem': float(data_lines[10])
        }
    except Exception as e:
        print(f"Error while running C++ program: {str(e)}")
        return None

def create_plots(data):
    try:
        # memory timeline
        plt.figure(figsize=(10, 5))
        timeline = [0, 20, 40, 60, 80, 100]
        memory = [
            data['initial_mem'],
            data['seq_before'],
            data['seq_after'],
            data['par_before'],
            data['par_after'],
            data['final_mem']
        ]
        labels = ["Initial", "Load", "Seq End", "Par Start", "Par End", "Final"]

        plt.plot(timeline, memory, 'b-o')
        for t, m, l in zip(timeline, memory, labels):
            plt.annotate(f"{l}\n{m:.0f} KB", (t, m), textcoords="offset points", xytext=(0, 10), ha='center')

        plt.title("Memory Consumption Timeline")
        plt.xlabel("Execution Timeline (%)")
        plt.ylabel("Memory (KB)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("memory_timeline.png")

        # Performance Comparison Plot
        plt.figure(figsize=(10, 5))
        labels = ['Sequential', 'Parallel']
        times = [data['seq_time'], data['par_time']]
        mem_diffs = [
            data['seq_after'] - data['seq_before'],
            data['par_after'] - data['par_before']
        ]

        bar1 = plt.bar(labels, times, color=['blue', 'orange'], label='Time (s)')
        bar2 = plt.bar(labels, mem_diffs, bottom=times, color=['green', 'red'], label='Mem Δ (KB)')

        plt.title("Performance Comparison")
        plt.ylabel("Time (s) + Memory Difference (KB)")
        plt.legend()
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.savefig("performance_comparison.png")

        plt.show()
        return True
    except Exception as e:
        print(f"Plotting error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running analysis...")

    if not os.path.exists("parallel_gray.exe"):
        print("Error: parallel_gray.exe not found!")
        print("Please compile first with: g++ -fopenmp -o parallel_gray grayscale.cpp -I. -lpsapi")
        exit(1)

    if not os.path.exists(IMAGE_FILE):
        print(f"Error: Input image '{IMAGE_FILE}' not found!")
        exit(1)

    data = run_cpp_program()
    if data:
        if create_plots(data):
            print("Graphs generated-")
            print("- memory_timeline.png")
            print("- performance_comparison.png")
    else:
        print("Failed to generate graphs")

    input("Press Enter to exit...")
