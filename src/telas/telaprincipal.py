import customtkinter as ctk
from tkcalendar import Calendar
from telas.daphnia import Daphnia


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
        self.data_entry = ctk.CTkEntry(self.data_frame, placeholder_text="DD/MM/AAAA")
        self.data_entry.grid(row=0, column=0, sticky="w")

        self.numero_entry = ctk.CTkEntry(self)
        self.numero_entry.grid(row=1, column=1, padx=10, sticky="w")

        self.tipo_entry = ctk.CTkComboBox(self, values=["Daphnia similis", "Ceriodaphnia dubia"])
        self.tipo_entry.grid(row=1, column=2, padx=10, sticky="w")

        # Botões
        self.data_button = ctk.CTkButton(self.data_frame, text="📆", width=20, command=self.abrir_calendario)
        self.data_button.grid(row=0, column=1, padx=(10,0), sticky="w")

        self.prosseguir = ctk.CTkButton(self, text="Prosseguir", command=self.prosseguir)
        self.prosseguir.grid(row=2, column=2, pady=30, padx=10, sticky="w")

    def abrir_calendario(self):
        self.janela_data = ctk.CTkToplevel(self)
        self.janela_data.title("Escolha uma data")
        self.janela_data.geometry("250x250")
        self.janela_data.grab_set()

        self.calendario = Calendar(
            self.janela_data,
            date_pattern="dd/mm/yyyy"
        )
        self.calendario.grid(row=0, column=0, sticky="ns")
        ctk.CTkButton(
            self.janela_data,
            text="Selecionar",
            command=self.selecionar_data
        ).grid(row=1, column=0, pady=20, padx=20, sticky="ns")

    def selecionar_data(self):
        data = self.calendario.get_date()
        self.data_entry.delete(0, "end")
        self.data_entry.insert(0, data)
        self.janela_data.destroy()

    def prosseguir(self):
        if self.tipo_entry.get() == "Daphnia similis":
            Daphnia(self.data_entry.get(), self.numero_entry.get(), self.tipo_entry.get())

def iniciar_app():
    app = TelaPrincipal()
    app.mainloop()
        
