import os
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import base64

# ------------------------------------------------------
# FUNÇÕES BÁSICAS (FINANCEIRO)
# ------------------------------------------------------
def call_payoff(S, K, vol):
    """Payoff de Call: max(0, S - K) * volume"""
    return np.maximum(S - K, 0) * vol

def put_payoff(S, K, vol):
    """Payoff de Put: max(0, K - S) * volume"""
    return np.maximum(K - S, 0) * vol

def calculate_pnl_at_ptax(payoff_func, ptax_vencimento, *args):
    """Calcula PnL em um ponto específico"""
    ptax = np.array([ptax_vencimento])
    return payoff_func(ptax, *args)[0]

def calculate_ndf_pnl(ptax, strike_ndf, vol):
    """Calcula PnL do NDF: (PTAX - strike) * volume"""
    return (ptax - strike_ndf) * vol

# ------------------------------------------------------
# FUNÇÃO PARA CARREGAR LOGO (BASE64)
# ------------------------------------------------------
def encode_image(image_path):
    """Converte imagem para base64 se existir"""
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
    except:
        return None

# ------------------------------------------------------
# DICIONÁRIO DE INFORMAÇÕES DAS ESTRATÉGIAS
# ------------------------------------------------------
ESTRATEGIAS_INFO = {
    "ndf": {
        "titulo": "NDF (Non-Deliverable Forward)",
        "descricao": [
            "✓ Permite fixar o preço da compra de uma moeda estrangeira em uma data futura.",
            "✓ Não há desembolso de caixa no início da operação.",
            "✓ Não há troca física de moedas, no vencimento a operação é liquidada via ajuste financeiro.",
            "✓ Fórmula: Valor da Operação em ME × (Fixing da ME no vencimento – Taxa Forward).",
            "✓ Possibilidade de liquidação antecipada.",
        ],
        "cor": "#00d4ff",
    },
    "call": {
        "titulo": "Call (Opção de Compra)",
        "descricao": [
            "✓ Direito (não obrigação) de comprar moeda estrangeira em uma data futura.",
            "✓ Taxa (strike) pré-determinada no início.",
            "✓ Necessidade de pagamento de prêmio no início da operação.",
            "✓ Protege contra desvalorização do BRL, mantendo upside assimétrico.",
        ],
        "cor": "#00ff88",
    },
    "cs": {
        "titulo": "Call Spread",
        "descricao": [
            "✓ Compra de uma call + venda de outra call com strike superior.",
            "✓ Reduz o custo (prêmio líquido) em relação à call simples.",
            "✓ Ganho limitado ao strike da call vendida.",
        ],
        "cor": "#ff00ff",
    },
    "zcc": {
        "titulo": "Zero Cost Collar",
        "descricao": [
            "✓ Combinação de venda de put + compra de call.",
            "✓ Garante um piso de proteção, limitando o ganho em cenários extremos.",
            "✓ Estrutura de custo zero (ou muito próximo disso).",
        ],
        "cor": "#00ccff",
    },
    "seagull": {
        "titulo": "Seagull",
        "descricao": [
            "✓ Define uma faixa de proteção para o importador.",
            "✓ Reduz o impacto de altas da moeda base acima de certo nível.",
            "✓ Abre mão de parte do ganho em uma desvalorização extrema.",
        ],
        "cor": "#ff3366",
    },
    "fec": {
        "titulo": "Forward Extra Cap",
        "descricao": [
            "✓ Dinâmica semelhante ao NDF, com possibilidade de ajuste positivo extra.",
            "✓ Cliente não tem ajuste negativo desde que não atinja a barreira knock-in.",
            "✓ Composto por NDF + opções com barreira.",
        ],
        "cor": "#33ff99",
    },
    "koki": {
        "titulo": "Estratégia com KO e KI",
        "descricao": [
            "✓ Dinâmica mais complexa, taxa maior que NDF se barreiras não são acionadas.",
            "✓ Protege contra alta relevante da moeda, mas com condicionantes.",
            "✓ Combina calls e puts com barreiras knock-in/knock-out.",
        ],
        "cor": "#ff4444",
    },
}

# ------------------------------------------------------
# PALETA E ESTILOS GERAIS – LAYOUT MODERNO
# ------------------------------------------------------
COLOR_BG = "#050812"
COLOR_BG_CARD = "rgba(17, 24, 39, 0.95)"
COLOR_BG_CARD_SOFT = "rgba(17, 24, 39, 0.8)"
COLOR_ACCENT = "#7C3AED"
COLOR_BORDER = "rgba(148, 163, 184, 0.5)"
COLOR_TEXT = "#E5E7EB"
COLOR_MUTED = "#9CA3AF"

tabs_style = {
    "height": "62px",
    "backgroundColor": COLOR_BG,
    "borderBottom": f"1px solid {COLOR_BORDER}",
}

tab_style = {
    "padding": "14px 18px",
    "fontWeight": "600",
    "backgroundColor": "transparent",
    "color": COLOR_MUTED,
    "border": "none",
    "borderRadius": "10px 10px 0 0",
    "marginRight": "6px",
    "fontSize": "13px",
    "fontFamily": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "transition": "all 0.2s ease-in-out",
}

content_style = {
    "padding": "24px 32px 40px 32px",
    "backgroundColor": COLOR_BG,
    "minHeight": "100vh",
}

input_style = {
    "width": "210px",
    "padding": "10px 12px",
    "fontSize": "14px",
    "backgroundColor": "#020617",
    "color": COLOR_TEXT,
    "border": f"1px solid {COLOR_BORDER}",
    "borderRadius": "8px",
    "fontFamily": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "outline": "none",
}

label_style = {
    "color": COLOR_MUTED,
    "fontWeight": "600",
    "marginBottom": "6px",
    "display": "block",
    "fontFamily": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "fontSize": "12px",
    "textTransform": "uppercase",
    "letterSpacing": "0.06em",
}

container_style = {
    "marginBottom": "20px",
    "backgroundColor": COLOR_BG_CARD,
    "padding": "18px 20px",
    "borderRadius": "14px",
    "border": f"1px solid {COLOR_BORDER}",
    "boxShadow": "0 18px 40px rgba(15, 23, 42, 0.7)",
}

info_box_style = {
    "display": "inline-block",
    "minWidth": "240px",
    "padding": "16px 18px",
    "margin": "10px 10px 10px 0",
    "background": "radial-gradient(circle at top left, rgba(124,58,237,0.15), rgba(15,23,42,0.95))",
    "border": f"1px solid {COLOR_BORDER}",
    "borderRadius": "12px",
    "boxShadow": "0 18px 30px rgba(15, 23, 42, 0.9)",
    "textAlign": "left",
    "backdropFilter": "blur(10px)",
}

info_header_style = {
    "color": COLOR_MUTED,
    "fontSize": "12px",
    "fontWeight": "600",
    "marginBottom": "6px",
    "textTransform": "uppercase",
    "letterSpacing": "0.08em",
}

info_value_style = {
    "color": COLOR_TEXT,
    "fontSize": "24px",
    "fontWeight": "700",
    "margin": "2px 0 4px 0",
    "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
}

# ------------------------------------------------------
# HELPERS DE LAYOUT
# ------------------------------------------------------
def create_input(label, id_name, value, step=0.01):
    return html.Div(
        [
            html.Label(label, style=label_style),
            dcc.Input(
                id=id_name,
                type="number",
                value=value,
                step=step,
                style=input_style,
            ),
        ],
        style={"display": "inline-block", "marginRight": "22px", "marginBottom": "12px"},
    )

