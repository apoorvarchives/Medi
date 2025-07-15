# --------------------------- visualize.py ---------------------------
import os
import subprocess
from graphviz import Digraph

def visualize_chain(chain, round_num):
    os.makedirs("visualizations", exist_ok=True)

    dot = Digraph(comment=f"Blockchain Round {round_num}")

    # Layout & resolution settings
    dot.attr(rankdir='LR')         # left-to-right layout
    dot.attr(dpi='300')            # high resolution
    dot.attr(size='10,5')          # canvas size

    for i, block in enumerate(chain.chain):
        label = f"Block #{block.index}\nMiner: {block.miner}"

        # Attach accuracy info if available
        for log in block.access_logs:
            if "accuracy" in log:
                label += f"\nAcc: {log['accuracy']:.2f}%"
                break

        label += f"\nPatients: {len(block.records)}"

        dot.node(str(i), label, shape='box', style='filled', color='lightblue')

        if i > 0:
            dot.edge(str(i - 1), str(i))

    # Save and render
    output_path = f"visualizations/blockchain_round_{round_num}"
    dot.render(output_path, format='png', cleanup=True)

    # Auto-open image on macOS
    img_path = output_path + ".png"
    if os.name == "posix":  # macOS/Linux
        try:
            subprocess.run(["open", img_path])
        except Exception:
            pass
