import numpy as np
from scipy.stats import norm

def calcular_daphnia_e_gerar_relatorio(
    concentracoes, 
    totais, 
    mortos, 
    data, 
    un,
    num_teste, 
    duracao=48, 
    especie="Daphnia similis",
    trim=0.0, 
    alfa=0.05,
):
    """
    Calcula a EC50 via Spearman-Karber (Trim 0%) e formata o resultado
    no modelo padrão de relatório impresso.
    """
    conc = np.array(concentracoes, dtype=float)
    tot = np.array(totais, dtype=float)
    mort = np.array(mortos, dtype=float)
    proporcoes = mort / tot
    z = norm.ppf(1 - alfa / 2)
    
    # -------------------------------------------------------------
    # 1. VALIDAÇÃO DO CONTROLE
    # -------------------------------------------------------------
    idx_ctrl = np.argmin(conc)
    mortalidade_controle = proporcoes[idx_ctrl]
    
    if mortalidade_controle > 0.10:
        return f"ERRO: Ensaio Inválido. Mortalidade no controle ({mortalidade_controle*100:.1f}%) excedeu 10%."

    # Separa os dados de teste (exclui o controle)
    mask = conc > 0
    c_exp = conc[mask]
    t_exp = tot[mask]
    m_exp = mort[mask]
    p_exp = m_exp / t_exp
    
    ec50 = None
    li_sk = None
    ls_sk = None
    ic_confiavel = False

    # -------------------------------------------------------------
    # 2. VERIFICAÇÃO DE TRANSIÇÃO ABRUPTA OU SEM RESPOSTA PARCIAL
    # -------------------------------------------------------------
    tem_intermediario = np.any((p_exp > 0) & (p_exp < 1.0))
    maior_que_50 = np.any(p_exp >= 0.5)
    menor_que_50 = np.any(p_exp <= 0.5)

    if not (tem_intermediario and maior_que_50 and menor_que_50):
        # Média Geométrica em caso de transição direta (0% a 100%)
        c_abaixo = c_exp[p_exp < 0.5]
        c_acima = c_exp[p_exp >= 0.5]
        
        if len(c_abaixo) > 0 and len(c_acima) > 0:
            c_a = np.max(c_abaixo)
            c_b = np.min(c_acima)
            ec50 = np.sqrt(c_a * c_b)
            ic_confiavel = False  # Transição abrupta -> Limites não confiáveis
        else:
            return "ERRO: Não foi possível determinar a EC50."
    else:
        # -------------------------------------------------------------
        # 3. SPEARMAN-KARBER PURO (TRIM FIXO EM 0%)
        # -------------------------------------------------------------
        log_c = np.log10(c_exp)
        n_doses = len(c_exp)
        
        dp = np.diff(np.concatenate(([0.0], p_exp)))
        log_ec50 = np.sum(dp * log_c)
        ec50 = 10**log_ec50
        
        # Variância
        var_sk = 0.0
        for i in range(n_doses):
            w_i = (p_exp[i] * (1.0 - p_exp[i])) / (t_exp[i] - 1.0 if t_exp[i] > 1.0 else t_exp[i])
            if i == 0:
                factor = log_c[1] - log_c[0]
            elif i == n_doses - 1:
                factor = log_c[n_doses - 1] - log_c[n_doses - 2]
            else:
                factor = log_c[i + 1] - log_c[i - 1]
            var_sk += ((factor / 2.0) ** 2) * w_i
            
        # Validação do IC 95%
        if var_sk > 0 and not np.isnan(var_sk):
            se_sk = np.sqrt(var_sk)
            li_calc = 10**(log_ec50 - z * se_sk)
            ls_calc = 10**(log_ec50 + z * se_sk)
            
            if li_calc > 0 and ls_calc <= (max(c_exp) * 2):
                li_sk = li_calc
                ls_sk = ls_calc
                ic_confiavel = True
            else:
                ic_confiavel = False
        else:
            ic_confiavel = False

    # -------------------------------------------------------------
    # 4. FORMATAÇÃO DO TEXTO DO RELATÓRIO
    # -------------------------------------------------------------
    linhas_raw = ""
    for c, n, m in zip(concentracoes, totais, mortos):
        # Formata os decimais conforme o modelo (ex: .78 para 0.78)
        if 0 < c < 1:
            c_str = f"{c:.2f}".lstrip('0')
        else:
            c_str = f"{c:.2f}"
        
        linhas_raw += f"               {c_str:>6}                {int(n):>2}                   {int(m):>2}\n"

    if ic_confiavel and li_sk is not None and ls_sk is not None:
        ic_texto = f"95% CONFIDENCE LIMITS\n                                       {li_sk:.2f} TO {ls_sk:.2f}"
    else:
        ic_texto = "95% CONFIDENCE LIMITS\n                                       ARE NOT RELIABLE."

    relatorio = f"""DATE:   {data}               TEST NUMBER: {num_teste}         DURATION:   {duracao} h
TOXICANT :   {num_teste}
SPECIES:   {especie}

RAW DATA:   Concentration         Number         Mortalities
--------    ({un})                  Exposed
{linhas_raw}

SPEARMAN-KARBER TRIM:                   {trim:.2f}%

SPEARMAN-KARBER ESTIMATES:     EC50:           {ec50:.2f}
                                       {ic_texto}
--------------------------------------------------------------------------------"""
    
    return relatorio
