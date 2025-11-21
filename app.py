import streamlit as st
import numpy as np
import time
import plotly.graph_objects as go
import pandas as pd

# ------------------ Disk Algorithms ---------------------

def fcfs(requests, head):
    order = [head] + requests
    total = sum(abs(order[i] - order[i - 1]) for i in range(1, len(order)))
    return order, total

def sstf(requests, head):
    reqs = requests.copy()
    order = [head]
    current = head

    while reqs:
        nearest = min(reqs, key=lambda x: abs(x - current))
        order.append(nearest)
        reqs.remove(nearest)
        current = nearest
    
    total = sum(abs(order[i] - order[i - 1]) for i in range(1, len(order)))
    return order, total

def scan(requests, head, disk_size=200):
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])

    # SCAN moves right first, then goes to end, then reverse
    order = [head] + right + [disk_size - 1] + left[::-1]
    total = sum(abs(order[i] - order[i - 1]) for i in range(1, len(order)))
    return order, total

def c_scan(requests, head, disk_size=200):
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])

    # Move in one direction (right), then jump to start
    order = [head] + right + [disk_size - 1, 0] + left
    total = 0
    for i in range(1, len(order)):
        total += abs(order[i] - order[i - 1])
    return order, total

# ------------------ Animation ---------------------

def animate(order,speed):
    st.write("### 🎬 Disk Head Animation")
    fig = go.Figure()

    for i in range(1, len(order)):
        fig.add_trace(go.Scatter(
            x=[order[i - 1], order[i]],
            y=[0, 0],
            mode="lines+markers+text",
            text=[order[i - 1], order[i]],
            textposition="top center"
        ))

        st.plotly_chart(fig, use_container_width=True)
        time.sleep(0.6)

# ------------------ UI ---------------------

st.title("🚀 Advanced Disk Scheduling Simulator")

req_str = st.text_input("Enter disk requests", "82, 170, 43, 140, 24, 16, 190")
head = st.number_input("Starting head position", 0, 500, 50)
disk_size = st.number_input("Disk Size (Cylinders)", 100, 1000, 200)

# Validate Input Requests
def parse_requests(req_str):
    try:
        req_list = list(map(int, req_str.replace(" ", "").split(",")))
        return req_list
    except:
        st.error("❌ Invalid input! Enter numbers separated by commas.")
        return None

# Random Request Generator
if st.button("🎲 Generate Random Requests"):
    import random
    req_str = ", ".join(map(str, random.sample(range(0, disk_size), 8)))
    st.success(f"✅ Random Requests Generated: {req_str}")

algorithms = {
    "FCFS": fcfs,
    "SSTF": sstf,
    "SCAN": lambda r, h: scan(r, h, disk_size),
    "C-SCAN": lambda r, h: c_scan(r, h, disk_size),
}

algo = st.selectbox("Select Algorithm", list(algorithms.keys()))
speed = st.slider("⚡ Animation Speed (sec per move)", 0.1, 1.0, 0.5)

if st.button("Run Simulation"):
    requests = list(map(int, req_str.split(',')))

    selected_algo = algorithms[algo]
    order, total = selected_algo(requests, head)

    avg_seek = total / len(requests)
    throughput = len(requests) / total if total != 0 else 0

    st.success(f"✅ Algorithm: {algo}")
    st.write(f"📌 **Sequence**: {order}")
    st.write(f"📊 **Total Seek Time**: {total}")
    st.write(f"⚙️ **Average Seek Time** = {avg_seek:.2f}")
    st.write(f"🚀 **System Throughput** = {throughput:.4f} requests/unit time")

    animate(order, speed)

if st.button("Compare All Algorithms"):
    
    request_list = list(map(int, req_str.split(',')))   # ✅ Now defined at the correct place

    results = {}
    orders = {}

    for name, fn in algorithms.items():
        order, total = fn(request_list, head)
        results[name] = total
        orders[name] = order

    st.subheader("🔎 Performance Comparison")

    # Display Table
    st.table({
        "Algorithm": list(results.keys()),
        "Total Seek Time": list(results.values()),
        "Avg SeekTime": [results[a] / len(request_list) for a in results],
        "Throughput": [len(request_list) / results[a] if results[a] != 0 else 0 for a in results]
    })

    # 📊 Bar Chart
    fig = go.Figure(data=[go.Bar(x=list(results.keys()), y=list(results.values()))])
    fig.update_layout(title="Seek Time Comparison", xaxis_title="Algorithm", yaxis_title="Total Seek Time")
    st.plotly_chart(fig, use_container_width=True)

    # 📈 Line Chart for Movement
    for name, order in orders.items():
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=list(range(len(order))), y=order, mode="lines+markers"))
        fig2.update_layout(title=f"Head Movement Pattern ({name})",
                           xaxis_title="Step",
                           yaxis_title="Cylinder Number")
        st.plotly_chart(fig2, use_container_width=True)

    # ✅ Export Table to CSV
    df = pd.DataFrame({
        "Algorithm": list(results.keys()),
        "Total Seek Time": list(results.values()),
        "Average Seek Time": [results[a]/len(request_list) for a in results],
        "Throughput (req/unit time)": [len(request_list) / results[a] if results[a] != 0 else 0 for a in results]

    })

    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Download Result as CSV",
        data=csv,
        file_name="disk_scheduling_results.csv",
        mime='text/csv',
    )


if st.button("🔄 Reset"):
    st.rerun()



