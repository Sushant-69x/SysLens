import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE = "http://127.0.0.1:5000"

st.set_page_config(page_title="SysLens", layout="wide")
st.title("SysLens — System Monitor")

def get(endpoint):
    try:
        return requests.get(f"{API_BASE}{endpoint}").json()
    except:
        return {}

latest = get("/api/metrics/latest")
alerts = get("/api/alerts")
processes = get("/api/processes")
history = get("/api/metrics/history")
auth_events = get("/api/auth/events")
brute_force = get("/api/auth/brute-force")
auth_summary = get("/api/auth/summary")

st.subheader("System Health")
col1, col2, col3 = st.columns(3)
cpu = latest.get("cpu", {})
mem = latest.get("memory", {})
disk = latest.get("disk", {})
col1.metric("CPU Usage", f"{cpu.get('cpu_percent', 'N/A')}%")
col2.metric("RAM Usage", f"{mem.get('percent_used', 'N/A')}%")
col3.metric("Disk Usage", f"{disk.get('percent_used', 'N/A')}%")

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("CPU History (Last 1 Hour)")
    cpu_history = history.get("cpu", [])
    if cpu_history:
        df_cpu = pd.DataFrame(cpu_history)
        fig = px.line(df_cpu, x="timestamp", y="cpu_percent", title="CPU Usage %")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No CPU history yet.")

with col_right:
    st.subheader("RAM History (Last 1 Hour)")
    mem_history = history.get("memory", [])
    if mem_history:
        df_mem = pd.DataFrame(mem_history)
        fig2 = px.line(df_mem, x="timestamp", y="percent_used", title="RAM Usage %")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No RAM history yet.")

st.divider()

st.subheader("Top Processes (by Memory)")
procs = processes.get("processes", [])
if procs:
    df_proc = pd.DataFrame(procs)[["pid", "name", "cpu_percent", "memory_percent", "status", "username"]]
    st.dataframe(df_proc, use_container_width=True)

st.divider()

st.subheader("Security Monitor")
sec_col1, sec_col2 = st.columns(2)

with sec_col1:
    st.markdown("**Auth Event Summary**")
    summary = auth_summary.get("summary", [])
    if summary:
        df_summary = pd.DataFrame(summary)
        fig3 = px.bar(df_summary, x="event_type", y="count", title="Auth Events by Type")
        st.plotly_chart(fig3, use_container_width=True)

with sec_col2:
    st.markdown("**Brute Force Detection**")
    bf_list = brute_force.get("brute_force_ips", [])
    if bf_list:
        df_bf = pd.DataFrame(bf_list)
        st.dataframe(df_bf, use_container_width=True)
    else:
        st.success("No brute force activity detected.")

st.markdown("**Recent Auth Events**")
auth_list = auth_events.get("auth_events", [])
if auth_list:
    df_auth = pd.DataFrame(auth_list)[["timestamp", "event_type", "username", "source_ip", "service"]]
    st.dataframe(df_auth, use_container_width=True)

st.divider()

st.subheader("Alerts")
alert_list = alerts.get("alerts", [])
if alert_list:
    df_alerts = pd.DataFrame(alert_list)[["timestamp", "alert_type", "severity", "description"]]
    st.dataframe(df_alerts, use_container_width=True)
else:
    st.success("No alerts.")