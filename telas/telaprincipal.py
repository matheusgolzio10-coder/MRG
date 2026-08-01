import customtkinter as ctk


class TelaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Confirgurações da janela
        self.title("MRG")
        self.geometry("600x300")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Layout colunas
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Carregar componentes de tela
    
    def componentes(self):
        # Labels
        ctk.CTkLabel(self, text="DATA DO TESTE").grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
