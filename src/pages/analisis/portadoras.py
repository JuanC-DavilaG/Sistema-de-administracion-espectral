from datetime import datetime
from dash.exceptions import PreventUpdate
import base64
import io
import dash
from dash import Dash, dash_table, dcc, html, Input, Output, callback, ctx, no_update, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import csv
from modules.leer_csv import *
from modules.disponible import *
from modules.variables import *
from modules.generar_portadoras import *
from modules.reporte_analisis import *
from modules.def_class import *
from modules.dbConnect import *
from flask import send_file

dash.register_page(
	__name__,
    path_template="/analisis/portadoras",
    title='Analisis de portadoras',
    description='Mustra una representacion grafica de las portadoras y genera reportes de disponibilidad y ocupación.', 
    order=0,
    location = "analisis"
)

layout = html.Div([

    dbc.Row([
        
        dbc.Col(
            html.Div([
                dcc.Upload(
                    id='datatable-upload',
                    accept=".CSV",
                    children=html.Div([
                        'Arrastrar y soltar o ',
                        html.A('Seleccionar archivo'),
                        ' ' + ETIQUETA_1
                    ]),
                )
            ], id='entrada_ET1')
        ),

        dbc.Col(
            html.Div([
                dcc.Upload(
                    id='datatable-upload-1',
                    accept=".CSV",
                    children=html.Div([
                        'Arrastrar y soltar o ',
                        html.A('Seleccionar archivo'),
                        ' ' + ETIQUETA_2
                    ]),
                )
            ], id='entrada_ET2')
        ),
        
    ],
    className="botones_SP",),

    dcc.Graph(id='datatable-upload-graph',

        style=style_graf_init,
    ),

    dbc.Row([
        dbc.Col(
            html.Div([
                dash_table.DataTable(id='datatable-upload-container',
                    page_action='none',
                    filter_action='native',
                    style_table = style_tabla,
                    style_header = header_tablas,
                    style_cell = cell_tablas,
                    style_data_conditional=[style_data_condition],
                    editable=True, 
                    row_deletable=True, 
                    page_size=12,
                ),
            ]), style={"width": "33.33%"}
        ),

        dbc.Col([
            dbc.Row([
                dbc.Col(
                    dbc.Row([
                        dbc.Col(
                            dbc.Checklist(
                                id='VerServicios',
                                options=[{'label': 'Ver servicios', 
                                        'value': 'View', 'disabled': True}],
                                input_checked_style={
                                "backgroundColor": "rgba(33,134,244,0.5)",
                                "borderColor": "#555",
                                },
                                label_checked_style={"color": "rgba(33,134,244,0.5)"},
                                value=[],
                            ),
                        ),
                        dbc.Col(
                            dbc.Input(id="int_can", placeholder="Canalización", 
                                      type="text", style={'padding': '1px','width': "90%", 'color': '#A0AABA', 'backgroundColor': '#555', 'borderColor': 'rgb(63,63,63)', 'margin': '0 5px 0 0'}, 
                                      disabled=True),
                        ),
                    ])

                ),
                dbc.Col(
                    dbc.Select(
                        id="select_band", placeholder="Bandas...",
                        options=[
                            {"label": "HF", "value": "HF"},
                            {"label": "VHF", "value": "VHF"},
                            {"label": "UHF", "value": "UHF"},
                            {"label": "SHF", "value": "SHF"},
                            {"label": "EHF", "value": "EHF", "disabled": True},
                        ],
                        disabled=True
                    )
                ),

            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.P("Segmento", style={'margin': '10px'}), width="auto", style={'color': '#A0AABA', 'padding': '0 0 0 38%'}),
                    ], style={'padding':'0 0 0 0%'}),
                    dbc.Row([
                            dbc.Input(id="seg_bajo", placeholder="Bajo", 
                                      type="text", style={'width': "48%", 'color': '#A0AABA', 'backgroundColor': '#555', 'borderColor': 'rgb(63,63,63)', 'margin': '0 5px 0 0'}, 
                                      disabled=True),
                            dbc.Input(id="seg_alto", placeholder="Alto", 
                                      type="text", style={'width': "48%", 'color': '#A0AABA', 'backgroundColor': '#555', 'borderColor': 'rgb(63,63,63)'}, 
                                      disabled=True),
                    ], style={"padding": "0px 0 0 15px"}),
                    dbc.Row([
                        dcc.Dropdown(
                                    ['Móvil', 
                                    'Móvil por satélite (Tierra-Espacio)', 
                                    'Móvil salvo móvil aeronáutico', 
                                    'Móvil marítimo (socorro y llamada por LLSD)',
                                    'Móvil marítimo',
                                    'Móvil Aeronáutico ®',
                                    ],
                                    ['Móvil'],
                                    id='Servis-dropdown',
                                    multi=True, 
                                    style=servis_dropdown, disabled=True),
                                    
                    ]),
                ]),

                dbc.Col(
                    dbc.Row([
                        dbc.Col([
                            dbc.Checklist(options = [{"label": "Todo", "value": "T", "disabled": True}], value = [], id="CEs",
                                                    input_checked_style={
                                                            "backgroundColor": "rgba(33,134,244,0.5)",
                                                            "borderColor": "#555",
                                                        },
                                                        label_checked_style={"color": "rgba(33,134,244,0.5)"},
                                                        inline=True),
                            dbc.Checklist(options = opcionesCEs_0, value=[], id="OpCEs_0",
                                                    input_checked_style={
                                                            "backgroundColor": "rgba(33,134,244,0.5)",
                                                            "borderColor": "#555",
                                                        },
                                                        label_checked_style={"color": "rgba(33,134,244,0.5)"}, 
                                                        input_style ={"cursor": "pointer",},
                                                        inline=True),
                        ], style={"padding": "0 0 0 10px"}),
                        dbc.Col([
                            dbc.Checklist(options = opcionesCEs_1, value=[], id="OpCEs_1",
                                input_checked_style={
                                    "backgroundColor": "rgba(33,134,244,0.5)",
                                    "borderColor": "#555",
                                },
                                label_checked_style={"color": "rgba(33,134,244,0.5)"}, 
                                input_style ={"cursor": "pointer",},
                                inline=True),
                        ], style={"padding": "27px 0 0 0"}),

                    ]), style={"padding-top": "10px"}
                )
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Button( "Guardar", active=True, id="btn-G", n_clicks=0, disabled=True),
                    dcc.Download(id="download-proposal"),
                ]),

                dbc.Col([
                    dbc.Button("Reporte", active=True, id="btn-R", n_clicks=0, disabled=True),
                    dcc.Download(id="download-reporte"),
                ]),

                dbc.Col([
                    dbc.Button("Ocupación", active=True, id="btn-O", n_clicks=0, disabled=True),
                    dcc.Download(id="download-ocupacion"),
                ]),

                dbc.Col([
                    dbc.Button("Iniciar", active=True, id="btn-I", n_clicks=0, disabled=True),
                ]),

            ], style={"padding": "20px 0 0 0"}),
        ], style={"width": "33.33%", "padding": "6px 6px 6px 6px"}),

        dbc.Col(
            html.Div([
                dash_table.DataTable(id='datatable-upload-1-container',
                    page_action='none',
                    filter_action='native',
                    style_table = style_tabla,
                    style_header = header_tablas,
                    style_cell = cell_tablas, 
                    style_data = data_table,
                    style_data_conditional=[style_data_condition],
                    editable=True, 
                    row_deletable=True, 
                    page_size=12,
                ),
            ]), style={"width": "33.33%"}
        ),
    ],

    className="tables_SP",),
    dbc.Row( # Tabla de resultados 
        dbc.Col(
            html.Div(id='tab_r')
        ),

    className="table_result")
])