def create_info_box(title, value, border_color=COLOR_ACCENT):
    if isinstance(value, (int, float, np.number)):
        value_str = f"R\$ {abs(value):,.0f}"
        value_color = "#10B981" if value >= 0 else "#F97316"
    else:
        value_str = str(value)
        value_color = COLOR_TEXT

    return html.Div(
        [
            html.Div(title, style=info_header_style),
            html.Div(value_str, style={**info_value_style, "color": value_color}),
            html.Div(
                "PnL Estimado",
                style={"color": COLOR_MUTED, "fontSize": "11px", "marginTop": "4px"},
            ),
        ],
        style={**info_box_style, "borderColor": border_color},
    )

def create_simple_pnl_box(title, value, border_color=COLOR_ACCENT):
    if isinstance(value, (int, float, np.number)):
        value_str = f"R\$ {abs(value):,.0f}"
        value_color = "#10B981" if value >= 0 else "#F97316"
    else:
        value_str = str(value)
        value_color = COLOR_TEXT

    return html.Div(
        [
            html.Div(
                title,
                style={
                    "color": COLOR_MUTED,
                    "fontSize": "12px",
                    "fontWeight": "600",
                    "marginBottom": "6px",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.08em",
                },
            ),
            html.Div(
                value_str,
                style={
                    "color": value_color,
                    "fontSize": "22px",
                    "fontWeight": "700",
                    "margin": "2px 0",
                    "fontFamily": info_value_style["fontFamily"],
                },
            ),
        ],
        style={
            "minWidth": "240px",
            "padding": "14px 16px",
            "margin": "8px 8px",
            "backgroundColor": COLOR_BG_CARD_SOFT,
            "border": f"1px solid {border_color}",
            "borderRadius": "12px",
            "boxShadow": "0 14px 24px rgba(15,23,42,0.8)",
            "textAlign": "left",
            "display": "inline-block",
        },
    )

def configure_graph(fig, title, legend_x=1.02, height=600):
    fig.update_layout(
        title={
            "text": title,
            "font": {
                "size": 20,
                "color": COLOR_TEXT,
                "family": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            },
            "x": 0.02,
            "xanchor": "left",
        },
        xaxis_title="PTAX no Vencimento",
        yaxis_title="Payoff (BRL)",
        plot_bgcolor="#020617",
        paper_bgcolor=COLOR_BG_CARD,
        font={
            "color": COLOR_TEXT,
            "family": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "size": 12,
        },
        height=height,
        xaxis={
            "gridcolor": "#1f2937",
            "zerolinecolor": "#4b5563",
            "linecolor": "#4b5563",
            "title_font": {"size": 13, "color": COLOR_MUTED},
            "showgrid": True,
            "tickformat": ".2f",
            "gridwidth": 1,
        },
        yaxis={
            "gridcolor": "#1f2937",
            "zerolinecolor": "#4b5563",
            "linecolor": "#4b5563",
            "title_font": {"size": 13, "color": COLOR_MUTED},
            "showgrid": True,
            "tickformat": ",.0f",
            "gridwidth": 1,
        },
        hovermode="x unified",
        legend={
            "bgcolor": "rgba(15, 23, 42, 0.95)",
            "bordercolor": COLOR_BORDER,
            "borderwidth": 1,
            "font": {"size": 11},
            "x": legend_x,
            "y": 0.5,
            "xanchor": "left",
            "yanchor": "middle",
        },
        margin={"l": 60, "r": 160 if legend_x > 1 else 60, "t": 60, "b": 60},
    )
    return fig

def criar_tooltip_estrategia(estrategia_key):
    info = ESTRATEGIAS_INFO.get(estrategia_key, {})
    if not info:
        return html.Div()

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        "Estratégia",
                        style={
                            "color": COLOR_MUTED,
                            "fontSize": "11px",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.16em",
                            "marginBottom": "2px",
                        },
                    ),
                    html.Div(
                        info["titulo"],
                        style={
                            "fontSize": "18px",
                            "fontWeight": "700",
                            "color": info["cor"],
                        },
                    ),
                ],
                style={"marginBottom": "10px"},
            ),
            html.Div(
                [
                    html.Div(
                        item,
                        style={
                            "color": COLOR_TEXT,
                            "fontSize": "13px",
                            "marginBottom": "4px",
                            "lineHeight": "1.6",
                        },
                    )
                    for item in info["descricao"]
                ]
            ),
        ],
        style={
            "background": "radial-gradient(circle at top left, rgba(56,189,248,0.22), rgba(15,23,42,0.95))",
            "padding": "18px 20px",
            "borderRadius": "14px",
            "border": f"1px solid {info['cor']}",
            "marginBottom": "18px",
            "boxShadow": "0 20px 40px rgba(15,23,42,0.9)",
        },
    )

# ------------------------------------------------------
# HELPER: INPUTS DE UM LEG (SIMULADOR LIVRE)
# ------------------------------------------------------
def create_leg_inputs(index):
    """Cria o conjunto de inputs de um leg de opção para o Simulador Livre."""
    leg_id = f"leg-{index}"

    return html.Div(
        [
            html.Div(
                f"Leg {index}",
                style={
                    "color": COLOR_TEXT,
                    "fontWeight": "700",
                    "marginBottom": "10px",
                    "fontSize": "14px",
                },
            ),
            # Tipo: Call / Put
            html.Div(
                [
                    html.Label("Tipo", style=label_style),
                    dcc.Dropdown(
                        id=f"{leg_id}-tipo",
                        options=[
                            {"label": "Call", "value": "call"},
                            {"label": "Put", "value": "put"},
                        ],
                        value="call",
                        clearable=False,
                        style={
                            **input_style,
                            "width": "170px",
                            "backgroundColor": "#F9FAFB",
                            "border": f"1px solid {COLOR_BORDER}",
                            "color": "#111827",
                        },
                    ),
                ],
                style={"display": "inline-block", "marginRight": "15px"},
            ),
            # Posição: Compra / Venda
            html.Div(
                [
                    html.Label("Posição", style=label_style),
                    dcc.Dropdown(
                        id=f"{leg_id}-posicao",
                        options=[
                            {"label": "Compra", "value": "compra"},
                            {"label": "Venda", "value": "venda"},
                        ],
                        value="compra",
                        clearable=False,
                        style={
                            **input_style,
                            "width": "170px",
                            "backgroundColor": "#F9FAFB",
                            "border": f"1px solid {COLOR_BORDER}",
                            "color": "#111827",
                        },
                    ),
                ],
                style={"display": "inline-block", "marginRight": "15px"},
            ),
            # Strike
            html.Div(
                [
                    html.Label("Strike", style=label_style),
                    dcc.Input(
                        id=f"{leg_id}-strike",
                        type="number",
                        value=5.30,
                        step=0.01,
                        style={**input_style, "width": "130px"},
                    ),
                ],
                style={"display": "inline-block", "marginRight": "15px"},
            ),
            # Volume (USD)
            html.Div(
                [
                    html.Label("Volume (USD)", style=label_style),
                    dcc.Input(
                        id=f"{leg_id}-vol",
                        type="number",
                        value=1_000_000,
                        step=1000,
                        style={**input_style, "width": "150px"},
                    ),
                ],
                style={"display": "inline-block", "marginRight": "15px"},
            ),
            # Prêmio (BRL)
            html.Div(
                [
                    html.Label("Prêmio (BRL)", style=label_style),
                    dcc.Input(
                        id=f"{leg_id}-premio",
                        type="number",
                        value=0,
                        step=1000,
                        style={**input_style, "width": "150px"},
                    ),
                ],
                style={"display": "inline-block", "marginRight": "15px"},
            ),
            # Barreira KO opcional
            html.Div(
                [
                    html.Label("Barreira KO (opcional)", style=label_style),
                    dcc.Input(
                        id=f"{leg_id}-barreira",
                        type="number",
                        step=0.01,
                        placeholder="Sem barreira",
                        style={**input_style, "width": "160px"},
                    ),
                ],
                style={"display": "inline-block"},
            ),
        ],
        id=f"leg-block-{index}",
        style={
            "marginBottom": "18px",
            "padding": "14px 16px",
            "backgroundColor": COLOR_BG_CARD_SOFT,
            "borderRadius": "12px",
            "border": f"1px solid {COLOR_BORDER}",
        },
    )

