import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
import requests
import json
import os

PIEZAS_DB = [
    {
        "nombre": "Pieza1",
        "codigos": {"1X1", "4P4", "3N0"},
        "foto": "pieza1.jpg"
    },
    {
        "nombre": "Pieza2",
        "codigos": {"AI1", "AI9"},
        "foto": "pieza2.jpg"
    },
]

class Espaciador(Widget):
    pass

class ConsultarWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self.input = TextInput(hint_text="Ingrese KNR", multiline=False, size_hint_y=None, height=40, font_size=18)
        self.add_widget(self.input)
        self.btn = Button(
            text="Consultar",
            size_hint_y=None,
            height=45,
            background_color=(0.2, 0.5, 0.8, 1),
            color=(1,1,1,1),
            font_size=18,
            bold=True
        )
        self.btn.bind(on_press=self.consultar)
        self.add_widget(self.btn)
        self.result_label = Label(text="", font_size=18, size_hint_y=None, height=40)
        self.add_widget(self.result_label)
        self.img = Image(size_hint_y=None, height=180)
        self.add_widget(self.img)
        self.add_widget(Espaciador())

    def consultar(self, instance):
        knr = self.input.text.strip()
        if not knr:
            self.result_label.text = "Ingrese un KNR válido."
            self.img.source = ""
            return
        url = f"http://assemblylive.sj.audi.vwg:9100/Carinformation/ALL/PRNumberbyFamily/{knr}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                self.result_label.text = "Error en la consulta."
                self.img.source = ""
                return
            data = resp.json()
            codigos_pr = {item["PR"] for item in data.get("PR", []) if "PR" in item}
            piezas_encontradas = []
            for pieza in PIEZAS_DB:
                if pieza["codigos"].issubset(codigos_pr):
                    piezas_encontradas.append(pieza)
            if piezas_encontradas:
                pieza = piezas_encontradas[0]
                self.result_label.text = f"Pieza encontrada: {pieza['nombre']}"
                if os.path.exists(pieza["foto"]):
                    self.img.source = pieza["foto"]
                else:
                    self.img.source = ""
            else:
                self.result_label.text = "No se encontró pieza."
                self.img.source = ""
        except Exception as e:
            self.result_label.text = f"Error: {e}"
            self.img.source = ""

class AdminPiezasWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.add_widget(Label(text="Agregar nueva pieza", font_size=20, bold=True, size_hint_y=None, height=35))
        self.nombre_input = TextInput(hint_text="Nombre de la pieza", multiline=False, size_hint_y=None, height=38, font_size=16)
        self.codigos_input = TextInput(hint_text="Códigos PR (separados por coma)", multiline=False, size_hint_y=None, height=38, font_size=16)
        self.foto_input = TextInput(hint_text="Nombre de archivo de foto", multiline=False, size_hint_y=None, height=38, font_size=16)
        self.add_btn = Button(
            text="Agregar pieza",
            size_hint_y=None,
            height=42,
            background_color=(0.1, 0.7, 0.3, 1),
            color=(1,1,1,1),
            font_size=17,
            bold=True
        )
        self.add_btn.bind(on_press=self.agregar_pieza)
        self.add_widget(self.nombre_input)
        self.add_widget(self.codigos_input)
        self.add_widget(self.foto_input)
        self.add_widget(self.add_btn)
        self.msg_label = Label(text="", font_size=16, size_hint_y=None, height=30)
        self.add_widget(self.msg_label)
        self.add_widget(Label(text="Piezas registradas", font_size=18, bold=True, size_hint_y=None, height=30))
        self.piezas_layout = GridLayout(cols=1, size_hint_y=None, spacing=8, padding=[0,5])
        self.piezas_layout.bind(minimum_height=self.piezas_layout.setter('height'))
        self.scroll = ScrollView(size_hint=(1, 1), size=(self.width, 200))
        self.scroll.add_widget(self.piezas_layout)
        self.add_widget(self.scroll)
        self.actualizar_lista()

    def actualizar_lista(self):
        self.piezas_layout.clear_widgets()
        for idx, pieza in enumerate(PIEZAS_DB):
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=38, spacing=8)
            box.add_widget(Label(text=f"{pieza['nombre']} ({', '.join(pieza['codigos'])})", font_size=16))
            del_btn = Button(
                text="Eliminar",
                size_hint_x=None,
                width=90,
                height=36,
                background_color=(0.8, 0.2, 0.2, 1),
                color=(1,1,1,1),
                font_size=15,
                bold=True
            )
            del_btn.bind(on_press=lambda inst, i=idx: self.eliminar_pieza(i))
            box.add_widget(del_btn)
            self.piezas_layout.add_widget(box)

    def agregar_pieza(self, instance):
        nombre = self.nombre_input.text.strip()
        codigos = {c.strip() for c in self.codigos_input.text.split(",") if c.strip()}
        foto = self.foto_input.text.strip()
        if not nombre or not codigos:
            self.msg_label.text = "Nombre y códigos requeridos."
            return
        PIEZAS_DB.append({"nombre": nombre, "codigos": codigos, "foto": foto})
        self.msg_label.text = "Pieza agregada."
        self.nombre_input.text = ""
        self.codigos_input.text = ""
        self.foto_input.text = ""
        self.actualizar_lista()

    def eliminar_pieza(self, idx):
        if 0 <= idx < len(PIEZAS_DB):
            del PIEZAS_DB[idx]
            self.msg_label.text = "Pieza eliminada."
            self.actualizar_lista()

class MainPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False
        tab1 = TabbedPanelItem(text='Consultar')
        tab1.add_widget(ConsultarWidget())
        tab2 = TabbedPanelItem(text='Administrar piezas')
        tab2.add_widget(AdminPiezasWidget())
        self.add_widget(tab1)
        self.add_widget(tab2)

class MiApp(App):
    def build(self):
        return MainPanel()

if __name__ == "__main__":
    MiApp().run()