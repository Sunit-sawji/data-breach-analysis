import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime

print("=" * 55)
print("  GLOBAL DATA BREACH ANALYSIS — by Sunit Sawji")
print("=" * 55)

# ── LOAD DATA ──
script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(script_dir, 'breaches.csv'))
df['Records_Lost'] = pd.to_numeric(df['Records_Lost'], errors='coerce').fillna(0)

print(f"[*] Dataset loaded: {len(df)} breach records")
print(f"[*] Time range: {df['Year'].min()} — {df['Year'].max()}")
print(f"[*] Total records exposed: {df['Records_Lost'].sum()/1e9:.2f} Billion")

# ── COLOR PALETTE ──
COLORS = {
    'primary':   '#00f5ff',
    'red':       '#ff2d55',
    'orange':    '#ff8c00',
    'green':     '#00ff88',
    'purple':    '#bf5af2',
    'yellow':    '#ffd60a',
    'bg':        '#010812',
    'bg2':       '#020f1e',
    'panel':     '#041428',
    'text':      '#e0f4ff',
    'muted':     '#5a8aaa',
}

CHART_COLORS = [
    '#00f5ff','#ff2d55','#00ff88','#ff8c00',
    '#bf5af2','#ffd60a','#30d5c8','#ff6b88',
    '#7bed9f','#eccc68'
]

def dark_layout(title):
    return dict(
        title=dict(text=title, font=dict(color=COLORS['primary'], size=16, family='Orbitron, monospace'), x=0.5),
        paper_bgcolor=COLORS['bg2'],
        plot_bgcolor=COLORS['panel'],
        font=dict(color=COLORS['text'], family='Rajdhani, sans-serif', size=13),
        xaxis=dict(gridcolor='rgba(0,245,255,0.08)', zerolinecolor='rgba(0,245,255,0.1)'),
        yaxis=dict(gridcolor='rgba(0,245,255,0.08)', zerolinecolor='rgba(0,245,255,0.1)'),
        margin=dict(t=60, b=40, l=40, r=20),
    )

# ── CHART 1: Breaches Per Year ──
yearly = df.groupby('Year').agg(
    Breach_Count=('Organization','count'),
    Records_Lost=('Records_Lost','sum')
).reset_index()

fig1 = make_subplots(specs=[[{"secondary_y": True}]])
fig1.add_trace(go.Bar(
    x=yearly['Year'], y=yearly['Breach_Count'],
    name='Number of Breaches',
    marker_color=COLORS['primary'],
    marker_line_color='rgba(0,245,255,0.5)',
    marker_line_width=1,
    opacity=0.85
), secondary_y=False)
fig1.add_trace(go.Scatter(
    x=yearly['Year'], y=yearly['Records_Lost']/1e6,
    name='Records Exposed (Millions)',
    line=dict(color=COLORS['red'], width=3),
    mode='lines+markers',
    marker=dict(size=8, color=COLORS['red'])
), secondary_y=True)
fig1.update_layout(**dark_layout('Data Breaches Per Year (2004–2024)'))
fig1.update_yaxes(title_text="Number of Breaches", secondary_y=False, title_font_color=COLORS['primary'])
fig1.update_yaxes(title_text="Records Exposed (Millions)", secondary_y=True, title_font_color=COLORS['red'])
chart1_html = fig1.to_html(full_html=False, include_plotlyjs=False)

# ── CHART 2: Breaches by Industry ──
industry = df.groupby('Industry').agg(
    Count=('Organization','count'),
    Records=('Records_Lost','sum')
).sort_values('Records', ascending=True).reset_index()

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    y=industry['Industry'],
    x=industry['Records']/1e6,
    orientation='h',
    marker=dict(
        color=industry['Records']/1e6,
        colorscale=[[0,'#020f1e'],[0.5,'#0077aa'],[1,'#00f5ff']],
        showscale=False,
        line=dict(color='rgba(0,245,255,0.3)', width=1)
    ),
    text=[f"{v/1e6:.0f}M" for v in industry['Records']],
    textposition='outside',
    textfont=dict(color=COLORS['primary'], size=11)
))
fig2.update_layout(**dark_layout('Records Exposed by Industry (Millions)'))
chart2_html = fig2.to_html(full_html=False, include_plotlyjs=False)