# ************************ Funcional **************************** #

def parse_contents(contents, filename):
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    if 'csv' in filename:
        contenido = io.StringIO(decoded.decode('latin-1'))

        # Supongamos que el usuario cargó un archivo CSV.
        csv_reader = list(csv.reader(contenido, delimiter=','))

        return pd.DataFrame(leer_csv(csv_reader))

    elif 'xls' in filename:
        # Supongamos que el usuario cargó un archivo de Excel.
        return pd.read_excel(io.BytesIO(decoded))

def analizar_contenido(contents, filename):
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    if 'csv' in filename:
        # Supongamos que el usuario cargó un archivo CSV.
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
            
    elif 'xls' in filename:
        # Supongamos que el usuario cargó un archivo de Excel.
        return pd.read_excel(io.BytesIO(decoded))

@callback(
    [Output('datatable-upload-container', 'data'), 
     Output('datatable-upload-container', 'columns'),
     Output('datatable-upload-1-container', 'data'),
     Output('datatable-upload-1-container', 'columns'),
     Output('btn-G',"disabled"), Output('btn-R',"disabled"),
     Output('btn-O',"disabled"), Output('int_can',"disabled"),
     Output('select_band',"disabled"), Output('seg_bajo',"disabled"),
     Output('seg_alto',"disabled"), Output('Servis-dropdown',"disabled"),
     Output('OpCEs_0', 'options'), Output('OpCEs_1', 'options'),
     Output('VerServicios', 'options'), 
     Output('datatable-upload', 'contents'), 
     Output('datatable-upload-1', 'contents'),],
    [Input('datatable-upload', 'contents'), 
     Input('datatable-upload-1', 'contents'),],
    [State('datatable-upload', 'filename'),
     State('datatable-upload-1', 'filename'),
     State('VerServicios', 'options'),
     State('OpCEs_0', 'options'), State('OpCEs_1', 'options'),
     ],
     prevent_initial_call=True,)