# ------------------------------------------------------
# APP DASH - CONFIGURAÇÃO
# ------------------------------------------------------
external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Simulador de Estruturas - XP Inc"
server = app.server
app.config.suppress_callback_exceptions = True

LOGO_PATH = "logoxp.png"
logo_base64 = encode_image(LOGO_PATH)

def create_main_layout():
    max_legs = 6

    return html.Div(
        [
            # HEADER
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src=logo_base64
                                if logo_base64
                                else "https://via.placeholder.com/140x40/111827/ffffff?text=XP+Inc",
                                style={"height": "38px", "marginRight": "18px"},
                            )
                        ],
                        style={"display": "flex", "alignItems": "center"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                "Simulador de Estruturas Financeiras",
                                style={
                                    "color": COLOR_TEXT,
                                    "fontFamily": "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI'",
                                    "fontWeight": "700",
                                    "fontSize": "22px",
                                },
                            ),
                            html.Div(
                                "Global Market FICC Sales Desk • XP Inc",
                                style={
                                    "color": COLOR_MUTED,
                                    "fontSize": "12px",
                                    "marginTop": "3px",
                                },
                            ),
                        ],
                        style={"flex": 1, "paddingLeft": "12px"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                datetime.now().strftime("%d/%m/%Y"),
                                style={
                                    "color": COLOR_MUTED,
                                    "fontSize": "12px",
                                    "textAlign": "right",
                                },
                            ),
                            html.Div(
                                "Versão Interativa",
                                style={
                                    "color": COLOR_ACCENT,
                                    "fontSize": "12px",
                                    "fontWeight": "600",
                                    "textAlign": "right",
                                },
                            ),
                        ],
                        style={"minWidth": "120px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "padding": "16px 26px 10px 26px",
                    "backgroundColor": COLOR_BG,
                    "borderBottom": f"1px solid {COLOR_BORDER}",
                    "position": "sticky",
                    "top": 0,
                    "zIndex": 20,
                },
            ),
            dcc.Tabs(
                id="tabs",
                value="ndf",
                children=[
                    dcc.Tab(label="NDF & NDF com Cap", value="ndf", style=tab_style),
                    dcc.Tab(label="Opção de Compra", value="call", style=tab_style),
                    dcc.Tab(label="Call Spread", value="cs", style=tab_style),
                    dcc.Tab(label="ZCC", value="zcc", style=tab_style),
                    dcc.Tab(label="Seagull", value="seagull", style=tab_style),
                    dcc.Tab(label="Forward Extra Cap", value="fec", style=tab_style),
                    dcc.Tab(label="KO e KI", value="koki", style=tab_style),
                    dcc.Tab(label="Simulador Livre", value="simulador", style=tab_style),
                ],
                style=tabs_style,
            ),
            html.Div(id="tab-content", style=content_style),
            dcc.Store(id="active-tab-store", data="ndf"),
        ],
        style={"backgroundColor": COLOR_BG, "margin": 0, "padding": 0},
    )

app.layout = create_main_layout()

