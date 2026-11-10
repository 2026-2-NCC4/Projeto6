"""Gera somente médias anuais de caixa autorizadas, a partir da base E2 local."""
import json
from pathlib import Path
from src.cti import agregados as ag
from src.cti.analises_gerenciais import ARQUIVO_PONTE, medias_adicionais


def main():
    base_path = Path("src/data/processed/e2/base_analitica.parquet")
    qualidade = json.loads(Path("src/data/processed/e2/qualidade.json").read_text(encoding="utf-8"))
    agregados = ag.ler()
    if (ag.sha256(base_path) != agregados["origem"]["sha256_base"] or
            qualidade.get("entrada_sha256") != agregados["origem"].get("entrada_sha256") or
            qualidade.get("corresponde_referencia_E1") is not True):
        raise ValueError("A base local não corresponde à origem dos agregados publicados.")
    import pandas as pd
    ponte = medias_adicionais(pd.read_parquet(base_path), agregados)
    ARQUIVO_PONTE.write_text(json.dumps(ponte, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print("Médias autorizadas da ponte geradas e reconciliadas para 12 anos e duas populações.")


if __name__ == "__main__":
    main()
