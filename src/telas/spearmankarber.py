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
    especie="D.similis",
    trim=0.0, 
    alfa=0.05,
):
    """
    Calcula a EC50 via Spearman-Karber Clássico (USEPA / Trim 0%) 
    e gera o relatório formatado com alinhamento visual preciso.
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

    # Separa apenas as concentrações expostas (> 0) para evitar log(0)
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
        c_abaixo = c_exp[p_exp < 0.5]
        c_acima = c_exp[p_exp >= 0.5]
        
        if len(c_abaixo) > 0 and len(c_acima) > 0:
            c_a = np.max(c_abaixo)
            c_b = np.min(c_acima)
            ec50 = np.sqrt(c_a * c_b)
            ic_confiavel = False
        else:
            ec50 = np.nan
            ic_confiavel = False
    else:
        # -------------------------------------------------------------
        # 3. SPEARMAN-KARBER PURO (MÉTODO OFICIAL USEPA)
        # -------------------------------------------------------------
        log_c = np.log10(c_exp)
        n_doses = len(c_exp)
        
        # Pontos médios dos intervalos (log_X)
        log_X = np.zeros(n_doses)
        dist_0 = log_c[1] - log_c[0] if n_doses > 1 else 0.3
        log_X[0] = log_c[0] - (dist_0 / 2.0)
        
        for i in range(1, n_doses):
            log_X[i] = (log_c[i - 1] + log_c[i]) / 2.0

        # Diferença incremental de mortalidade (dp_i)
        dp = np.diff(np.concatenate(([0.0], p_exp)))
        
        # Estimativa da EC50
        log_ec50 = np.sum(dp * log_X)
        ec50 = 10**log_ec50 if not np.isnan(log_ec50) else np.nan
        
        # Variância (Fórmula Hamilton / USEPA)
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
            
        # Validação do Intervalo de Confiança 95%
        if var_sk > 0 and not np.isnan(var_sk) and not np.isnan(ec50):
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
    # 4. FORMATAÇÃO DO TEXTO DO RELATÓRIO (ESPAÇAMENTOS E COLUNAS)
    # -------------------------------------------------------------
    linhas_raw = ""
    for c, n, m in zip(concentracoes, totais, mortos):
        if c == 0:
            c_str = ".00"
        elif 0 < c < 1:
            c_str = f"{c:.2f}".lstrip('0')
        else:
            c_str = f"{c:.2f}"
        
        # Alinhamento das colunas de dados brutos
        linhas_raw += f"        {c_str:>6}        {int(n):>3}        {int(m):>3}\n"

    # Formatação do bloco final de estimativa
    if ic_confiavel and li_sk is not None and ls_sk is not None:
        est_texto = (
            f"SPEARMAN-KARBER ESTIMATES:   EC50:          {ec50:>7.2f}\n"
            f"                             95% LOWER CONFIDENCE: {li_sk:>7.2f}\n"
            f"                             95% UPPER CONFIDENCE: {ls_sk:>7.2f}"
        )
    else:
        ec50_str = "nan" if (ec50 is None or np.isnan(ec50)) else f"{ec50:>7.2f}"
        est_texto = (
            f"SPEARMAN-KARBER ESTIMATES:   EC50:          {ec50_str}\n"
            f"                             95% CONFIDENCE LIMITS\n"
            f"                             ARE NOT RELIABLE."
        )

    relatorio = f"""DATE:  {data:<10}    TEST NUMBER: {num_teste:<10}    DURATION:  {duracao} h
TOXICANT : {num_teste}
SPECIES: {especie}

RAW DATA:   Concentration     Number     Mortalities
--------        (%)          Exposed
{linhas_raw}
SPEARMAN-KARBER TRIM:              {trim:>5.2f}%

{est_texto}
--------------------------------------------------------------------------------"""
    
    return relatorio