# ── CHART 3: Attack Types Donut ──
attacks = df.groupby('Attack_Type')['Records_Lost'].sum().sort_values(ascending=False).reset_index()
fig3 = go.Figure(go.Pie(
    labels=attacks['Attack_Type'],
    values=attacks['Records_Lost'],
    hole=0.55,
    marker=dict(colors=CHART_COLORS, line=dict(color=COLORS['bg'], width=2)),
    textinfo='label+percent',
    textfont=dict(size=12, color=COLORS['text']),
    hovertemplate='<b>%{label}</b><br>Records: %{value:,.0f}<br>Share: %{percent}<extra></extra>'
))
fig3.add_annotation(
    text=f"<b>{df['Records_Lost'].sum()/1e9:.1f}B</b><br>Total Records",
    x=0.5, y=0.5, showarrow=False,
    font=dict(size=16, color=COLORS['primary'], family='Orbitron, monospace'),
    align='center'
)
fig3.update_layout(**dark_layout('Attack Methods — Records Exposed'))
fig3.update_layout(showlegend=True, legend=dict(
    bgcolor='rgba(0,0,0,0.3)', bordercolor='rgba(0,245,255,0.2)',
    borderwidth=1, font=dict(color=COLORS['text'])
))
chart3_html = fig3.to_html(full_html=False, include_plotlyjs=False)

# ── CHART 4: Top 15 Biggest Breaches ──
top15 = df.nlargest(15, 'Records_Lost').sort_values('Records_Lost')
fig4 = go.Figure(go.Bar(
    y=top15['Organization'] + ' (' + top15['Year'].astype(str) + ')',
    x=top15['Records_Lost']/1e6,
    orientation='h',
    marker=dict(
        color=top15['Records_Lost']/1e6,
        colorscale=[[0,'#ff8c00'],[0.5,'#ff2d55'],[1,'#bf5af2']],
        showscale=False,
        line=dict(color='rgba(255,45,85,0.3)', width=1)
    ),
    text=[f"{v/1e6:.0f}M" if v < 1e9 else f"{v/1e9:.1f}B" for v in top15['Records_Lost']],
    textposition='outside',
    textfont=dict(color=COLORS['text'], size=11)
))
fig4.update_layout(**dark_layout('Top 15 Largest Data Breaches in History'))
chart4_html = fig4.to_html(full_html=False, include_plotlyjs=False)

# ── CHART 5: Country Breakdown ──
countries = df.groupby('Country').agg(
    Breaches=('Organization','count'),
    Records=('Records_Lost','sum')
).sort_values('Breaches', ascending=False).head(10).reset_index()

fig5 = go.Figure()
fig5.add_trace(go.Bar(
    x=countries['Country'], y=countries['Breaches'],
    name='Number of Breaches',
    marker_color=COLORS['cyan'] if 'cyan' in COLORS else COLORS['primary'],
    opacity=0.9
))
fig5.update_layout(**dark_layout('Top Countries by Number of Breaches'))
chart5_html = fig5.to_html(full_html=False, include_plotlyjs=False)

# ── CHART 6: Attack Type Count (Bar) ──
atk_count = df.groupby('Attack_Type').size().sort_values(ascending=False).reset_index()
atk_count.columns = ['Attack_Type','Count']
fig6 = go.Figure(go.Bar(
    x=atk_count['Attack_Type'], y=atk_count['Count'],
    marker=dict(
        color=CHART_COLORS[:len(atk_count)],
        line=dict(color='rgba(0,245,255,0.2)', width=1)
    ),
    text=atk_count['Count'],
    textposition='outside',
    textfont=dict(color=COLORS['text'])
))
fig6.update_layout(**dark_layout('Most Common Attack Types (Frequency)'))
chart6_html = fig6.to_html(full_html=False, include_plotlyjs=False)

# ── KEY STATS ──
total_records  = df['Records_Lost'].sum()
total_breaches = len(df)
biggest_breach = df.loc[df['Records_Lost'].idxmax()]
worst_year     = yearly.loc[yearly['Records_Lost'].idxmax(), 'Year']
top_industry   = df.groupby('Industry')['Records_Lost'].sum().idxmax()
top_attack     = df.groupby('Attack_Type')['Records_Lost'].sum().idxmax()

print(f"[*] Biggest breach: {biggest_breach['Organization']} ({biggest_breach['Year']})")
print(f"[*] Worst year: {worst_year}")
print(f"[*] Most targeted industry: {top_industry}")
print(f"[*] Most common attack: {top_attack}")

