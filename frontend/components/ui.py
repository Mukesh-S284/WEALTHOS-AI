"""WealthOS AI — Reusable UI components and styling helpers for Streamlit."""

import streamlit as st
from typing import Optional, List, Dict, Any


def apply_custom_css():
    """Apply modern financial dashboard styling."""
    st.markdown("""
    <style>
        /* Modern theme variables */
        :root {
            --primary: #0F172A;
            --accent: #2563EB;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --card-bg: #FFFFFF;
        }

        .metric-card {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 12px;
            transition: all 0.2s ease-in-out;
        }
        .metric-card:hover {
            border-color: #CBD5E1;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        .metric-label {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
        }
        .metric-subtitle {
            font-size: 0.8rem;
            color: #64748B;
            margin-top: 4px;
        }
        .badge-safe {
            background-color: #DCFCE7;
            color: #166534;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-warning {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-danger {
            background-color: #FEE2E2;
            color: #991B1B;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .regulatory-banner {
            background-color: #F1F5F9;
            border-left: 4px solid #64748B;
            padding: 12px 16px;
            margin-top: 30px;
            font-size: 0.8rem;
            color: #475569;
            border-radius: 0 6px 6px 0;
        }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str, badge: Optional[str] = None):
    """Render consistent page header with optional status badge."""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(title)
        st.caption(subtitle)
    with col2:
        if badge:
            st.markdown(f"<div style='text-align: right; margin-top: 25px;'><span class='badge-safe'>{badge}</span></div>", unsafe_allow_html=True)
    st.markdown("---")


def render_metric_card(label: str, value: str, subtitle: Optional[str] = None, delta_color: str = "normal"):
    """Render structured financial metric block."""
    sub_html = f"<div class='metric-subtitle'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value'>{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_regulatory_disclaimer():
    """Render regulatory and fiduciary disclaimer required by Module M."""
    st.markdown("""
    <div class='regulatory-banner'>
        <strong>Regulatory & Educational Notice:</strong> WealthOS AI is a software intelligence platform designed for personal budgeting, scenario simulation, and educational research. WealthOS AI does not provide licensed fiduciary advice, portfolio management, or individual securities recommendations. Market calculations are based on historical and modeled data. Past performance does not guarantee future results.
    </div>
    """, unsafe_allow_html=True)
