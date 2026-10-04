import re
# Importe aqui as outras bibliotecas que seu projeto utiliza (ex: tkinter, openpyxl, etc.)


def limpar_texto(texto):
  """Função auxiliar para limpar e formatar os dados extraídos."""
  if not texto:
    return ""
  return str(texto).strip()


def processar_codigo_3(barcode):
  """Processa o 3º Código de Barras e extrai DUN/GTIN, Vencimento e Fabricação

  garantindo que o identificador '11' utilize a última ocorrência da string.
  """
  try:
    limpo = barcode.replace("(", "").replace(")", "")

    # Extração do DUN/GTIN (iniciado em 02)
    match_dun = re.search(r"(?:^|\D)02(\d{14})", limpo)
    if match_dun:
      dun = match_dun.group(1)
    else:
      match_dun_alt = re.search(r"02(\d+?)(?=17|11|$)", limpo)
      dun = match_dun_alt.group(1) if match_dun_alt else limpo[2:16]

    # Extração da Data de Validade/Vencimento (identificador 17)
    match_venc = re.search(r"17(\d{6})", limpo)
    vencimento = match_venc.group(1) if match_venc else ""

    # Extração da Data de Fabricação (identificador 11)
    # findall pega todas as ocorrências e pegamos a última ([-1]) para evitar falsos positivos
    matches_fab = re.findall(r"11(\d{6})", limpo)
    fabricacao = matches_fab[-1] if matches_fab else ""

    return limpar_texto(dun), limpar_texto(vencimento), limpar_texto(fabricacao)

  except Exception as e:
    print(f"Erro ao processar código de barras: {e}")
    return "", "", ""


# Exemplo de uso para testes:
if __name__ == "__main__":
  codigo_teste = "02778911501037631729090811260908"
  dun, vencimento, fabricacao = processar_codigo_3(codigo_teste)

  print(f"Código (DUN): {dun}")
  print(f"Vencimento (17): {vencimento}")
  print(f"Fabricação (11): {fabricacao}")
