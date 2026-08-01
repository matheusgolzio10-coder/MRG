import customtkinter as ctk
from telas.spearmankarber import calcular_daphnia_e_gerar_relatorio

class Daphnia(ctk.CTkToplevel):
    def __init__(self, data, numero, tipo):
        super().__init__()

        # Dados iniciais
        self.data = data
        self.numero = numero
        self.tipo = tipo

        # Configurações da janela
        self.title("Daphnia similis")
        self.geometry("700x450")
        self.grab_set()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Layout colunas
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.componentes()

    def componentes(self):
        # Labels
        ctk.CTkLabel(self, text="DATA DO TESTE", font=("Arial", 15)).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        ctk.CTkLabel(self, text="NÚMERO DO TESTE", font=("Arial", 15)).grid(row=0, column=1, padx=10, pady=(10, 5), sticky="w")
        ctk.CTkLabel(self, text="TIPO DE TESTE", font=("Arial", 15)).grid(row=0, column=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self, text=self.data, font=("Arial", 20), text_color="red").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self, text=self.numero, font=("Arial", 20), text_color="red").grid(row=1, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self, text=self.tipo, font=("Arial", 20), text_color="red").grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Frame para o controle
        self.controle_frame = ctk.CTkFrame(self, fg_color="transparent", border_color="white", border_width=1)
        self.controle_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nw")

        # Labels do controle
        ctk.CTkLabel(self.controle_frame, text="CONTROLE", font=("Arial", 15, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.controle_frame, text="TOTAL", font=("Arial", 13)).grid(row=1, column=1, padx=10, sticky="w")
        ctk.CTkLabel(self.controle_frame, text="MORTOS", font=("Arial", 13)).grid(row=1, column=0, padx=10, sticky="w")

        # Entradas do controle
        self.controle_total = ctk.CTkTextbox(self.controle_frame, fg_color="grey", height=20, width=50, corner_radius=0)
        self.controle_total.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.controle_mortos = ctk.CTkTextbox(self.controle_frame, fg_color="grey", height=20, width=100, corner_radius=0)
        self.controle_mortos.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Frame para amostra
        self.amostra_frame = ctk.CTkFrame(self, fg_color="transparent", border_color="white", border_width=1)
        self.amostra_frame.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Labels da amostra
        ctk.CTkLabel(self.amostra_frame, text="AMOSTRA", font=("Arial", 15, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.amostra_frame, text="CONCENTRAÇÕES", font=("Arial", 13)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(self.amostra_frame, text="MORTOS", font=("Arial", 13)).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(self.amostra_frame, text="TOTAL", font=("Arial", 13)).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(self.amostra_frame, text="UNIDADE", font=("Arial", 13)).grid(row=1, column=3, padx=10, pady=10, sticky="w")

        # Entradas da amostra
        self.amostra_conc = ctk.CTkTextbox(self.amostra_frame, fg_color="grey", corner_radius=0, width=120)
        self.amostra_conc.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.amostra_mortos = ctk.CTkTextbox(self.amostra_frame, fg_color="grey", corner_radius=0, width=120)
        self.amostra_mortos.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.amostra_total = ctk.CTkTextbox(self.amostra_frame, fg_color="grey", corner_radius=0, width=50)
        self.amostra_total.grid(row=2, column=2, padx=10, pady=10, sticky="w")

        self.unidade = ctk.CTkComboBox(self.amostra_frame, values=["%", "mg/L"], width=100)
        self.unidade.grid(row=2, column=3, padx=10, pady=10, sticky="n")

        # Calcular
        self.calcular_button = ctk.CTkButton(self, text="Calcular", command=self.calcular)
        self.calcular_button.grid(row=4, column=2, padx=10, pady=10, sticky="e")

    def calcular(self):
        concentracoes = [0]
        for linha in self.amostra_conc.get("1.0", "end").split("\n"):
            if linha:
                linha = float(linha.replace(",", "."))
                concentracoes.append(linha)

        totais = []
        totais.append(float(self.controle_total.get("1.0", "1.2")))
        for linha in self.amostra_total.get("1.0", "end").split("\n"):
            if linha:
                linha = float(linha.replace(",", "."))
                totais.append(linha)

        tuplas_mortos = []
        for linha in self.controle_mortos.get("1.0", "end").split("\n"):
            if linha:
                valores = linha.split('\t')
                tuplas_mortos.append(tuple(valores))

        for linha in self.amostra_mortos.get("1.0", "end").split("\n"):
            if linha:
                valores = linha.split('\t')
                tuplas_mortos.append(tuple(valores))

        mortos = []
        for k in tuplas_mortos:
            mortos.append(float(k[0]) + float(k[1]))

        self.resultado_tela = ctk.CTkToplevel()
        self.resultado_tela.grab_set()

        self.resultado_tela.title("Resultado")

        self.resultado_tela.geometry("600x500")

        self.textbox_resultado = ctk.CTkTextbox(self.resultado_tela, fg_color="grey", corner_radius=0)
        self.textbox_resultado.pack(fill="both", expand=True)

        self.textbox_resultado.insert("1.0", calcular_daphnia_e_gerar_relatorio(
                    concentracoes, totais, mortos, 
                    data=self.data, 
                    num_teste=self.numero,
                    un=self.unidade.get()
                ))
        
        self.textbox_resultado.configure(state="disabled")

