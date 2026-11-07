# Painel de demandas · MapBiomas Água e Risco Climático

Site estático (GitHub Pages) que mostra as demandas, scripts/Colabs, assets GEE e planilhas
cadastrados no Notion (teamspace GeoKarten → *MapBiomas Água & Risco Climático — Gestão*).

- **Editar** é sempre no Notion. O site só lê.
- O GitHub Actions roda `scripts/sync_notion.py` a cada 30 min e grava `data/dados.json`.
  Só gera commit quando algo mudou no Notion.

## Configuração (uma vez)

1. **Integração do Notion**: em https://www.notion.so/profile/integrations → *New integration*
   (tipo *Internal*, só leitura: marque *Read content*). Copie o *Internal Integration Secret*.
2. **Dar acesso à página**: no Notion, abra *MapBiomas Água & Risco Climático — Gestão* →
   `•••` → *Connections* → adicione a integração. Os 5 bancos herdam o acesso.
3. **Segredo no GitHub**: *Settings → Secrets and variables → Actions → New repository secret*,
   nome `NOTION_TOKEN`, valor = o secret do passo 1.
4. **Pages**: *Settings → Pages → Source: Deploy from a branch → `main` / `(root)`*.
5. **Primeira sincronização**: aba *Actions → Sincronizar Notion → Run workflow*.

O site fica em `https://pedrogalve00.github.io/painel-demandas-mapbiomas/`.

## Bancos do Notion

| Banco | Para quê |
|---|---|
| Demandas | O que fazer: status, prioridade, início, prazo, % de avanço, frente, scripts |
| Frentes | Linhas de trabalho e o teamspace (Água / Risco Climático) |
| Scripts & Colabs | Cada `.js`/`.ipynb`: assets que usa, planilhas que lê e que gera |
| Assets GEE | Caminho, origem, tema, versão e cuidados de cada asset |
| Planilhas & Dados | CSVs/XLSX/assets de saída: pasta no Drive, recorte e período |

Se renomear uma propriedade no Notion, ajuste `MAPAS` em `scripts/sync_notion.py`.
