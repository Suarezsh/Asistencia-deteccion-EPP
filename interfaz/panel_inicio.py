import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from conexion.database import (
    contar_total_empleados, 
    contar_asistencias_hoy, 
    contar_incidentes_epp_hoy, 
    obtener_asistencia_ultimos_7_dias
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import date, timedelta

class PanelInicio(ttk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.parent = parent
        self.controlador = controlador
        
        # Estilo para los gráficos
        plt.style.use('seaborn-v0_8-bright') 

        # Inicializar figuras y ejes para los gráficos
        self.fig_semanal, self.ax_semanal = plt.subplots(figsize=(7, 3.5), dpi=100)
        self.fig_epp, self.ax_epp = plt.subplots(figsize=(4, 3.5), dpi=100)

        self.crear_widgets()
        self.actualizar_dashboard()

    def crear_widgets(self):
        # Usar grid para una maquetación consistente
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- Fila de KPIs ---
        kpi_frame = ttk.Frame(self, padding=(20, 10))
        kpi_frame.grid(row=0, column=0, sticky="ew")
        kpi_frame.columnconfigure((0, 1, 2), weight=1)

        # Crear y posicionar las tarjetas KPI
        card1, self.lbl_total_empleados = self.crear_kpi_card(kpi_frame, "Empleados Totales", "0", "info")
        card1.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        card2, self.lbl_asistencias_hoy = self.crear_kpi_card(kpi_frame, "Asistencias Hoy", "0", "success")
        card2.grid(row=0, column=1, padx=10, sticky="ew")

        card3, self.lbl_incidentes_hoy = self.crear_kpi_card(kpi_frame, "Incidentes EPP Hoy", "0", "danger")
        card3.grid(row=0, column=2, padx=(10, 0), sticky="ew")

        # --- Fila de Gráficos ---
        graficos_frame = ttk.Frame(self, padding=(20, 10))
        graficos_frame.grid(row=1, column=0, sticky="nsew")
        graficos_frame.columnconfigure(0, weight=2)
        graficos_frame.columnconfigure(1, weight=1)
        graficos_frame.rowconfigure(0, weight=1)

        # Gráfico de Asistencia Semanal
        semanal_frame = ttk.Labelframe(graficos_frame, text="Asistencia de los Últimos 7 Días", padding=15)
        semanal_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self.canvas_semanal = FigureCanvasTkAgg(self.fig_semanal, master=semanal_frame)
        self.canvas_semanal.get_tk_widget().pack(expand=True, fill=BOTH)

        # Gráfico de Cumplimiento EPP
        epp_frame = ttk.Labelframe(graficos_frame, text="Cumplimiento EPP (Hoy)", padding=15)
        epp_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        self.canvas_epp = FigureCanvasTkAgg(self.fig_epp, master=epp_frame)
        self.canvas_epp.get_tk_widget().pack(expand=True, fill=BOTH)

    def crear_kpi_card(self, parent, titulo, valor_inicial, bootstyle):
        """Crea una tarjeta KPI y devuelve el frame y la etiqueta del valor."""
        card = ttk.Frame(parent, padding=10, bootstyle=f"{bootstyle}")
        
        lbl_titulo = ttk.Label(card, text=titulo, font=("Helvetica", 12), bootstyle=f"inverse-{bootstyle}")
        lbl_titulo.pack(pady=(0, 5), fill=X)
        
        lbl_valor = ttk.Label(card, text=valor_inicial, font=("Helvetica", 28, "bold"), bootstyle=f"inverse-{bootstyle}")
        lbl_valor.pack(pady=(5, 0), fill=X)
        
        return card, lbl_valor

    def actualizar_dashboard(self):
        """Actualiza todos los datos del dashboard."""
        total_empleados = contar_total_empleados()
        asistencias_hoy = contar_asistencias_hoy()
        incidentes_hoy = contar_incidentes_epp_hoy()

        self.lbl_total_empleados.config(text=str(total_empleados))
        self.lbl_asistencias_hoy.config(text=str(asistencias_hoy))
        self.lbl_incidentes_hoy.config(text=str(incidentes_hoy))

        self.actualizar_grafico_semanal()
        self.actualizar_grafico_epp(asistencias_hoy, incidentes_hoy)

    def actualizar_grafico_semanal(self):
        self.ax_semanal.clear()
        datos = obtener_asistencia_ultimos_7_dias()
        
        datos_dict = {d[0]: d[1] for d in datos}
        
        fechas = [(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
        dias_labels = [f.strftime('%a %d') for f in fechas]
        valores = [datos_dict.get(f.strftime('%Y-%m-%d'), 0) for f in fechas]

        self.ax_semanal.bar(dias_labels, valores, color='#0d6efd')
        self.ax_semanal.set_title("Asistencias por Día", fontsize=12, weight='bold')
        self.ax_semanal.set_ylabel("Nº de Empleados")
        self.ax_semanal.tick_params(axis='x', rotation=0)
        self.fig_semanal.tight_layout(pad=1.5)
        self.canvas_semanal.draw()

    def actualizar_grafico_epp(self, asistencias, incidentes):
        self.ax_epp.clear()
        
        cumplimiento = asistencias - incidentes
        
        if asistencias > 0:
            labels = 'Cumplimiento', 'Incidentes'
            sizes = [cumplimiento, incidentes]
            colors = ['#198754', '#dc3545']
            explode = (0, 0.1) if incidentes > 0 and cumplimiento > 0 else (0, 0)
            
            self.ax_epp.pie(sizes, explode=explode, labels=labels, colors=colors,
                            autopct='%1.1f%%', shadow=False, startangle=90,
                            wedgeprops={'linewidth': 0})
            self.ax_epp.axis('equal')
        else:
            self.ax_epp.text(0.5, 0.5, 'Sin datos de hoy', 
                             horizontalalignment='center', verticalalignment='center',
                             fontsize=10, color='gray')
            self.ax_epp.axis('off')

        self.ax_epp.set_title("Estado EPP (Entradas)", fontsize=12, weight='bold')
        self.fig_epp.tight_layout(pad=1.5)
        self.canvas_epp.draw()

    def activate(self):
        """Se llama cuando el panel se muestra para actualizar los datos."""
        self.actualizar_dashboard()

if __name__ == '__main__':
    app = ttk.Window(themename="litera")
    app.title("Dashboard de Prueba")
    app.geometry("1024x600")
    panel = PanelInicio(app, None)
    panel.pack(expand=True, fill=BOTH)
    app.mainloop()