def update_output(contentsS, contentsP, filenameS, filenameP, Vserv, Ops0, Ops1):

    if contentsS is None and contentsP is None: raise PreventUpdate

    actBtnR = True

    if filenameS is not None and filenameP is not None:
        actBtnR = False

    if contentsS is not None:
        df_S = parse_contents(contentsS, filenameS)
        df_S = df_S.rename_axis('#').reset_index()

        if filenameS is not None and filenameP is None:

            Vserv[0]['disabled'] = False

            for i in range(len(Ops0)):
                Ops0[i]['disabled'] = False

            for i in range(len(Ops1)):
                Ops1[i]['disabled'] = False


        return (df_S.to_dict('records'), 
                [{"name": i, "id": i, 'deletable':True, 'renamable': True} for i in df_S.columns],
                no_update, no_update, no_update, actBtnR, False, False, False, False, 
                False, False, Ops0, Ops1, Vserv, None, None)

    if contentsP is not None:
        df_P = analizar_contenido(contentsP, filenameP)
        df_P = df_P.rename_axis('#').reset_index()

        if filenameS is None and filenameP is not None:

            Vserv[0]['disabled'] = False

            for i in range(len(Ops0)):
                Ops0[i]['disabled'] = False

            for i in range(len(Ops1)):
                Ops1[i]['disabled'] = False

        return (no_update, 
                no_update, 
                df_P.to_dict('records'), 
                [{"name": i, "id": i, 'deletable': True, 'renamable': True} for i in df_P.columns], 
                False, actBtnR, no_update, no_update, no_update, no_update, 
                no_update, no_update, Ops0, Ops1, Vserv, None, None)

def genFig(datos):

    nuevaFig = go.Figure(data=datos, layout=style_graf_S)

    nuevaFig.update_layout(
                shapes = [],
                xaxis_showgrid=True,
                yaxis_showgrid=True,
                xaxis_zeroline=True, 
                yaxis_zeroline=True,
                xaxis_gridcolor='rgba(63, 63, 63, 0.060)',
                yaxis_gridcolor='rgba(63, 63, 63, 0.060)',
                xaxis_zerolinecolor='rgb(63,63,63)',
                yaxis_zerolinecolor='rgb(63,63,63)',
                yaxis=dict(
                    linecolor='rgba(0,0,0, 0)',
                    ),
                )
    
    return nuevaFig

