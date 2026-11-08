"""Lê os 5 bancos do Notion e grava data/dados.json para o painel.

Roda no GitHub Actions a cada 30 min (ver .github/workflows/sync.yml).
Localmente:  NOTION_TOKEN=secret_xxx python scripts/sync_notion.py
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TOKEN = os.environ.get("NOTION_TOKEN")
API = "https://api.notion.com/v1"
VERSAO = "2022-06-28"

BANCOS = {
    "demandas": "17be4eb5e6f541929c80e9d63e792eba",
    "frentes":  "5557d8ebae7e44198b4bed2ce922ae90",
    "scripts":  "e679d5b9e8744b539e0d09c7feacca6a",
    "assets":   "d3c0868f2c5744e2b681b4af8f10ad16",
    "dados":    "d3999b2351da41229759b0447b49606d",
}
PAGINA_NOTION = "https://www.notion.so/4117219ef930815dac67eb445b03dce4"
SAIDA = Path(__file__).resolve().parent.parent / "data" / "dados.json"


def consultar(db_id):
    linhas, cursor = [], None
    while True:
        corpo = {"page_size": 100}
        if cursor:
            corpo["start_cursor"] = cursor
        req = urllib.request.Request(
            f"{API}/databases/{db_id}/query", data=json.dumps(corpo).encode(), method="POST",
            headers={"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSAO,
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.load(r)
        linhas += res["results"]
        if not res.get("has_more"):
            return linhas
        cursor = res["next_cursor"]


def texto(partes):
    return "".join(p.get("plain_text", "") for p in partes or [])


def valor(p):
    """Converte uma propriedade do Notion num valor simples."""
    t = p["type"]
    v = p.get(t)
    if t in ("title", "rich_text"):
        return texto(v)
    if t in ("select", "status"):
        return v["name"] if v else None
    if t == "multi_select":
        return [o["name"] for o in v]
    if t == "date":
        return v["start"] if v else None
    if t in ("number", "url", "checkbox", "email", "created_time", "last_edited_time"):
        return v
    if t == "people":
        return [u.get("name") or "" for u in v]
    if t == "relation":
        return [r["id"].replace("-", "") for r in v]
    if t == "unique_id":
        return f"{v['prefix']}-{v['number']}" if v and v.get("prefix") else (v or {}).get("number")
    return None


def linha(pg, mapa):
    props = pg["properties"]
    out = {"id": pg["id"].replace("-", ""), "url": pg["url"]}
    for chave, nome in mapa.items():
        out[chave] = valor(props[nome]) if nome in props else None
    return out


MAPAS = {
    "demandas": {"doc": "Documentação", "titulo": "Demanda", "codigo": "ID", "status": "Status", "prioridade": "Prioridade",
                 "inicio": "Início", "prazo": "Prazo", "avanco": "Avanço (%)", "responsavel": "Responsável",
                 "solicitante": "Solicitante", "frentes": "Frente", "scripts": "Scripts",
                 "entregavel": "Entregável", "notas": "Notas", "editado": "Editado em"},
    "frentes": {"doc": "Documentação", "nome": "Frente", "teamspace": "Teamspace", "descricao": "Descrição",
                "colaboradores": "Colaboradores", "ativa": "Ativa"},
    "scripts": {"doc": "Documentação", "nome": "Script", "tipo": "Tipo", "status": "Status", "versao": "Versão",
                "descricao": "Descrição", "frentes": "Frente", "assets": "Assets usados",
                "le": "Lê dados", "gera": "Gera dados", "arquivo": "Arquivo no projeto", "link": "Link"},
    "assets": {"doc": "Documentação", "nome": "Asset", "path": "Path", "origem": "Origem", "tema": "Tema",
               "versao": "Coleção/versão", "notas": "Notas"},
    "dados": {"doc": "Documentação", "nome": "Arquivo", "formato": "Formato", "pasta": "Pasta Drive",
              "unidades": "Unidade espacial", "periodo": "Período", "link": "Link", "notas": "Notas"},
}


def main():
    if not TOKEN:
        sys.exit("Defina NOTION_TOKEN (segredo do repositório no GitHub).")
    dados = {"atualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "notion": PAGINA_NOTION}
    for nome, db in BANCOS.items():
        dados[nome] = [linha(p, MAPAS[nome]) for p in consultar(db)]
        print(f"{nome}: {len(dados[nome])} linhas")

    # Só regrava se algo além do horário mudou, para não gerar commit a cada 30 min
    if SAIDA.exists():
        antigo = json.loads(SAIDA.read_text(encoding="utf-8"))
        if {k: v for k, v in antigo.items() if k != "atualizado"} == \
           {k: v for k, v in dados.items() if k != "atualizado"}:
            print("Sem mudanças no Notion.")
            return
    SAIDA.parent.mkdir(exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Gravado {SAIDA}")


if __name__ == "__main__":
    main()