# ── GENERATE HTML REPORT ──
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Data Breach Analysis — Sunit Sawji</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --cyan:#00f5ff; --green:#00ff88; --red:#ff2d55;
  --orange:#ff8c00; --yellow:#ffd60a; --purple:#bf5af2;
  --bg:#010812; --bg2:#020f1e; --panel:#041428;
  --text:#e0f4ff; --muted:#5a8aaa; --border:rgba(0,245,255,0.15);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family:'Rajdhani',sans-serif;
  background:var(--bg);
  color:var(--text);
  min-height:100vh;
}}
body::before {{
  content:'';
  position:fixed; inset:0;
  background-image:
    linear-gradient(rgba(0,245,255,0.03) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,245,255,0.03) 1px,transparent 1px);
  background-size:40px 40px;
  pointer-events:none; z-index:0;
}}
.content {{ position:relative; z-index:1; }}

/* HEADER */
header {{
  background:linear-gradient(90deg,rgba(0,245,255,0.05),transparent);
  border-bottom:1px solid var(--border);
  padding:24px 40px;
  position:relative;
}}
header::after {{
  content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--cyan),var(--green),transparent);
}}
.header-top {{ display:flex; justify-content:space-between; align-items:flex-start; }}
.logo {{ font-family:'Orbitron',monospace; font-size:24px; font-weight:900; color:var(--cyan); letter-spacing:4px; text-shadow:0 0 20px rgba(0,245,255,0.5); }}
.logo span {{ color:var(--green); }}
.author {{ font-size:13px; color:var(--muted); letter-spacing:2px; margin-top:4px; }}
.generated {{ font-family:'Orbitron',monospace; font-size:11px; color:var(--muted); letter-spacing:1px; text-align:right; }}
.subtitle {{ font-size:15px; color:var(--muted); margin-top:8px; letter-spacing:1px; }}

/* STAT CARDS */
.stats-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; padding:24px 40px; }}
.stat-card {{
  background:rgba(0,245,255,0.03);
  border:1px solid var(--border);
  padding:20px 24px;
  position:relative;
  clip-path:polygon(0 0,calc(100% - 14px) 0,100% 14px,100% 100%,0 100%);
  transition:all 0.3s;
}}
.stat-card:hover {{ border-color:rgba(0,245,255,0.3); transform:translateY(-2px); }}
.stat-val {{ font-family:'Orbitron',monospace; font-size:30px; font-weight:700; line-height:1; margin-bottom:8px; }}
.stat-label {{ font-size:11px; color:var(--muted); letter-spacing:2px; text-transform:uppercase; }}
.stat-sub {{ font-size:12px; color:var(--muted); margin-top:4px; }}

/* SECTIONS */
.section {{ padding:0 40px 32px; }}
.section-title {{
  font-family:'Orbitron',monospace;
  font-size:13px; color:var(--cyan);
  letter-spacing:3px; margin-bottom:16px;
  padding-bottom:10px;
  border-bottom:1px solid rgba(0,245,255,0.1);
  display:flex; align-items:center; gap:10px;
}}
.section-title::before {{
  content:''; width:4px; height:4px;
  background:var(--cyan); border-radius:50%;
  box-shadow:0 0 8px var(--cyan);
}}
.chart-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
.chart-box {{
  background:var(--bg2);
  border:1px solid var(--border);
  padding:4px;
  position:relative;
}}
.chart-box::before,.chart-box::after {{
  content:''; position:absolute;
  width:10px; height:10px;
  border-color:var(--cyan); border-style:solid;
  opacity:0.5;
}}
.chart-box::before {{ top:-1px; left:-1px; border-width:2px 0 0 2px; }}
.chart-box::after  {{ bottom:-1px; right:-1px; border-width:0 2px 2px 0; }}
.chart-full {{ grid-column:1/-1; }}

/* KEY FINDINGS */
.findings-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }}
.finding-card {{
  padding:16px 20px;
  background:rgba(0,245,255,0.03);
  border:1px solid var(--border);
  border-left:3px solid var(--cyan);
}}
.finding-title {{ font-family:'Orbitron',monospace; font-size:10px; color:var(--cyan); letter-spacing:2px; margin-bottom:8px; }}
.finding-val {{ font-size:18px; font-weight:700; color:var(--text); margin-bottom:4px; }}
.finding-sub {{ font-size:12px; color:var(--muted); line-height:1.5; }}

