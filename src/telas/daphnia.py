import customtkinter as ctk

class Daphnia(ctk.CTkToplevel):
    def __init__(self, data, numero, tipo):
        super().__init__()

        # Dados iniciais
        self.data = data
        self.numero = numero
        self.tipo = tipo

        # Configurações da janela
        self.title("Daphnia similis")
        self.geometry("600x400")
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

