import matplotlib.pyplot as plt
import subprocess
import re
import os

def run_cpp_program():
    try:
        # run cpp
        result = subprocess.run(["./parallel_gray.exe"], 
                              capture_output=True, 
                              text=True,
                              check=True)
        output = result.stdout
        
        print("Complete program output:")
        print(output)
        
        # extract 
        data_match = re.search(r'DATA_START\n(.*?)\nDATA_END', output, re.DOTALL)
        if not data_match:
            print("Error: Could not find data markers in output")
            return None
        
        data_lines = [line.strip() for line in data_match.group(1).split('\n') if line.strip()]
        if len(data_lines) != 11:
            print(f"Error: Expected 11 data points, got {len(data_lines)}")
            print("Data received:", data_lines)
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
        
    except subprocess.CalledProcessError as e:
        print(f"Error running C++ program: {e}")
        print("Program stderr:", e.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def create_memory_timeline(data):
    try:
        plt.figure(figsize=(10, 6))
        
        timeline = [0, 20, 30, 50, 60, 80, 100]
        
        memory_values = [
            data['initial_mem'],     
            data['seq_before'],      
            data['seq_before'],      
            data['seq_after'],       
            data['par_before'],      
            data['par_after'],       
            data['final_mem']        
        ]
        
        labels = [
            "Initial",
            "After Loading",
            "Seq Start",
            "Seq End",
            "Par Start",
            "Par End",
            "Final"
        ]
        
        plt.plot(timeline, memory_values, 'b-o', linewidth=2, markersize=8)
        
        for time, mem, label in zip(timeline, memory_values, labels):
            plt.annotate(f"{label}\n{mem:.0f} KB",
                        (time, mem),
                        textcoords="offset points",
                        xytext=(0,10),
                        ha='center',
                        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
        
        plt.title("Memory Consumption Timeline")
        plt.xlabel("Execution Timeline (%)")
        plt.ylabel("Memory Usage (KB)")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(timeline)
        plt.tight_layout()
        plt.savefig("memory_timeline.png", dpi=150)
        plt.show()
        return True
        
    except Exception as e:
        print(f"Error creating memory timeline: {e}")
        return False

def create_performance_comparison(data):
    try:
        plt.figure(figsize=(10, 6))
        
        labels = ['Sequential', 'Parallel']
        time_data = [data['seq_time'], data['par_time']]
        mem_diff = [
            data['seq_after'] - data['seq_before'],
            data['par_after'] - data['par_before']
        ]
        
        bar_width = 0.35
        x = range(len(labels))
        
        time_bars = plt.bar(x, time_data, bar_width, color='blue', label='Time (s)')
        mem_bars = plt.bar([i + bar_width for i in x], mem_diff, bar_width, color='red', label='Mem Increase (KB)')
        
        plt.title("Performance Comparison")
        plt.xlabel("Processing Method")
        plt.ylabel("Time (s) / Memory (KB)")
        plt.xticks([i + bar_width/2 for i in x], labels)
        plt.legend()
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig("performance_comparison.png", dpi=150)
        plt.show()
        return True
        
    except Exception as e:
        print(f"Error creating performance comparison: {e}")
        return False

if __name__ == "__main__":
    print("Running grayscale analysis...")
    
 
    if not os.path.exists("./parallel_gray"):
        print("Error: parallel_gray executable not found in current directory")
        print("Please compile your C++ program first")
        exit(1)
    
    data = run_cpp_program()
    
    if data:
        print("\nData collected successfully:")
        print(f"- Initial memory: {data['initial_mem']} KB")
        print(f"- Sequential time: {data['seq_time']:.6f} s (Mem Δ: {data['seq_after']-data['seq_before']} KB)")
        print(f"- Parallel time: {data['par_time']:.6f} s (Mem Δ: {data['par_after']-data['par_before']} KB)")
        print(f"- Final memory: {data['final_mem']} KB")
        
        success1 = create_memory_timeline(data)
        success2 = create_performance_comparison(data)
        
        if success1 and success2:
            print("\nGraphs generated successfully!")
            print("- Memory timeline: memory_timeline.png")
            print("- Performance comparison: performance_comparison.png")
        else:
            print("\nSome graphs failed to generate")
    else:
        print("\nFailed to collect data from C++ program")
    
    input("\nPress Enter to exit...")