/* TABLE */
.table-wrap {{ overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{
  font-family:'Orbitron',monospace; font-size:9px;
  color:rgba(0,245,255,0.5); letter-spacing:2px;
  padding:10px 16px; background:rgba(0,0,0,0.3);
  border-bottom:1px solid rgba(0,245,255,0.1);
  text-align:left;
}}
td {{ padding:10px 16px; border-bottom:1px solid rgba(0,245,255,0.05); }}
tr:hover td {{ background:rgba(0,245,255,0.03); }}
.sev-badge {{
  font-family:'Orbitron',monospace; font-size:9px;
  padding:3px 8px; letter-spacing:1px;
}}
.sev-high {{ background:rgba(255,45,85,0.15); color:#ff6b88; border:1px solid rgba(255,45,85,0.3); }}
.sev-med  {{ background:rgba(255,140,0,0.15); color:#ffab40; border:1px solid rgba(255,140,0,0.3); }}
.sev-low  {{ background:rgba(0,255,136,0.1); color:#00ff88; border:1px solid rgba(0,255,136,0.2); }}

/* FOOTER */
footer {{
  text-align:center; padding:24px;
  border-top:1px solid var(--border);
  font-family:'Orbitron',monospace;
  font-size:11px; color:var(--muted); letter-spacing:2px;
}}
footer span {{ color:var(--cyan); }}
</style>
</head>
<body>
<div class="content">

<!-- HEADER -->
<header>
  <div class="header-top">
    <div>
      <div class="logo">◈ DATA<span>-</span>BREACH ANALYSIS</div>
      <div class="author">Analyst: Sunit Sawji &nbsp;·&nbsp; ISC2 CC &nbsp;·&nbsp; Cybersecurity Professional</div>
      <div class="subtitle">Global Data Breach Intelligence Report &nbsp;·&nbsp; 2004 — 2024</div>
    </div>
    <div class="generated">
      Generated: {datetime.now().strftime("%d %B %Y, %H:%M")}<br>
      Dataset: {total_breaches} Breach Records<br>
      Coverage: 20 Years
    </div>
  </div>
</header>

<!-- STAT CARDS -->
<div class="stats-grid">
  <div class="stat-card" style="border-color:rgba(255,45,85,0.25)">
    <div class="stat-val" style="color:#ff2d55;text-shadow:0 0 15px rgba(255,45,85,0.5)">{total_records/1e9:.2f}B</div>
    <div class="stat-label">Total Records Exposed</div>
    <div class="stat-sub">Across all documented breaches</div>
  </div>
  <div class="stat-card" style="border-color:rgba(255,140,0,0.25)">
    <div class="stat-val" style="color:#ff8c00;text-shadow:0 0 15px rgba(255,140,0,0.5)">{total_breaches}</div>
    <div class="stat-label">Total Breaches Analysed</div>
    <div class="stat-sub">2004 to 2024</div>
  </div>
  <div class="stat-card" style="border-color:rgba(0,245,255,0.2)">
    <div class="stat-val" style="color:#00f5ff;text-shadow:0 0 15px rgba(0,245,255,0.4)">{worst_year}</div>
    <div class="stat-label">Worst Year</div>
    <div class="stat-sub">Highest records exposed</div>
  </div>
  <div class="stat-card" style="border-color:rgba(191,90,242,0.25)">
    <div class="stat-val" style="color:#bf5af2;font-size:18px;padding-top:6px">{biggest_breach['Organization']}</div>
    <div class="stat-label">Largest Single Breach</div>
    <div class="stat-sub">{biggest_breach['Records_Lost']/1e9:.1f}B records — {biggest_breach['Year']}</div>
  </div>
</div>

<!-- CHART 1: Timeline -->
<div class="section">
  <div class="section-title">Breach Timeline Analysis</div>
  <div class="chart-box chart-full">{chart1_html}</div>
</div>

<!-- CHARTS 2 & 3 -->
<div class="section">
  <div class="section-title">Industry & Attack Method Analysis</div>
  <div class="chart-grid">
    <div class="chart-box">{chart2_html}</div>
    <div class="chart-box">{chart3_html}</div>
  </div>
</div>

<!-- CHART 4: Top Breaches -->
<div class="section">
  <div class="section-title">Top 15 Largest Breaches in History</div>
  <div class="chart-box chart-full">{chart4_html}</div>
</div>

<!-- CHARTS 5 & 6 -->
<div class="section">
  <div class="section-title">Geographic & Attack Frequency Analysis</div>
  <div class="chart-grid">
    <div class="chart-box">{chart5_html}</div>
    <div class="chart-box">{chart6_html}</div>
  </div>
</div>

<!-- KEY FINDINGS -->
<div class="section">
  <div class="section-title">Key Intelligence Findings</div>
  <div class="findings-grid">
    <div class="finding-card">
      <div class="finding-title">Most Targeted Industry</div>
      <div class="finding-val">{top_industry}</div>
      <div class="finding-sub">Highest volume of records exposed across all breach events in dataset</div>
    </div>
    <div class="finding-card" style="border-left-color:var(--red)">
      <div class="finding-title" style="color:var(--red)">Most Dangerous Attack</div>
      <div class="finding-val">{top_attack}</div>
      <div class="finding-sub">Responsible for the most records stolen across all documented incidents</div>
    </div>
    <div class="finding-card" style="border-left-color:var(--orange)">
      <div class="finding-title" style="color:var(--orange)">Average Breach Size</div>
      <div class="finding-val">{total_records/total_breaches/1e6:.0f}M Records</div>
      <div class="finding-sub">Average records exposed per breach event across 20 year dataset</div>
    </div>
    <div class="finding-card" style="border-left-color:var(--purple)">
      <div class="finding-title" style="color:var(--purple)">Ransomware Rise</div>
      <div class="finding-val">Post 2019</div>
      <div class="finding-sub">Ransomware attacks increased significantly from 2019 onwards targeting critical infrastructure</div>
    </div>
    <div class="finding-card" style="border-left-color:var(--green)">
      <div class="finding-title" style="color:var(--green)">USA Dominance</div>
      <div class="finding-val">{len(df[df['Country']=='USA'])} Breaches</div>
      <div class="finding-sub">USA accounts for the majority of documented breaches due to high digitisation and reporting requirements</div>
    </div>
    <div class="finding-card" style="border-left-color:var(--yellow)">
      <div class="finding-title" style="color:var(--yellow)">Insider Threats</div>
      <div class="finding-val">{len(df[df['Attack_Type']=='Insider Threat'])} Incidents</div>
      <div class="finding-sub">Internal actors remain a significant threat vector despite technical security controls</div>
    </div>
  </div>
</div>

<!-- TOP BREACHES TABLE -->
<div class="section">
  <div class="section-title">Top 20 Breaches — Detailed Record</div>
  <div class="table-wrap">
    <table>
      <tr>
        <th>Year</th><th>Organization</th><th>Industry</th>
        <th>Records Lost</th><th>Attack Type</th><th>Country</th><th>Data Type</th>
      </tr>
      {"".join([f'''<tr>
        <td style="font-family:Orbitron,monospace;color:#5a8aaa;font-size:11px">{r.Year}</td>
        <td style="font-weight:600;color:#e0f4ff">{r.Organization}</td>
        <td style="color:#5a8aaa">{r.Industry}</td>
        <td style="font-family:Orbitron,monospace;color:#ff2d55;font-size:12px">{f"{r.Records_Lost/1e9:.1f}B" if r.Records_Lost>=1e9 else f"{r.Records_Lost/1e6:.0f}M"}</td>
        <td><span class="sev-badge {'sev-high' if r.Attack_Type in ['Hacking','Ransomware','Malware'] else 'sev-med' if r.Attack_Type in ['Phishing','Social Engineering','Supply Chain'] else 'sev-low'}">{r.Attack_Type}</span></td>
        <td style="color:#5a8aaa">{r.Country}</td>
        <td style="color:#7ab8d4;font-size:12px">{r.Sensitivity}</td>
      </tr>''' for _, r in df.nlargest(20,'Records_Lost').iterrows()])}
    </table>
  </div>
</div>

<!-- FOOTER -->
<footer>
  <span>◈ Global Data Breach Analysis</span> &nbsp;·&nbsp;
  Analyst: <span>Sunit Sawji</span> &nbsp;·&nbsp;
  ISC2 Certified in Cybersecurity &nbsp;·&nbsp;
  Generated: {datetime.now().strftime("%d %B %Y")}
</footer>

</div>
</body>
</html>"""

# ── SAVE REPORT ──
output_path = os.path.join(script_dir, 'breach_analysis_report.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n{'='*55}")
print(f"  REPORT GENERATED SUCCESSFULLY!")
print(f"{'='*55}")
print(f"  File: breach_analysis_report.html")
print(f"  Open it in your browser to view the full report")
print(f"{'='*55}")
