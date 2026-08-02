import numpy as np
from scipy.stats import norm

def _ajustar_pava(m_exp, t_exp):
    p_raw = m_exp / t_exp
    p_adj = p_raw.copy()
    w = t_exp.copy()

    while True:
        violacao = False
        for i in range(len(p_adj) - 1):
            if p_adj[i] > p_adj[i + 1]:
                p_pooled = (p_adj[i] * w[i] + p_adj[i + 1] * w[i + 1]) / (w[i] + w[i + 1])
                p_adj[i] = p_pooled
                p_adj[i + 1] = p_pooled
                violacao = True
                break
        if not violacao:
            break

    return p_adj


def _fmt_conc(val):
    """
    Formata as concentrações exatamente como no MS-DOS USEPA:
    - Menores que 1: omite o zero à esquerda (ex: .00, .78)
    - Demais: 2 casas decimais (ex: 1.56, 100.00)
    """
    if val < 1.0:
        s = f"{val:.2f}"
        return s[1:] if s.startswith("0") else s
    else:
        return f"{val:.2f}"


def _gerar_log_terminal_incalculavel(
    data, num_teste, especie, unidade, duracao, 
    concentracoes, totais, mortos, estimado="e", un_duracao="h", trim_auto="y"
):
    ctrl_tot = int(totais[0])
    ctrl_mort = int(mortos[0])
    
    doses = concentracoes[1:]
    tot_doses = totais[1:]
    mort_doses = mortos[1:]
    num_doses = len(doses)
    
    str_doses = "\n".join([f"{d:g}" if d >= 1 else f"{d}" for d in doses])
    str_mortes = "\n".join([f"{int(m)}" for m in mort_doses])
    
    return f"""ENTER DATE OF TEST: 
{data}
ENTER TEST NUMBER: 
{num_teste}
WHAT IS TO BE ESTIMATED? 
(ENTER "L" FOR LC50 AND "E" FOR EC50) 
{estimado.lower()}
ENTER TEST SPECIES NAME: 
{especie}
ENTER TOXICANT  NAME: 
{num_teste}
ENTER UNITS FOR EXPOSURE CONCENTRATION OF TOXICANT : 
{unidade}
ENTER THE NUMBER OF INDIVIDUALS IN THE CONTROL: 
{ctrl_tot}
ENTER THE NUMBER OF MORTALITIES IN THE CONTROL: 
{ctrl_mort}
ENTER THE NUMBER OF CONCENTRATIONS 
(NOT INCLUDING THE CONTROL;  MAX = 10): 
{num_doses}
ENTER THE  {num_doses} EXPOSURE CONCENTRATIONS (IN INCREASING ORDER): 

{str_doses}
ARE THE NUMBER OF INDIVIDUALS AT EACH EXPOSURE CONCENTRATION EQUAL (Y/N) ? 
{trim_auto.lower()}
ENTER THE NUMBER OF INDIVIDUALS AT EACH EXPOSURE CONCENTRATION: 
{int(tot_doses[0])}
ENTER UNITS FOR DURATION OF EXPERIMENT 
(ENTER "H" FOR HOURS, "D" FOR DAYS, ETC.): 
{un_duracao.lower()}
ENTER DURATION OF TEST: 
{duracao}
ENTER THE NUMBER OF MORTALITIES AT EACH EXPOSURE CONCENTRATION: 

{str_mortes}
WOULD YOU LIKE THE AUTOMATIC TRIM CALCULATION(Y/N) ? 
{trim_auto.lower()}

 MINIMUM REQUIRED TRIM IS TOO LARGE: 100.0,SO SK IS NOT CALCULABLE."""


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
    estimado="e",
    un_duracao="h",
    trim_auto="y"
):
    len_conc = len(concentracoes)
    len_tot = len(totais)
    len_mort = len(mortos)

    if not (len_conc == len_tot == len_mort):
        return (
            f"ERRO DE DADOS: O número de elementos nas listas não coincide!\n"
            f"- Concentrações: {len_conc} | Totais: {len_tot} | Mortalidades: {len_mort}"
        )

    dados_ordenados = sorted(zip(concentracoes, totais, mortos), key=lambda x: x[0])
    conc = np.array([x[0] for x in dados_ordenados], dtype=float)
    tot = np.array([x[1] for x in dados_ordenados], dtype=float)
    mort = np.array([x[2] for x in dados_ordenados], dtype=float)

    proporcoes = mort / tot
    z = norm.ppf(1 - alfa / 2)
    
    idx_ctrl = np.argmin(conc)
    mortalidade_controle = proporcoes[idx_ctrl]
    
    if mortalidade_controle > 0.10:
        return f"ERRO: Ensaio Inválido. Mortalidade no controle ({mortalidade_controle*100:.1f}%) excedeu 10%."

    mask = conc > 0
    c_exp = conc[mask]
    t_exp = tot[mask]
    m_exp = mort[mask]
    p_raw = m_exp / t_exp

    total_mortes_expostas = np.sum(m_exp)
    total_organismos_expostos = np.sum(t_exp)

    if total_mortes_expostas == 0 or total_organismos_expostos == total_mortes_expostas:
        return _gerar_log_terminal_incalculavel(
            data, num_teste, especie, un, duracao, 
            conc, tot, mort, estimado, un_duracao, trim_auto
        )

    houve_inversao = np.any(np.diff(p_raw) < 0)
    p_exp = _ajustar_pava(m_exp, t_exp)

    ec50 = None
    li_sk = None
    ls_sk = None
    ic_confiavel = False

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
            return _gerar_log_terminal_incalculavel(
                data, num_teste, especie, un, duracao, 
                conc, tot, mort, estimado, un_duracao, trim_auto
            )
    else:
        log_c = np.log10(c_exp)
        n_doses = len(c_exp)
        
        log_X = np.zeros(n_doses)
        dist_0 = log_c[1] - log_c[0] if n_doses > 1 else 0.3
        log_X[0] = log_c[0] - (dist_0 / 2.0)
        
        for i in range(1, n_doses):
            log_X[i] = (log_c[i - 1] + log_c[i]) / 2.0

        dp = np.diff(np.concatenate(([0.0], p_exp)))
        log_ec50 = np.sum(dp * log_X)
        ec50 = 10**log_ec50 if not np.isnan(log_ec50) else np.nan
        
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
            
        if var_sk > 0 and not np.isnan(var_sk) and not np.isnan(ec50) and not houve_inversao:
            se_sk = np.sqrt(var_sk)
            li_calc = 10**(log_ec50 - z * se_sk)
            ls_calc = 10**(log_ec50 + z * se_sk)
            
            if li_calc > 0 and ls_calc <= (max(c_exp) * 2):
                li_sk = li_calc
                ls_sk = ls_calc
                ic_confiavel = True

    # -------------------------------------------------------------
    # FORMATAÇÃO DA TABELA E RESULTADOS (CONFORME IMAGEM)
    # -------------------------------------------------------------
    linhas_raw = []
    for c, n, m in zip(conc, tot, mort):
        c_str = _fmt_conc(c)
        linhas_raw.append(f"{c_str:>19} {int(n):>18} {int(m):>12}")

    tabela_dados = "\n".join(linhas_raw)
    sigla = "LC50" if estimado.lower() == "l" else "EC50"
    
    # Trim formatado sem zero à esquerda se for < 1 (ex: .00%)
    trim_str = _fmt_conc(trim) + "%"

    if ic_confiavel and li_sk is not None and ls_sk is not None:
        est_texto = (
            f"SPEARMAN-KARBER ESTIMATES:     {sigla}:          {ec50:>7.2f}\n"
            f"                                        95% LOWER CONFIDENCE: {li_sk:>7.2f}\n"
            f"                                        95% UPPER CONFIDENCE: {ls_sk:>7.2f}"
        )
    else:
        ec50_str = "nan" if (ec50 is None or np.isnan(ec50)) else f"{ec50:>7.2f}"
        est_texto = (
            f"SPEARMAN-KARBER ESTIMATES:     {sigla}:          {ec50_str}\n"
            f"                                        95% CONFIDENCE LIMITS\n"
            f"                                        ARE NOT RELIABLE."
        )

    relatorio = f"""DATE:    {data}           TEST NUMBER: {num_teste:<11} DURATION:   {duracao} h
TOXICANT :   {num_teste}
SPECIES:   {especie}

RAW DATA:  Concentration         Number         Mortalities
--- ----   ({un})                 Exposed
{tabela_dados}

SPEARMAN-KARBER TRIM:               {trim_str:>5}

{est_texto}
--------------------------------------------------------------------------------"""
    
    return relatorio