######### Inicio graficar y actualizar Espectro ***********************************

@callback(
    Output('datatable-upload-graph', 'figure'),
    Input('datatable-upload-container', 'data'),
    Input('datatable-upload-1-container', 'data'),
    State('datatable-upload-graph', 'figure'),
)
def display_graph(rowsS, rowsP, fig):

    if (fig is None):

        fig = dict({
                    'data': [{
                        'x': [],
                        'y': [],
                        'type': 'markers'
                    }],'layout': style_graf
                })

        return fig

    df_S = pd.DataFrame(rowsS)
    df_P = pd.DataFrame(rowsP, dtype = 'float64')

    datos=[]

    definicion = 26

    if(not(df_S.empty) or len(df_S.columns) >= 1):

        df_S[["Frecuencias", 
            "P.I.R.E (dBW)", 
            "Anchos de banda"]] = df_S[["Frecuencias", 
                                    "P.I.R.E (dBW)", 
                                    "Anchos de banda"]].apply(pd.to_numeric)

        dS = genPorta(df_S[df_S.columns[1]], 
                        df_S[df_S.columns[2]], 
                        df_S[df_S.columns[3]],
                        definicion)

        df_GS = pd.DataFrame(data=dS)

        for i in range(len(df_GS)):
            objeto={
                'x': df_GS[df_GS.columns[0]][i],
                'y': df_GS[df_GS.columns[1]][i],
                'name': ETIQUETA_1,
                'showlegend': False,
                'mode': 'lines',
                'opacity': 0.9,
                'marker': {
                    'color': 'rgba(33,134,244,0.5)',
                    'size': 6,
                    'line': {
                        'width': 0.5, 
                        'color': 'rgba(255, 255, 255, 0)'
                    }
                }
            }

            trace = go.Scattergl(objeto)
            datos.insert(i+1, trace)

            if(len(datos)==0): 
                datos.insert(len(datos), trace)

            else:
                datos.insert(len(datos)+i+1, trace)
    
    if(not(df_P.empty) or len(df_P.columns) >= 1):

        framesXP = [df_P[df_P.columns[1]], df_P[df_P.columns[2]]]
        framesAP = [df_P[df_P.columns[3]], df_P[df_P.columns[3]]]
        framesYP = [df_P[df_P.columns[4]], df_P[df_P.columns[4]]]

        frecuencias = pd.concat(framesXP, ignore_index=True)
        Potencias = pd.concat(framesYP, ignore_index=True)
        Anchos_de_banda = pd.concat(framesAP, ignore_index=True)

        dP = genPorta(frecuencias, 
                        Potencias, 
                        Anchos_de_banda,
                        definicion)

        df_GP = pd.DataFrame(data=dP)

        for i in range(len(df_GP)):

            objeto={
                'x': df_GP[df_GP.columns[0]][i],
                'y': df_GP[df_GP.columns[1]][i],
                'name': ETIQUETA_2,
                'showlegend': False,
                'mode': 'lines',
                'opacity': 0.9,
                'marker': {
                    'color': 'rgba(244, 33, 33, 0.5)',
                    'size': 6,
                    'line': {
                        'width': 0.5, 
                        'color': 'rgba(255, 255, 255, 0)'
                    }
                }
            }

            if(len(datos)==0): 
                trace = go.Scattergl(objeto)
                datos.insert(len(datos), trace)


            else:
                trace = go.Scattergl(objeto)
                datos.insert(len(datos)+i+1, trace)

    newFig = genFig(datos)

    newFig.update_layout(xaxis=dict(
                                    linecolor='rgba(0,0,0, 0)',
                                    rangeslider=dict(visible=False)))

    return newFig

######### Fin graficar y actualizar Espectro ***********************************