# ------------------------------------------------------
# LAYOUT POR ABA
# ------------------------------------------------------
@app.callback(
    [Output("tab-content", "children"), Output("active-tab-store", "data")],
    Input("tabs", "value"),
)
def render_tab_content(tab):
    if tab == "ndf":
        return (
            html.Div(
                [
                    criar_tooltip_estrategia("ndf"),
                    html.Div(
                        [
                            create_input("Volume (USD)", "ndf-vol", 1_000_000, 1000),
                            create_input("NDF", "ndf-strike", 5.30),
                            create_input("Strike Cap", "ndf-cap", 5.50),
                            create_input("PTAX Vencimento", "ndf-ptax-hoje", 5.20),
                            create_input("PTAX Mínima (eixo x)", "ndf-ptax-min", 4.80),
                        ],
                        style=container_style,
                    ),
                    html.Div(
                        id="ndf-info-boxes",
                        style={
                            "textAlign": "left",
                            "marginBottom": "16px",
                            "display": "flex",
                            "flexWrap": "wrap",
                        },
                    ),
                    html.Div(dcc.Graph(id="ndf-graph"), style=container_style),
                ]
            ),
            "ndf",
        )

    elif tab == "call":
        return (
            html.Div(
                [
                    criar_tooltip_estrategia("call"),
                    html.Div(
                        [
                            create_input("Volume (USD)", "call-vol", 1_000_000, 1000),
                            create_input("NDF", "call-ndf-strike", 5.30),
                            create_input("Strike Call", "call-strike", 5.30),
                            create_input("Prêmio Pago (BRL)", "call-premio", 50000, 1000),
                            create_input("PTAX Vencimento", "call-ptax-hoje", 5.20),
                            create_input("PTAX Mínima (eixo x)", "call-ptax-min", 4.80),
                        ],
                        style=container_style,
                    ),
                    html.Div(
                        id="call-info-boxes",
                        style={
                            "textAlign": "left",
                            "marginBottom": "16px",
                            "display": "flex",
                            "flexWrap": "wrap",
                        },
                    ),
                    html.Div(dcc.Graph(id="call-graph"), style=container_style),
                ]
            ),
            "call",
        )

    elif tab == "cs":
        return (
            html.Div(
                [
                    criar_tooltip_estrategia("cs"),
                    html.Div(
                        [
                            create_input("Volume (USD)", "cs-vol", 1_000_000, 1000),
                            create_input("NDF", "cs-ndf-strike", 5.30),
                            create_input("Strike Call Comprada", "cs-strike1", 5.25),
                            create_input("Strike Call Vendida", "cs-strike2", 5.45),
                            create_input("Prêmio Call 1 (BRL)", "cs-premio1", 40000, 1000),
                            create_input("Prêmio Call 2 (BRL)", "cs-premio2", 20000, 1000),
                            create_input("PTAX Vencimento", "cs-ptax-hoje", 5.20),
                            create_input("PTAX Mínima (eixo x)", "cs-ptax-min", 4.80),
                        ],
                        style=container_style,
                    ),
                    html.Div(
                        id="cs-info-boxes",
                        style={
                            "textAlign": "left",
                            "marginBottom": "16px",
                            "display": "flex",
                            "flexWrap": "wrap",
                        },
                    ),
                    html.Div(dcc.Graph(id="cs-graph"), style=container_style),
                ]
            ),
            "cs",
        )

    elif tab == "zcc":
        return (
            html.Div(
                [
                    criar_tooltip_estrategia("zcc"),
                    html.Div(
                        [
                            create_input("Volume (USD)", "zcc-vol", 1_000_000, 1000),
                            create_input("NDF", "zcc-ndf-strike", 5.29),
                            create_input("Strike Put (vende)", "zcc-strike-put", 5.23),
                            create_input("Strike Call (compra)", "zcc-strike-call", 5.35),
                            create_input("PTAX Vencimento", "zcc-ptax-hoje", 5.20),
                        ],
                        style=container_style,
                    ),
                    html.Div(
                        id="zcc-info-boxes",
                        style={
                            "textAlign": "left",
                            "marginBottom": "16px",
                            "display": "flex",
                            "flexWrap": "wrap",
                        },
                    ),
                    html.Div(dcc.Graph(id="zcc-graph"), style=container_style),
                ]
            ),
            "zcc",
        )

    elif tab == "seagull":
        return (
            html.Div(
                [
                    criar_tooltip_estrategia("seagull"),
                    html.Div(
                        [
                            create_input("Volume (USD)", "seag-vol", 1_000_000, 1000),
                            create_input("NDF", "seag-ndf-strike", 5.29),
                            create_input("Strike Put (vende)", "seag-strike-put", 5.20),
                            create_input("Strike Call 1 (compra)", "seag-strike-call1", 5.35),
                            create_input("Strike Call 2 (vende)", "seag-strike-call2", 5.70),
                            create_input("PTAX Vencimento", "seag-ptax-hoje", 5.20),
                        ],
                        style=container_style,
                    ),
                    html.Div(
                        id="seagull-info-boxes",
                        style={
                            "textAlign": "left",
                            "marginBottom": "16px",
                            "display": "flex",
                            "flexWrap": "wrap",
                        },
                    ),
                    html.Div(dcc.Graph(id="seagull-graph"), style=container_style),
                ]
            ),
            "seagull",
        )

    elif tab == "fec":
        return (
            html.Div(
                [
                    criar_tooltip_estrategia("fec"),
                    html.H3(
                        "Forward Extra Cap",
                        style={
                            "color": COLOR_TEXT,
                            "margin": "0 0 16px 2px",
                            "fontSize": "18px",
                        },
                    ),
                    html.Div(
                        [
                            create_input("Volume (USD)", "fec-vol", 1_000_000, 1000),
                            create_input("NDF", "fec-ndf-strike", 5.32),
                            create_input("Strike Put", "fec-strike-put", 5.20),
                            create_input("Strike Call 1", "fec-strike-call1", 5.32),
                            create_input("Strike Call 2 (CAP)", "fec-strike-call2", 5.60),
                            create_input("Barreira Knock-In", "fec-barreira-ki", 5.03),
                            create_input("PTAX Vencimento", "fec-ptax-hoje", 5.20),
                            create_input("USD Mínimo (eixo x)", "fec-usd-minimo", 5.00),
                        ],
                        style=container_style,
                    ),
                    html.Div(
                        id="fec-info-boxes",
                        style={
                            "textAlign": "left",
                            "marginBottom": "16px",
                            "display": "flex",
                            "flexWrap": "wrap",
                        },
                    ),
                    html.Div(dcc.Graph(id="fec-graph"), style=container_style),
                ]
            ),
            "fec",
        )

    elif tab == "koki":
        return (
            html.Div(
                [
                    criar_tooltip_estrategia("koki"),
                    html.H3(
                        "Estratégia KO e KI",
                        style={
                            "color": COLOR_TEXT,
                            "margin": "0 0 16px 2px",
                            "fontSize": "18px",
                        },
                    ),
                    html.Div(
                        [
                            create_input("Volume (USD)", "koki-vol", 1_000_000, 1000),
                            create_input("NDF", "koki-ndf-strike", 5.29),
                            create_input("Strike Call 1", "koki-strike-call1", 5.24),
                            create_input("Strike Call 2", "koki-strike-call2", 5.37),
                            create_input("Strike Put 1", "koki-strike-put1", 5.24),
                            create_input("Strike Put 2", "koki-strike-put2", 5.08),
                            create_input("Barreira KI", "koki-barreira-ki", 5.08),
                            create_input("Barreira KO", "koki-barreira-ko", 5.37),
                            create_input("PTAX Vencimento", "koki-ptax-hoje", 5.20),
                            create_input("USD Mínimo (eixo x)", "koki-usd-minimo", 5.20),
                        ],
                        style=container_style,
                    ),
                    html.Div(
                        id="koki-info-boxes",
                        style={
                            "textAlign": "left",
                            "marginBottom": "16px",
                            "display": "flex",
                            "flexWrap": "wrap",
                        },
                    ),
                    html.Div(dcc.Graph(id="koki-graph"), style=container_style),
                ]
            ),
            "koki",
        )

    elif tab == "simulador":
        max_legs = 6
        return (
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "Simulador Livre de Estratégias",
                                style={
                                    "color": COLOR_TEXT,
                                    "marginBottom": "6px",
                                    "fontSize": "18px",
                                },
                            ),
                            html.P(
                                "Monte combinações customizadas de calls e puts (compra/venda), "
                                "incluindo barreiras KO. O gráfico mostra o payoff agregado.",
                                style={
                                    "color": COLOR_MUTED,
                                    "fontSize": "13px",
                                    "marginBottom": "12px",
                                },
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            create_input("PTAX Mínima (eixo x)", "sim-ptax-min", 4.80),
                            create_input("PTAX Máxima (eixo x)", "sim-ptax-max", 6.20),
                            create_input("PTAX Vencimento", "sim-ptax-hoje", 5.20),
                        ],
                        style=container_style,
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Quantidade de Legs",
                                style={
                                    **label_style,
                                    "display": "block",
                                    "marginBottom": "12px",
                                },
                            ),
                            html.Div(
                                dcc.Slider(
                                    id="sim-num-legs",
                                    min=1,
                                    max=max_legs,
                                    step=1,
                                    value=3,
                                    marks={
                                        i: {
                                            "label": str(i),
                                            "style": {"color": COLOR_MUTED},
                                        }
                                        for i in range(1, max_legs + 1)
                                    },
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                ),
                                style={"width": "80%", "margin": "0 auto"},
                            ),
                        ],
                        style={**container_style, "textAlign": "center"},
                    ),
                    html.Div(
                        id="sim-legs-container",
                        children=[create_leg_inputs(i) for i in range(1, max_legs + 1)],
                        style={"marginBottom": "24px"},
                    ),
                    html.Div(
                        id="sim-info-boxes",
                        style={"textAlign": "left", "marginBottom": "16px"},
                    ),
                    html.Div(dcc.Graph(id="sim-graph"), style=container_style),
                ]
            ),
            "simulador",
        )

    return (
        html.Div(
            "Aba inválida.",
            style={"color": COLOR_TEXT, "padding": "50px", "textAlign": "center"},
        ),
        tab,
    )

