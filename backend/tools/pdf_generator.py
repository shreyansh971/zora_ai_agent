# backend/tools/pdf_generator.py
# Generates the "Research Receipt" PDF using Jinja2 + WeasyPrint

import os
import logging
from datetime import datetime
from typing import List
from jinja2 import Template

from backend.models import ZoraSession

logger = logging.getLogger("vera.pdf")

RECEIPT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Space Grotesk', sans-serif;
    background: #0a0a0f;
    color: #e8e8f0;
    padding: 40px;
    font-size: 12px;
    line-height: 1.6;
  }

  .receipt-header {
    border: 2px solid #7c3aed;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 32px;
    background: linear-gradient(135deg, #1a1030 0%, #0f0a20 100%);
    text-align: center;
  }

  .vera-logo {
    font-size: 28px;
    font-weight: 700;
    color: #a78bfa;
    letter-spacing: 4px;
    text-transform: uppercase;
  }

  .vera-subtitle {
    color: #6d6d8a;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
  }

  .vera-id {
    margin-top: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #7c3aed;
    background: #1a0f30;
    display: inline-block;
    padding: 4px 12px;
    border-radius: 4px;
    border: 1px solid #4c1d95;
  }

  .section {
    margin-bottom: 28px;
    page-break-inside: avoid;
  }

  .section-title {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #7c3aed;
    border-bottom: 1px solid #2d1b69;
    padding-bottom: 6px;
    margin-bottom: 14px;
  }

  .score-box {
    display: inline-block;
    padding: 16px 32px;
    border-radius: 8px;
    background: {% if integrity_score >= 80 %}#052e16{% elif integrity_score >= 60 %}#1c1f09{% else %}#2d0d0d{% endif %};
    border: 2px solid {% if integrity_score >= 80 %}#16a34a{% elif integrity_score >= 60 %}#ca8a04{% else %}#dc2626{% endif %};
    text-align: center;
    margin-bottom: 12px;
  }

  .score-number {
    font-size: 36px;
    font-weight: 700;
    color: {% if integrity_score >= 80 %}#4ade80{% elif integrity_score >= 60 %}#fbbf24{% else %}#f87171{% endif %};
  }

  .score-label {
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6d6d8a;
  }

  .source-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
  }

  .source-table th {
    background: #1a1030;
    color: #a78bfa;
    padding: 8px 10px;
    text-align: left;
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border: 1px solid #2d1b69;
  }

  .source-table td {
    padding: 8px 10px;
    border: 1px solid #1a1030;
    vertical-align: top;
    color: #c4c4d4;
  }

  .source-table tr:nth-child(even) td {
    background: #0d0d18;
  }

  .reliability-bar {
    height: 6px;
    background: #1a1030;
    border-radius: 3px;
    overflow: hidden;
    width: 80px;
    display: inline-block;
    vertical-align: middle;
  }

  .reliability-fill {
    height: 100%;
    background: linear-gradient(90deg, #7c3aed, #a78bfa);
    border-radius: 3px;
  }

  .chunk-item {
    padding: 10px 12px;
    margin-bottom: 6px;
    border-radius: 4px;
    border-left: 3px solid transparent;
    font-size: 11px;
  }

  .chunk-verified {
    background: #052e16;
    border-left-color: #16a34a;
  }

  .chunk-hallucinated {
    background: #2d0d0d;
    border-left-color: #dc2626;
  }

  .chunk-partial {
    background: #1c1409;
    border-left-color: #d97706;
  }

  .chunk-unverifiable {
    background: #0f0f1a;
    border-left-color: #6b7280;
  }

  .chunk-badge {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 3px;
    margin-right: 8px;
  }

  .badge-verified { background: #14532d; color: #4ade80; }
  .badge-hallucinated { background: #450a0a; color: #f87171; }
  .badge-partial { background: #451a03; color: #fbbf24; }
  .badge-unverifiable { background: #1f2937; color: #9ca3af; }

  .interaction-item {
    padding: 8px 12px;
    margin-bottom: 4px;
    background: #0d0d18;
    border-radius: 4px;
    border: 1px solid #1a1030;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #9ca3af;
  }

  .interaction-role {
    color: #7c3aed;
    font-weight: 600;
    margin-right: 8px;
  }

  .footer {
    margin-top: 40px;
    text-align: center;
    font-size: 9px;
    color: #3d3d5c;
    letter-spacing: 1px;
    border-top: 1px solid #1a1030;
    padding-top: 16px;
  }

  .query-tag {
    display: inline-block;
    background: #1a0f30;
    border: 1px solid #4c1d95;
    border-radius: 3px;
    padding: 3px 8px;
    font-size: 10px;
    color: #a78bfa;
    margin: 2px;
    font-family: 'JetBrains Mono', monospace;
  }
</style>
</head>
<body>

<!-- HEADER -->
<div class="receipt-header">
  <div class="vera-logo">ZORA</div>
  <div class="vera-subtitle">The Integrity Agent · Research Receipt</div>
  <div class="vera-id">ZORA-ID: {{ session_id }} · {{ timestamp }}</div>
</div>

<!-- INTEGRITY SCORE -->
<div class="section">
  <div class="section-title">🏆 Integrity Score</div>
  <div class="score-box">
    <div class="score-number">{{ integrity_score }}%</div>
    <div class="score-label">Verified Claims / Total Claims</div>
  </div>
  <p style="color: #6d6d8a; font-size: 11px; margin-top: 8px;">
    Topic: <strong style="color: #e8e8f0;">{{ topic }}</strong> ·
    Verified: {{ verified_count }} / {{ total_claims }} claims ·
    Generated: {{ timestamp }}
  </p>
</div>

<!-- SOURCE MAP -->
<div class="section">
  <div class="section-title">📚 Source Map</div>
  <table class="source-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>Title</th>
        <th>Author</th>
        <th>Date</th>
        <th>Reliability</th>
        <th>URL</th>
      </tr>
    </thead>
    <tbody>
      {% for source in sources %}
      <tr>
        <td><strong>{{ source.id }}</strong></td>
        <td>{{ source.title[:60] }}</td>
        <td>{{ source.author or 'Unknown' }}</td>
        <td>{{ source.date or 'n.d.' }}</td>
        <td>
          <div class="reliability-bar">
            <div class="reliability-fill" style="width: {{ (source.reliability_score * 100)|int }}%"></div>
          </div>
          {{ (source.reliability_score * 100)|int }}%
        </td>
        <td style="font-family: monospace; font-size: 9px; color: #7c3aed;">{{ source.url[:50] }}...</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<!-- SEARCH QUERIES -->
<div class="section">
  <div class="section-title">🔍 Search Queries Executed</div>
  {% for q in queries %}
  <span class="query-tag">{{ q }}</span>
  {% endfor %}
</div>

<!-- VERIFICATION LOG -->
<div class="section">
  <div class="section-title">✅ Claim Verification Log</div>
  {% for chunk in verification_log %}
  <div class="chunk-item chunk-{{ chunk.status|lower }}">
    <span class="chunk-badge badge-{{ chunk.status|lower }}">{{ chunk.status }}</span>
    <span>{{ chunk.chunk }}</span>
    {% if chunk.source_ref %}<span style="color: #6d6d8a; font-size: 10px;"> → [{{ chunk.source_ref }}]</span>{% endif %}
    {% if chunk.suggestion %}<div style="margin-top: 4px; color: #fbbf24; font-size: 10px;">💡 {{ chunk.suggestion }}</div>{% endif %}
  </div>
  {% endfor %}
</div>

<!-- INTERACTION LOG -->
{% if interaction_log %}
<div class="section">
  <div class="section-title">💬 Interaction Log (Proves Human Oversight)</div>
  {% for log in interaction_log %}
  <div class="interaction-item">
    <span class="interaction-role">{{ log.role|upper }}</span>{{ log.content[:120] }}
  </div>
  {% endfor %}
</div>
{% endif %}

<!-- BIBLIOGRAPHY -->
<div class="section">
  <div class="section-title">📖 APA Bibliography</div>
  {% for citation in bibliography %}
  <p style="font-size: 10px; color: #9ca3af; margin-bottom: 6px; padding-left: 20px; text-indent: -20px;">{{ citation }}</p>
  {% endfor %}
</div>

<div class="footer">
  ZORA · The Integrity Agent · This receipt certifies that the above research process was conducted transparently.<br>
  Generated automatically — verify independently at your institution.
</div>

</body>
</html>
"""


def generate_receipt_pdf(session: ZoraSession, bibliography: List[str]) -> str:
    """Generate the Research Receipt PDF. Returns the output file path."""
    from backend.agents.citation_specialist import generate_bibliography
    from backend.agents.verifier import calculate_integrity_score

    output_dir = os.getenv("PDF_OUTPUT_PATH", "./output/receipts")
    os.makedirs(output_dir, exist_ok=True)

    verification_log = session.research_trail.verification_log
    verified_count = sum(1 for v in verification_log if v.status == "Verified")

    template = Template(RECEIPT_TEMPLATE)
    html_content = template.render(
        session_id=session.session_id[:12].upper(),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        topic=session.metadata.topic,
        integrity_score=session.integrity_score or 0.0,
        sources=session.research_trail.sources,
        queries=session.research_trail.queries,
        verification_log=verification_log,
        interaction_log=session.interaction_log[-10:],
        bibliography=bibliography,
        verified_count=verified_count,
        total_claims=len(verification_log),
    )

    pdf_path = os.path.join(output_dir, f"zora_receipt_{session.session_id[:8]}.pdf")

    try:
        import weasyprint
        weasyprint.HTML(string=html_content).write_pdf(pdf_path)
        logger.info(f"PDF receipt saved: {pdf_path}")
    except Exception as e:
        logger.warning(f"WeasyPrint failed ({e}), saving HTML fallback.")
        html_path = pdf_path.replace(".pdf", ".html")
        with open(html_path, "w") as f:
            f.write(html_content)
        return html_path

    return pdf_path