# Genera una visualización de la planeacion espectrar en la zona de visualización
@callback(
        Output('datatable-upload-graph', 'figure', allow_duplicate=True),
        Input('VerServicios', 'value'),
        Input('OpCEs_0', 'value'), 
        Input('OpCEs_1', 'value'),
        State('datatable-upload-graph', 'figure'),
        prevent_initial_call=True,
)
def grafPlanE(Vserv, Ops0, Ops1, fig):

    if(fig is None): raise PreventUpdate

    if('View' in Vserv):

        Ops = Ops0 + Ops1

        if(Ops == []):
            trigger = len(ctx.triggered_prop_ids)
            if(trigger<2): return genFig(fig.get('data', []))

            return no_update

        global checkAct

        checkAct = dict(map(lambda x: (x[0], False), checkAct.items()))

        fig = go.Figure(fig)

        dataTrazos = TraceInfoData(fig)
        trazos_actuales = dataTrazos.traces

        layoutTrazos = TraceInfoLayout(fig)
        layout_actual = layoutTrazos.traces
        segmento = layoutTrazos.tamView

        shapesActivos = set(layoutTrazos.names)
        shapeSeleccionado = set(Ops)

        keep = shapesActivos & shapeSeleccionado
        delete = shapesActivos ^ keep
        new = keep ^ shapeSeleccionado

        newFig = genFig(trazos_actuales)

        csv_tablas = traerData()

        for Abreviatura in rangosRF_MHz: 
            if(rangosRF_MHz[Abreviatura][0] <= segmento[0] and segmento[1] < rangosRF_MHz[Abreviatura][1]): band = Abreviatura 

        if('L' in Ops and not checkAct['L']):
            checkAct['L'] = True
            
            Lb_B = csv_tablas[csv_tablas[band+'.Lib.B'].notna()][band+'.Lib.B']

            Lb_A =  csv_tablas[csv_tablas[band+'.Lib.A'].notna()][band+'.Lib.A']

            Libre = list(zip(Lb_B, Lb_A))


            for sL in Libre:

                newFig.add_vrect(
                        name='L',
                        x0=sL[0], x1=sL[1],
                        label=dict(
                            text="Libre",
                            textposition="top center",
                            font=dict(size=11, family="Arial"),
                        ),
                        fillcolor="#33CCFF",
                        opacity=0.06,
                        layer="below", 
                        line_width=1,
                        line_color="#33CCFF",)

        if('P' in Ops and not checkAct['P']):
            checkAct['P'] = True

            Protegido = list(csv_tablas[csv_tablas[band+'.Pro'].notna()][band+'.Pro'])

            for fP in Protegido:
                if(segmento[0]<=fP and fP<=segmento[1]):

                    # Añadir región
                    newFig.add_vrect(
                            name='P',
                            x0=fP, x1=fP,
                            label=dict(
                                text="Protegido",
                                textposition="top center",
                                font=dict(size=11, family="Arial"),
                            ),
                            fillcolor="#FF0066",
                            opacity=0.06,
                            layer="below", 
                            line_width=5,
                            line_color="#FF0066",)

            
        if('S' in Ops and not checkAct['S']):
            checkAct['S'] = True

            Smm_B = csv_tablas[csv_tablas[band+'.SMM.B'].notna()][band+'.SMM.B']

            Smm_A =  csv_tablas[csv_tablas[band+'.SMM.A'].notna()][band+'.SMM.A']

            Maritimo = list(zip(Smm_B, Smm_A))

            for sM in Maritimo:

                # Añadir región
                newFig.add_vrect(
                        name='S',
                        x0=sM[0], x1=sM[1],
                        label=dict(
                            text="Móvil Maritimo",
                            textposition="top center",
                            font=dict(size=11, family="Arial"),
                        ),
                        fillcolor="#66FF33",
                        opacity=0.06,
                        layer="below", 
                        line_width=1,
                        line_color="#66FF33",)

        if('F' in Ops and not checkAct['F']):
            checkAct['F'] = True

            Frontera = list(csv_tablas[csv_tablas[band+'.Fron'].notna()][band+'.Fron'])

            for fF in Frontera:
                if(segmento[0]<=fF and fF<=segmento[1]):

                    # Añadir región
                    newFig.add_vrect(
                            name='F',
                            x0=fF, x1=fF,
                            label=dict(
                                text="Fontera",
                                textposition="top center",
                                font=dict(size=11, family="Arial"),
                            ),
                            fillcolor="#CC66FF",
                            opacity=0.06,
                            layer="below", 
                            line_width=5,
                            line_color="#CC66FF",)

        if('C' in Ops and not checkAct['C']):
            checkAct['C'] = True

            # Añadir región
            newFig.add_vrect(
                    name='C',
                    x0=162.0125, x1=162.0375,
                    label=dict(
                        text="Determinado",
                        textposition="top center",
                        font=dict(size=11, family="Arial"),
                    ),
                    fillcolor="#FF9999",
                    opacity=0.06,
                    layer="below", 
                    line_width=1,
                    line_color="#FF9999",)

        if('O' in Ops and not checkAct['O']):
            checkAct['O'] = True

            # Añadir región
            newFig.add_vrect(
                    name='O',
                    x0=173.0750, x1=173.0750,
                    label=dict(
                        text="Otros",
                        textposition="top center",
                        font=dict(size=11, family="Arial"),
                    ),
                    fillcolor="#FFFF00",
                    opacity=0.06,
                    layer="below", 
                    line_width=5,
                    line_color="#FFFF00",)

        if(not delete==set()):

            # Obtener índices de shapes para eliminar
            d_index = [layoutTrazos.names.index(d) for d in delete]

            # Eliminar los shapes de los shape actuales
            # ordenar los índices en orden descendente
            for i in sorted(d_index, reverse=True):
                layout_actual.pop(i)

            newFig.update_layout(shapes=layout_actual,)

        return newFig
    
    return no_update