# ------------------------------------------------------
# CALLBACKS DAS ESTRATÉGIAS
# ------------------------------------------------------
@app.callback(
    [Output("ndf-graph", "figure"), Output("ndf-info-boxes", "children")],
    [
        Input("ndf-vol", "value"),
        Input("ndf-strike", "value"),
        Input("ndf-cap", "value"),
        Input("ndf-ptax-min", "value"),
        Input("ndf-ptax-hoje", "value"),
    ],
)
def update_ndf_graph(vol, strike_ndf, cap, ptax_min, ptax_vencimento):
    vol = vol or 1_000_000
    strike_ndf = strike_ndf or 5.30
    cap = cap or 5.50
    ptax_min = ptax_min or 4.80
    ptax_vencimento = ptax_vencimento or 5.20

    ptax = np.arange(ptax_min, 6.20, 0.01)
    ndf = calculate_ndf_pnl(ptax, strike_ndf, vol)
    ndf_cap = np.minimum(ndf, (cap - strike_ndf) * vol)

    pnl_ndf_hoje = calculate_ndf_pnl(ptax_vencimento, strike_ndf, vol)
    pnl_ndf_cap_hoje = min(pnl_ndf_hoje, (cap - strike_ndf) * vol)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=ndf,
            name=f"NDF: {strike_ndf:.2f}",
            line=dict(color="#38BDF8", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=ndf_cap,
            name=f"NDF com Cap ({cap:.2f})",
            line=dict(color="#F97316", width=3),
        )
    )

    fig.add_vline(
        x=ptax_vencimento,
        line_dash="dash",
        line_color="#E5E7EB",
        line_width=2,
        annotation_text=f"PTAX Vencimento: {ptax_vencimento:.2f}",
        annotation_position="top",
        annotation_font_size=12,
    )
    fig.add_vline(
        x=ptax_min,
        line_dash="dash",
        line_color="#6B7280",
        line_width=1,
        annotation_text=f"PTAX Mín: {ptax_min:.2f}",
        annotation_position="bottom",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=cap,
        line_dash="dot",
        line_color="#F97316",
        line_width=1,
        annotation_text=f"Cap: {cap:.2f}",
        annotation_position="top right",
        annotation_font_size=10,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#4B5563", line_width=1)

    fig = configure_graph(
        fig, f"Payoff – NDF / NDF com Cap | Volume: ${vol:,.0f}"
    )

    info_boxes = html.Div(
        [
            create_info_box("PnL NDF", pnl_ndf_hoje, "#38BDF8"),
            create_info_box("PnL NDF + Cap", pnl_ndf_cap_hoje, "#F97316"),
        ],
        style={"display": "flex", "flexWrap": "wrap"},
    )

    return fig, info_boxes

@app.callback(
    [Output("call-graph", "figure"), Output("call-info-boxes", "children")],
    [
        Input("call-vol", "value"),
        Input("call-ndf-strike", "value"),
        Input("call-strike", "value"),
        Input("call-premio", "value"),
        Input("call-ptax-min", "value"),
        Input("call-ptax-hoje", "value"),
    ],
)
def update_call_graph(
    vol, strike_ndf, strike_call, premio_call, ptax_min, ptax_vencimento
):
    vol = vol or 1_000_000
    strike_ndf = strike_ndf or 5.30
    strike_call = strike_call or 5.30
    premio_call = premio_call or 50000
    ptax_min = ptax_min or 4.80
    ptax_vencimento = ptax_vencimento or 5.20

    ptax = np.arange(ptax_min, 6.20, 0.01)
    ndf = calculate_ndf_pnl(ptax, strike_ndf, vol)
    call_payoff_total = call_payoff(ptax, strike_call, vol) - premio_call

    pnl_ndf_hoje = calculate_ndf_pnl(ptax_vencimento, strike_ndf, vol)
    pnl_call_hoje = call_payoff(ptax_vencimento, strike_call, vol) - premio_call

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=ndf,
            name=f"NDF: {strike_ndf:.2f}",
            line=dict(color="#F97316", width=2, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=call_payoff_total,
            name=f"Call (Prêmio: R\$ {premio_call:,.0f})",
            line=dict(color="#22C55E", width=3),
        )
    )

    fig.add_vline(
        x=ptax_vencimento,
        line_dash="dash",
        line_color="#E5E7EB",
        line_width=2,
        annotation_text=f"PTAX Vencimento: {ptax_vencimento:.2f}",
        annotation_position="top",
        annotation_font_size=12,
    )
    fig.add_vline(
        x=ptax_min,
        line_dash="dash",
        line_color="#6B7280",
        line_width=1,
        annotation_text=f"PTAX Mín: {ptax_min:.2f}",
        annotation_position="bottom",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike_call,
        line_dash="dot",
        line_color="#22C55E",
        line_width=1,
        annotation_text=f"Strike Call: {strike_call:.2f}",
        annotation_position="top right",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike_ndf,
        line_dash="dot",
        line_color="#F97316",
        line_width=1,
        annotation_text=f"NDF: {strike_ndf:.2f}",
        annotation_position="bottom right",
        annotation_font_size=10,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#4B5563", line_width=1)

    fig = configure_graph(
        fig, f"Payoff – Opção de Compra (Call) + NDF | Volume: ${vol:,.0f}"
    )

    info_boxes = html.Div(
        [
            create_info_box("PnL NDF", pnl_ndf_hoje, "#F97316"),
            create_info_box("PnL Call", pnl_call_hoje, "#22C55E"),
            create_info_box("Prêmio Pago", -premio_call, "#6B7280"),
        ],
        style={"display": "flex", "flexWrap": "wrap"},
    )

    return fig, info_boxes

@app.callback(
    [Output("cs-graph", "figure"), Output("cs-info-boxes", "children")],
    [
        Input("cs-vol", "value"),
        Input("cs-ndf-strike", "value"),
        Input("cs-strike1", "value"),
        Input("cs-strike2", "value"),
        Input("cs-premio1", "value"),
        Input("cs-premio2", "value"),
        Input("cs-ptax-min", "value"),
        Input("cs-ptax-hoje", "value"),
    ],
)
def update_cs_graph(
    vol,
    strike_ndf,
    strike1,
    strike2,
    premio1,
    premio2,
    ptax_min,
    ptax_vencimento,
):
    vol = vol or 1_000_000
    strike_ndf = strike_ndf or 5.30
    strike1 = strike1 or 5.25
    strike2 = strike2 or 5.45
    premio1 = premio1 or 40000
    premio2 = premio2 or 20000
    ptax_min = ptax_min or 4.80
    ptax_vencimento = ptax_vencimento or 5.20

    ptax = np.arange(ptax_min, 6.20, 0.01)
    ndf = calculate_ndf_pnl(ptax, strike_ndf, vol)

    call1_buy = call_payoff(ptax, strike1, vol)
    call2_sell = -call_payoff(ptax, strike2, vol)
    cs = call1_buy + call2_sell - premio1 + premio2

    premio_liquido = premio1 - premio2
    pnl_ndf_hoje = calculate_ndf_pnl(ptax_vencimento, strike_ndf, vol)
    pnl_cs_hoje = (
        call_payoff(ptax_vencimento, strike1, vol)
        - call_payoff(ptax_vencimento, strike2, vol)
        - premio_liquido
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=ndf,
            name=f"NDF: {strike_ndf:.2f}",
            line=dict(color="#F97316", width=2, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=cs,
            name=f"Call Spread (Prêmio Líq: R\$ {premio_liquido:,.0f})",
            line=dict(color="#A855F7", width=3),
        )
    )

    fig.add_vline(
        x=ptax_vencimento,
        line_dash="dash",
        line_color="#E5E7EB",
        line_width=2,
        annotation_text=f"PTAX Vencimento: {ptax_vencimento:.2f}",
        annotation_position="top",
        annotation_font_size=12,
    )
    fig.add_vline(
        x=ptax_min,
        line_dash="dash",
        line_color="#6B7280",
        line_width=1,
        annotation_text=f"PTAX Mín: {ptax_min:.2f}",
        annotation_position="bottom",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike1,
        line_dash="dot",
        line_color="#A855F7",
        line_width=1,
        annotation_text=f"Call 1: {strike1:.2f}",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike2,
        line_dash="dot",
        line_color="#A855F7",
        line_width=1,
        annotation_text=f"Call 2: {strike2:.2f}",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike_ndf,
        line_dash="dot",
        line_color="#F97316",
        line_width=1,
        annotation_text=f"NDF: {strike_ndf:.2f}",
        annotation_font_size=10,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#4B5563", line_width=1)

    fig = configure_graph(
        fig, f"Payoff – Call Spread + NDF | Volume: ${vol:,.0f}"
    )

    info_boxes = html.Div(
        [
            create_info_box("PnL NDF", pnl_ndf_hoje, "#F97316"),
            create_info_box("PnL Call Spread", pnl_cs_hoje, "#A855F7"),
            create_info_box("Prêmio Líquido", -premio_liquido, "#6B7280"),
        ],
        style={"display": "flex", "flexWrap": "wrap"},
    )

    return fig, info_boxes

@app.callback(
    [Output("zcc-graph", "figure"), Output("zcc-info-boxes", "children")],
    [
        Input("zcc-vol", "value"),
        Input("zcc-ndf-strike", "value"),
        Input("zcc-strike-put", "value"),
        Input("zcc-strike-call", "value"),
        Input("zcc-ptax-hoje", "value"),
    ],
)
def update_zcc_graph(
    vol, strike_ndf, strike_put, strike_call, ptax_vencimento
):
    vol = vol or 1_000_000
    strike_ndf = strike_ndf or 5.29
    strike_put = strike_put or 5.23
    strike_call = strike_call or 5.35
    ptax_vencimento = ptax_vencimento or 5.20

    ptax = np.arange(4.80, 6.20, 0.01)
    ndf = calculate_ndf_pnl(ptax, strike_ndf, vol)

    put_vendida = -put_payoff(ptax, strike_put, vol)
    call_comprada = call_payoff(ptax, strike_call, vol)
    zcc = put_vendida + call_comprada

    pnl_ndf_hoje = calculate_ndf_pnl(ptax_vencimento, strike_ndf, vol)
    pnl_zcc_hoje = -put_payoff(ptax_vencimento, strike_put, vol) + call_payoff(
        ptax_vencimento, strike_call, vol
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=ndf,
            name=f"NDF: {strike_ndf:.2f}",
            line=dict(color="#F97316", width=2, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=zcc,
            name="ZCC (Zero Cost Collar)",
            line=dict(color="#0EA5E9", width=3),
        )
    )

    fig.add_vline(
        x=ptax_vencimento,
        line_dash="dash",
        line_color="#E5E7EB",
        line_width=2,
        annotation_text=f"PTAX Vencimento: {ptax_vencimento:.2f}",
        annotation_position="top",
        annotation_font_size=12,
    )
    fig.add_vline(
        x=strike_put,
        line_dash="dot",
        line_color="#0EA5E9",
        line_width=1,
        annotation_text=f"Put: {strike_put:.2f}",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike_call,
        line_dash="dot",
        line_color="#0EA5E9",
        line_width=1,
        annotation_text=f"Call: {strike_call:.2f}",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike_ndf,
        line_dash="dot",
        line_color="#F97316",
        line_width=1,
        annotation_text=f"NDF: {strike_ndf:.2f}",
        annotation_font_size=10,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#4B5563", line_width=1)

    fig = configure_graph(
        fig, f"Payoff – ZCC + NDF | Volume: ${vol:,.0f}"
    )

    info_boxes = html.Div(
        [
            create_info_box("PnL NDF", pnl_ndf_hoje, "#F97316"),
            create_info_box("PnL ZCC", pnl_zcc_hoje, "#0EA5E9"),
        ],
        style={"display": "flex", "flexWrap": "wrap"},
    )

    return fig, info_boxes

@app.callback(
    [Output("seagull-graph", "figure"), Output("seagull-info-boxes", "children")],
    [
        Input("seag-vol", "value"),
        Input("seag-ndf-strike", "value"),
        Input("seag-strike-put", "value"),
        Input("seag-strike-call1", "value"),
        Input("seag-strike-call2", "value"),
        Input("seag-ptax-hoje", "value"),
    ],
)
def update_seagull_graph(
    vol,
    strike_ndf,
    strike_put,
    strike_call1,
    strike_call2,
    ptax_vencimento,
):
    vol = vol or 1_000_000
    strike_ndf = strike_ndf or 5.29
    strike_put = strike_put or 5.20
    strike_call1 = strike_call1 or 5.35
    strike_call2 = strike_call2 or 5.70
    ptax_vencimento = ptax_vencimento or 5.20

    ptax = np.arange(4.80, 6.20, 0.01)
    ndf = calculate_ndf_pnl(ptax, strike_ndf, vol)

    put_vendida = -put_payoff(ptax, strike_put, vol)
    call1_comprada = call_payoff(ptax, strike_call1, vol)
    call2_vendida = -call_payoff(ptax, strike_call2, vol)
    seagull = put_vendida + call1_comprada + call2_vendida

    pnl_ndf_hoje = calculate_ndf_pnl(ptax_vencimento, strike_ndf, vol)
    pnl_seagull_hoje = (
        -put_payoff(ptax_vencimento, strike_put, vol)
        + call_payoff(ptax_vencimento, strike_call1, vol)
        - call_payoff(ptax_vencimento, strike_call2, vol)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=ndf,
            name=f"NDF: {strike_ndf:.2f}",
            line=dict(color="#F97316", width=2, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=seagull,
            name="Seagull",
            line=dict(color="#FB7185", width=3),
        )
    )

    fig.add_vline(
        x=ptax_vencimento,
        line_dash="dash",
        line_color="#E5E7EB",
        line_width=2,
        annotation_text=f"PTAX Vencimento: {ptax_vencimento:.2f}",
        annotation_position="top",
        annotation_font_size=12,
    )
    fig.add_vline(
        x=strike_put,
        line_dash="dot",
        line_color="#FB7185",
        line_width=1,
        annotation_text=f"Put: {strike_put:.2f}",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike_call1,
        line_dash="dot",
        line_color="#FB7185",
        line_width=1,
        annotation_text=f"Call 1: {strike_call1:.2f}",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike_call2,
        line_dash="dot",
        line_color="#FB7185",
        line_width=1,
        annotation_text=f"Call 2: {strike_call2:.2f}",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=strike_ndf,
        line_dash="dot",
        line_color="#F97316",
        line_width=1,
        annotation_text=f"NDF: {strike_ndf:.2f}",
        annotation_font_size=10,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#4B5563", line_width=1)

    fig = configure_graph(
        fig, f"Payoff – Seagull + NDF | Volume: ${vol:,.0f}"
    )

    info_boxes = html.Div(
        [
            create_info_box("PnL NDF", pnl_ndf_hoje, "#F97316"),
            create_info_box("PnL Seagull", pnl_seagull_hoje, "#FB7185"),
        ],
        style={"display": "flex", "flexWrap": "wrap"},
    )

    return fig, info_boxes

# 6) FORWARD EXTRA CAP
@app.callback(
    [Output("fec-graph", "figure"), Output("fec-info-boxes", "children")],
    [
        Input("fec-vol", "value"),
        Input("fec-ndf-strike", "value"),
        Input("fec-strike-put", "value"),
        Input("fec-strike-call1", "value"),
        Input("fec-strike-call2", "value"),
        Input("fec-barreira-ki", "value"),
        Input("fec-usd-minimo", "value"),
        Input("fec-ptax-hoje", "value"),
    ],
)
def update_fec_graph(
    vol,
    strike_ndf,
    strike_put,
    strike_call1,
    strike_call2,
    barreira_ki,
    usd_minimo,
    ptax_vencimento,
):
    vol = vol or 1_000_000
    strike_ndf = strike_ndf or 5.32
    strike_put = strike_put or 5.20
    strike_call1 = strike_call1 or 5.32
    strike_call2 = strike_call2 or 5.60
    barreira_ki = barreira_ki or 5.03
    usd_minimo = usd_minimo or 5.00
    ptax_vencimento = ptax_vencimento or 5.20

    ptax = np.arange(min(usd_minimo, ptax_vencimento) - 0.3, 6.20, 0.01)

    ndf = calculate_ndf_pnl(ptax, strike_ndf, vol)
    put_vendida = -put_payoff(ptax, strike_put, vol)
    call1_comprada = call_payoff(ptax, strike_call1, vol)
    call2_vendida = -call_payoff(ptax, strike_call2, vol)
    fec_payoff = put_vendida + call1_comprada + call2_vendida

    mask_zona_barreira = (ptax >= barreira_ki) & (ptax <= strike_call1)
    ki_ativado = usd_minimo <= barreira_ki

    idx_hoje = np.argmin(np.abs(ptax - ptax_vencimento))
    if ki_ativado and mask_zona_barreira[idx_hoje]:
        pnl_fec_hoje = 0
        cor_ki = "#F97316"
    else:
        pnl_fec_hoje = fec_payoff[idx_hoje]
        cor_ki = "#22C55E" if not ki_ativado else "#FACC15"

    pnl_ndf_hoje = ndf[idx_hoje]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=fec_payoff,
            name="Forward Extra Cap",
            line=dict(color="#22C55E", width=4),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.12)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=ndf,
            name=f"NDF Teórico: {strike_ndf:.2f}",
            line=dict(color="#F97316", width=2, dash="dash"),
        )
    )

    if np.any(mask_zona_barreira):
        fig.add_trace(
            go.Scatter(
                x=ptax[mask_zona_barreira],
                y=fec_payoff[mask_zona_barreira],
                name="Zona Barreira KI" if ki_ativado else "Zona KI (Inativa)",
                line=dict(
                    color="#F97316" if ki_ativado else "#6B7280",
                    width=3,
                    dash="dot",
                ),
                mode="lines",
                showlegend=True,
            )
        )
        if ki_ativado:
            fig.add_trace(
                go.Scatter(
                    x=ptax[mask_zona_barreira],
                    y=np.zeros(np.sum(mask_zona_barreira)),
                    name="PnL = 0 (KI Ativo)",
                    line=dict(color="#F97316", width=2, dash="dash"),
                    mode="lines",
                )
            )

    fig.add_vline(
        x=ptax_vencimento,
        line_dash="dash",
        line_color="#E5E7EB",
        line_width=3,
        annotation_text=f"PTAX Vencimento: {ptax_vencimento:.2f}",
        annotation_position="top",
        annotation_font_size=12,
    )
    fig.add_vline(
        x=usd_minimo,
        line_dash="dash",
        line_color="#9CA3AF",
        line_width=2,
        annotation_text=f"USD Mín: {usd_minimo:.2f}",
        annotation_position="bottom",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=barreira_ki,
        line_dash="dot",
        line_color="#F97316",
        line_width=2,
        annotation_text=f"KI: {barreira_ki:.2f}",
        annotation_font_size=11,
    )
    fig.add_vline(
        x=strike_call1,
        line_dash="dot",
        line_color="#22C55E",
        line_width=2,
        annotation_text=f"Call1: {strike_call1:.2f}",
        annotation_font_size=11,
    )
    fig.add_vline(
        x=strike_call2,
        line_dash="dot",
        line_color="#FACC15",
        line_width=2,
        annotation_text=f"Cap: {strike_call2:.2f}",
        annotation_font_size=11,
    )
    fig.add_vline(
        x=strike_ndf,
        line_dash="dot",
        line_color="#F97316",
        line_width=1,
        annotation_text=f"NDF: {strike_ndf:.2f}",
        annotation_font_size=10,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#4B5563", line_width=1)

    fig = configure_graph(fig, f"Forward Extra Cap | Vol: ${vol:,.0f}", height=650)

    info_boxes = html.Div(
        [
            create_simple_pnl_box("PnL NDF", pnl_ndf_hoje, "#F97316"),
            create_simple_pnl_box("PnL FEC", pnl_fec_hoje, cor_ki),
        ],
        style={"display": "flex", "flexWrap": "wrap"},
    )

    return fig, info_boxes

# 7) KO/KI
@app.callback(
    [Output("koki-graph", "figure"), Output("koki-info-boxes", "children")],
    [
        Input("koki-vol", "value"),
        Input("koki-ndf-strike", "value"),
        Input("koki-strike-call1", "value"),
        Input("koki-strike-call2", "value"),
        Input("koki-strike-put1", "value"),
        Input("koki-strike-put2", "value"),
        Input("koki-usd-minimo", "value"),
        Input("koki-ptax-hoje", "value"),
        Input("koki-barreira-ki", "value"),
        Input("koki-barreira-ko", "value"),
    ],
)
def update_koki_graph(
    vol,
    strike_ndf,
    strike_call1,
    strike_call2,
    strike_put1,
    strike_put2,
    usd_minimo,
    ptax_vencimento,
    barreira_ki,
    barreira_ko,
):

    vol = vol or 1_000_000
    strike_ndf = strike_ndf or 5.35
    strike_call1 = strike_call1 or 5.25
    strike_call2 = strike_call2 or 5.40
    strike_put1 = strike_put1 or 5.25
    strike_put2 = strike_put2 or 5.40
    usd_minimo = usd_minimo or 5.20
    ptax_vencimento = ptax_vencimento or 5.20
    barreira_ki = barreira_ki or 5.20
    barreira_ko = barreira_ko or 5.20

    ptax = np.arange(4.80, 6.10, 0.01)

    ndf_cliente = calculate_ndf_pnl(ptax, strike_ndf, vol)

    call1 = call_payoff(ptax, strike_call1, vol)
    call2 = call_payoff(ptax, strike_call2, vol)
    put1 = -put_payoff(ptax, strike_put1, vol)
    put2 = -put_payoff(ptax, strike_put2, vol)

    estrutura_partida = call1 + put1
    estrutura_se_barreira = call2 + put2

    if usd_minimo < barreira_ki:
        pnl_koki_hoje = np.interp(ptax_vencimento, ptax, estrutura_partida)
        cor_principal = "#22C55E"
        status = "Partida (KI/KO não acionados)"
    else:
        pnl_koki_hoje = np.interp(ptax_vencimento, ptax, estrutura_se_barreira)
        cor_principal = "#F97316"
        status = "Barreira Ativada"

    pnl_ndf_hoje = np.interp(ptax_vencimento, ptax, ndf_cliente)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=estrutura_partida,
            name="Estratégia (Barreira Inativa)",
            line=dict(color="#22C55E", width=4),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=estrutura_se_barreira,
            name="Estratégia (Barreira Ativada)",
            line=dict(color="#F97316", width=4, dash="dash"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=ndf_cliente,
            name="NDF Teórico",
            line=dict(color="#EF4444", width=3, dash="dot"),
        )
    )

    fig.add_vline(
        x=barreira_ki,
        line_dash="dot",
        line_color="#22C55E",
        line_width=2,
        annotation_text=f"Barreira KI: {barreira_ki:.2f}",
        annotation_position="top",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=barreira_ko,
        line_dash="dot",
        line_color="#EF4444",
        line_width=2,
        annotation_text=f"Barreira KO: {barreira_ko:.2f}",
        annotation_position="top",
        annotation_font_size=10,
    )
    fig.add_vline(
        x=ptax_vencimento,
        line_dash="dash",
        line_color="#E5E7EB",
        line_width=3,
        annotation_text=f"Hoje: {ptax_vencimento:.2f}",
        annotation_position="top",
        annotation_font_size=12,
    )
    fig.add_vline(
        x=usd_minimo,
        line_dash="dash",
        line_color="#9CA3AF",
        line_width=2,
        annotation_text=f"USD Min: {usd_minimo:.2f}",
        annotation_position="bottom",
        annotation_font_size=10,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#4B5563", line_width=1)

    titulo = f"KO/KI + NDF | Vol=${vol:,.0f} | Status: {status}"
    fig = configure_graph(fig, titulo, height=650)

    info_boxes = html.Div(
        [
            create_simple_pnl_box("PnL NDF Cliente", pnl_ndf_hoje, "#EF4444"),
            create_simple_pnl_box("PnL Estrutura Atual", pnl_koki_hoje, cor_principal),
        ],
        style={"display": "flex", "flexWrap": "wrap"},
    )

    return fig, info_boxes

# ------------------------------------------------------
# CALLBACKS DA ABA SIMULADOR LIVRE
# ------------------------------------------------------
@app.callback(
    Output("sim-legs-container", "children"),
    Input("sim-num-legs", "value"),
    prevent_initial_call=False,
)
def update_sim_legs_visibility(num_legs):
    max_legs = 6
    num_legs = int(num_legs or 3)
    num_legs = max(1, min(max_legs, num_legs))

    children = []
    for i in range(1, max_legs + 1):
        leg = create_leg_inputs(i)
        style = (leg.style or {}).copy()
        if i > num_legs:
            style["display"] = "none"
        children.append(
            html.Div(
                leg.children,
                id=f"leg-block-{i}",
                style=style,
            )
        )
    return children


@app.callback(
    [Output("sim-graph", "figure"), Output("sim-info-boxes", "children")],
    [
        Input("sim-num-legs", "value"),
        Input("sim-ptax-min", "value"),
        Input("sim-ptax-max", "value"),
        Input("sim-ptax-hoje", "value"),
        *[Input(f"leg-{i}-tipo", "value") for i in range(1, 7)],
        *[Input(f"leg-{i}-posicao", "value") for i in range(1, 7)],
        *[Input(f"leg-{i}-strike", "value") for i in range(1, 7)],
        *[Input(f"leg-{i}-vol", "value") for i in range(1, 7)],
        *[Input(f"leg-{i}-premio", "value") for i in range(1, 7)],
        *[Input(f"leg-{i}-barreira", "value") for i in range(1, 7)],
    ],
    prevent_initial_call=False,
)
def update_sim_graph(num_legs, ptax_min, ptax_max, ptax_hoje, *leg_inputs):
    """Calcula e plota payoff total da estratégia customizada (incluindo prêmios)."""

    max_legs = 6
    num_legs = int(num_legs or 3)
    num_legs = max(1, min(max_legs, num_legs))

    tipos     = leg_inputs[0:6]
    posicoes  = leg_inputs[6:12]
    strikes   = leg_inputs[12:18]
    vols      = leg_inputs[18:24]
    premios   = leg_inputs[24:30]
    barreiras = leg_inputs[30:36]

    try:
        ptax_min = float(ptax_min or 4.80)
        ptax_max = float(ptax_max or 6.20)
        ptax_hoje = float(ptax_hoje or 5.20)
    except (ValueError, TypeError):
        ptax_min, ptax_max, ptax_hoje = 4.80, 6.20, 5.20

    if ptax_max <= ptax_min:
        ptax_max = ptax_min + 0.5

    ptax = np.arange(ptax_min, ptax_max + 0.0001, 0.01)
    payoff_total = np.zeros_like(ptax)
    strikes_linha = []
    leg_info = []

    for i in range(num_legs):
        try:
            tipo = tipos[i] or "call"
            pos = posicoes[i] or "compra"
            K = float(strikes[i] or 5.30)
            vol = float(vols[i] or 1_000_000)
            premio = float(premios[i] or 0.0)
            barr = barreiras[i]

            if tipo == "call":
                leg_payoff = call_payoff(ptax, K, vol)
                leg_type = "Call"
            else:
                leg_payoff = put_payoff(ptax, K, vol)
                leg_type = "Put"

            direction = "Buy" if pos == "compra" else "Sell"
            if pos == "venda":
                leg_payoff = -leg_payoff

            barrier_info = ""
            if barr is not None and str(barr).strip() != "":
                try:
                    barr = float(barr)
                    if tipo == "call":
                        leg_payoff = np.where(ptax >= barr, 0, leg_payoff)
                    else:
                        leg_payoff = np.where(ptax <= barr, 0, leg_payoff)
                    barrier_info = f" KO@{barr:.2f}"
                except (ValueError, TypeError):
                    barrier_info = " (barreira inválida)"

            premio_label = ""
            if premio != 0:
                if pos == "compra":
                    leg_payoff = leg_payoff - premio
                    premio_label = f" -Prêmio R${premio:,.0f}"
                else:
                    leg_payoff = leg_payoff + premio
                    premio_label = f" +Prêmio R${premio:,.0f}"

            payoff_total += leg_payoff
            strikes_linha.append(K)

            leg_info.append(
                f"Leg {i+1}: {direction} {leg_type} K={K:.2f} Vol=${vol/1_000:.0f}K"
                f"{barrier_info}{premio_label}"
            )

        except (ValueError, TypeError, IndexError):
            leg_info.append(f"Leg {i+1}: ⚠️ Erro na configuração")
            continue

    try:
        idx_hoje = np.argmin(np.abs(ptax - ptax_hoje))
        pnl_hoje = payoff_total[idx_hoje]
    except (IndexError, ValueError):
        pnl_hoje = 0

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=ptax,
            y=payoff_total,
            name=f"Payoff Total ({num_legs} Legs)",
            line=dict(color="#A855F7", width=4),
            fill="tozeroy",
            fillcolor="rgba(168,85,247,0.16)",
            hovertemplate="PTAX: %{x:.2f}<br>PnL: R\$ %{y:,.0f}<extra></extra>",
        )
    )

    unique_strikes = sorted(set(strikes_linha))
    for idx, K in enumerate(unique_strikes):
        fig.add_vline(
            x=K,
            line_dash="dot",
            line_color="#FACC15",
            line_width=1,
            annotation_text=f"K{idx+1}: {K:.2f}",
            annotation_position="top" if idx % 2 == 0 else "bottom",
            annotation_font_size=10,
        )

    fig.add_vline(
        x=ptax_hoje,
        line_dash="dash",
        line_color="#E5E7EB",
        line_width=3,
        annotation_text=f"PTAX Vencimento: {ptax_hoje:.2f}",
        annotation_position="top",
        annotation_font=dict(size=12, color="#E5E7EB"),
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#65748A", line_width=1)

    legs_summary = ", ".join(leg_info[:2])
    if len(leg_info) > 2:
        legs_summary += f" +{len(leg_info)-2} mais"

    fig = configure_graph(fig, f"Simulador Livre – {legs_summary}", height=650)

    info_boxes = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        "Configuração Atual",
                        style={
                            "color": COLOR_ACCENT,
                            "fontWeight": "600",
                            "fontSize": "14px",
                            "marginBottom": "8px",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                leg,
                                style={
                                    "margin": "4px 0",
                                    "padding": "6px 10px",
                                    "backgroundColor": "#020617",
                                    "borderRadius": "6px",
                                    "borderLeft": f"3px solid {COLOR_ACCENT}",
                                    "fontSize": "12px",
                                    "fontFamily": info_value_style["fontFamily"],
                                    "color": COLOR_TEXT,
                                },
                            )
                            for leg in leg_info
                        ],
                        style={
                            "maxHeight": "200px",
                            "overflowY": "auto",
                            "marginBottom": "10px",
                        },
                    ),
                ],
                style={
                    "backgroundColor": COLOR_BG_CARD,
                    "padding": "14px 16px",
                    "borderRadius": "12px",
                    "border": f"1px solid {COLOR_BORDER}",
                    "marginBottom": "16px",
                },
            ),
            create_simple_pnl_box(
                f"PnL Total ({num_legs} Legs)", pnl_hoje, "#22C55E"
            ),
        ]
    )

    return fig, info_boxes

# ------------------------------------------------------
# MAIN
# ------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Iniciando Simulador de Estruturas Financeiras - XP Inc")
    print("=" * 70)
    print("📡 ACESSO LOCAL:  http://localhost:8050")
    print("📡 REDE LOCAL:   http://0.0.0.0:8050")
    print("🌐 LINK PÚBLICO: será gerado via Cloudflare Tunnel (veja o console)")
    print("=" * 70)
    print("🎨 Layout:")
    print(" • Tema dark moderno, com cards, glass leve e tipografia Inter.")
    print(" • Aba Simulador Livre com slider de legs e resumo da estratégia.")
    print(" • Dropdowns claros, texto escuro; texto de configuração em branco.")
    print("=" * 70)

    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)