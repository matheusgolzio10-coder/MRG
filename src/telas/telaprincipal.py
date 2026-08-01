import customtkinter as ctk


class TelaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Confirgurações da janela
        self.title("MRG")
        self.geometry("550x150")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Layout colunas
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Carregar componentes de tela
        self.componentes()
    
    def componentes(self):
        # Labels
        ctk.CTkLabel(self, text="DATA DO TESTE", font=("Arial", 15)).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        ctk.CTkLabel(self, text="NÚMERO DO TESTE", font=("Arial", 15)).grid(row=0, column=1, padx=10, pady=(10, 5), sticky="w")
        ctk.CTkLabel(self, text="TIPO DE TESTE", font=("Arial", 15)).grid(row=0, column=2, padx=10, pady=(10, 5), sticky="w")

        # Frame para data
        self.data_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.data_frame.grid(row=1, column=0, padx=10, sticky="w")

        # Entradas
        self.data = ctk.CTkEntry(self.data_frame, placeholder_text="DD/MM/AAAA")
        self.data.grid(row=0, column=0, sticky="w")

        self.numero = ctk.CTkEntry(self)
        self.numero.grid(row=1, column=1, padx=10, sticky="w")

        self.tipo = ctk.CTkComboBox(self, values=["Daphnia similis", "Ceriodaphnia dubia"])
        self.tipo.grid(row=1, column=2, padx=10, sticky="w")

        # Botões
        self.data_button = ctk.CTkButton(self.data_frame, text="📆", width=20)
        self.data_button.grid(row=0, column=1, padx=(10,0), sticky="w")

        self.prosseguir = ctk.CTkButton(self, text="Prosseguir", command=self.prosseguir)
        self.prosseguir.grid(row=2, column=2, pady=30, padx=10, sticky="w")

    def prosseguir(self):
        print(self.data.get(), self.numero.get(), self.tipo.get())

def iniciar_app():
    app = TelaPrincipal()
    app.mainloop()
        