# Descarga de la tabla propueta
@callback(
    Output("download-proposal", "data"),
    Input("btn-G", "n_clicks"),
    State('datatable-upload-1-container', 'data'),
    prevent_initial_call=True,
)
def guardarPropuesta(n, rowsP):

    df_P = pd.DataFrame(rowsP)

    if n is None:
        
        return []

    elif (n > 0):

        return dcc.send_data_frame(df_P.set_index('#').to_csv, ETIQUETA_2 + "_"+str(n)+"_.csv")

# Genera reporte de ocupación espectral
@callback(
    Output("download-ocupacion", "data"),
    Input("btn-O", "n_clicks"),
    State("int_can", "value"),
    State("select_band", "value"),
    State("seg_bajo", "value"),
    State("seg_alto", "value"),
    State("OpCEs_0", "value"),
    State("OpCEs_1", "value"),
    State('Servis-dropdown', 'value'),
    State('datatable-upload-container', 'data'),
)
def analizar(n, can, ban, bajo, alto, OpCEs_0, OpCEs_1, SerPer, rowO):

    if n is None:
        
        return []

    elif (n > 0):

        now = datetime.now()
        format = now.strftime('%d%m%y_%H-%M-%S')

        con = pd.DataFrame(rowO)['Frecuencias'].drop_duplicates().reset_index()

        df_O = Ocupacion(ban, float(can), float(bajo), float(alto), OpCEs_0+OpCEs_1, SerPer, con)

        return dcc.send_data_frame(df_O.to_excel, "Ocupación_"+format+".xlsx", index = False, sheet_name='Reporte de Ocupación')

# Genera reportes de invación espectral
@callback(
    Output("download-reporte", "data"),
    Input("btn-R", "n_clicks"),
    State('datatable-upload-container', 'data'),
    State('datatable-upload-1-container', 'data'),
)
def analizar(n, rowS, rowP):

    if n is None:

        return []

    elif (n > 0):

        now = datetime.now()
        format = now.strftime('%d%m%y_%H-%M-%S')

        dfS = pd.DataFrame(rowS)
        dfP = pd.DataFrame(rowP)

        df = EstudioDeInvacion(dfS, dfP)

        return dcc.send_data_frame(df.to_excel, "Reporte_"+format+".xlsx", index = False, sheet_name="Reporte de disponibilidad")

# ********************* Fin Funcional **************************** #
