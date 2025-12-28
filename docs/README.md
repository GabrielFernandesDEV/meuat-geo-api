# Relatório Técnico – Ganhos com uso de Índice GiST em Geography

## 📋 Índice

1. [Contexto da Análise](#contexto-da-análise)
2. [Índice Avaliado](#índice-avaliado)
3. [Cenário com Índice GiST em Geography](#cenário-com-índice-gist-em-geography)
4. [Cenário sem Índice GiST em Geography](#cenário-sem-índice-gist-em-geography)
5. [Comparativo Objetivo](#comparativo-objetivo)
6. [Conclusão](#conclusão)
7. [Recomendações de Manutenção](#recomendações-de-manutenção)

---

## 🎯 Contexto da Análise

A API realiza consultas espaciais do tipo **busca por raio**, utilizando a função:

```sql
ST_DWithin(geom::geography, <ponto>, <raio>)
```

Esse tipo de operação é computacionalmente custoso quando executado sem suporte de índice espacial adequado, especialmente em tabelas com grande volume de geometrias.

### Implementação na API

A funcionalidade está implementada no método `get_by_radius` do `GeoRepositoryMixin`:

```108:114:app/repositories/geo_repository_mixin.py
        query = db.query(self.model).filter(
            func.ST_DWithin(
                geom_field,
                ponto,
                radius_meters,
                True  # use_spheroid=True
            )
        )
```

---

## 🔍 Índice Avaliado

```sql
CREATE INDEX idx_fazendas_geom_geog
ON public.fazendas
USING GIST ((geom::geography));
```

**Características:**
- Tipo: **GiST (Generalized Search Tree)**
- Campo indexado: `geom::geography` (conversão de geometry para geography)
- Uso: Otimização de consultas espaciais baseadas em distância

---

## ✅ Cenário com Índice GiST em Geography

### Principais Características Observadas

- **Plano de execução:** `Index Scan using idx_fazendas_geom_geog`
- **Tipo de acesso:** Acesso direto ao índice espacial
- **Filtros aplicados:**
  - `Index Cond: (geom::geography && _st_expand(...))`
  - `Filter: st_dwithin(...)`

### Ganhos Observados

| Métrica | Valor |
|---------|-------|
| **Tempo de execução** | ~850 ms |
| **Tipo de Scan** | Index Scan |
| **Leitura** | Majoritariamente em memória (shared hit) |
| **Linhas filtradas** | Significativamente menor (~14 mil) |
| **Seq Scan** | Nenhum |
| **Tempo de planejamento** | ~0.1 ms |

### Interpretação Técnica

O índice GiST permite que o PostgreSQL:

1. **Limite o universo de comparação espacial** usando bounding boxes
2. **Avalie o ST_DWithin apenas em candidatos espaciais relevantes**
3. **Evite cálculos de distância desnecessários**
4. **Explore eficientemente cache de buffer** (shared hit)

**Evidência visual:** Ver `docs/print/geography_index.png` e `docs/print/geopraghy_index _db_explain.png`

---

## ❌ Cenário sem Índice GiST em Geography

### Principais Características Observadas

- **Plano de execução:** `Parallel Seq Scan on fazendas`
- **Tipo de acesso:** Varredura completa da tabela
- **Filtro aplicado após leitura completa:**
  - `Filter: st_dwithin(geom::geography, ...)`

### Impactos Negativos Observados

| Métrica | Valor |
|---------|-------|
| **Tempo de execução** | ~4.8 a 7.1 segundos |
| **Tipo de Scan** | Parallel Seq Scan |
| **Leitura** | Massiva de blocos em disco (read) |
| **Registros avaliados** | Mais de 148 mil |
| **Uso de paralelismo** | Apenas para mitigar custo |
| **Custo estimado** | ≈ 4.8 milhões |

### Interpretação Técnica

Sem o índice:

1. O PostgreSQL é **obrigado a testar cada geometria da tabela**
2. O custo **cresce linearmente com o volume de dados**
3. O uso de paralelismo apenas **reduz parcialmente o impacto**
4. Há **pressão significativa sobre I/O de disco e CPU**

**Evidência visual:** Ver `docs/print/no_geography_index.png` e `docs/print/no_geopraghy_index _db_explain.png`

---

## 📊 Comparativo Objetivo

| Métrica | Sem Índice | Com Índice GiST Geography | Ganho |
|---------|------------|---------------------------|-------|
| **Tipo de Scan** | Parallel Seq Scan | Index Scan | ✅ Eliminação de varredura completa |
| **Tempo de execução** | ~5–7 segundos | ~0.85 segundos | **~6x a 8x mais rápido** |
| **Linhas analisadas** | ~148 mil | ~14 mil | **~10x menos linhas** |
| **Uso de disco** | Alto (read) | Baixo (shared hit) | ✅ Leitura majoritariamente em memória |
| **Escalabilidade** | Ruim | Alta | ✅ Suporta crescimento de dados |
| **Impacto em API** | Alto (latência elevada) | Baixo (resposta rápida) | ✅ Experiência do usuário melhorada |
| **Custo estimado** | ≈ 4.8 milhões | Significativamente menor | ✅ Redução drástica |

---

## 🎯 Conclusão

A criação do índice:

```sql
CREATE INDEX idx_fazendas_geom_geog
ON public.fazendas
USING GIST ((geom::geography));
```

gera **ganhos expressivos e diretos** para operações espaciais baseadas em distância, destacando-se:

✅ **Redução de tempo de resposta da API em ordem de magnitude** (de segundos para milissegundos)  
✅ **Eliminação de varreduras completas da tabela**  
✅ **Melhor aproveitamento de cache e memória**  
✅ **Maior previsibilidade de desempenho**  
✅ **Base sólida para crescimento do volume de dados** sem degradação significativa  

> **Em cenários de busca por raio, o uso de índice GiST em geography não é apenas recomendado, mas essencial para garantir desempenho aceitável em produção.**

---

## 🔧 Recomendações de Manutenção

### 1. Criação do Índice

Execute o seguinte comando SQL após a criação da tabela:

```sql
CREATE INDEX idx_fazendas_geom_geog
ON public.fazendas
USING GIST ((geom::geography));
```

### 2. Análise de Estatísticas

Após inserções ou atualizações significativas, execute:

```sql
ANALYZE fazendas;
```

Isso atualiza as estatísticas do planner do PostgreSQL, permitindo que ele escolha o melhor plano de execução.

### 3. Reindexação Periódica

Em ambientes com muitas atualizações, considere reindexar periodicamente:

```sql
REINDEX INDEX CONCURRENTLY idx_fazendas_geom_geog;
```

O `CONCURRENTLY` permite que a reindexação ocorra sem bloquear operações de escrita.

### 4. Vacuum

Execute VACUUM regularmente para manter a saúde do banco:

```sql
VACUUM ANALYZE fazendas;
```

### 5. Monitoramento

Monitore o uso do índice através de:

```sql
-- Verificar tamanho do índice
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE indexname = 'idx_fazendas_geom_geog';

-- Verificar estatísticas de uso
SELECT 
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE indexname = 'idx_fazendas_geom_geog';
```

### 6. Script de Manutenção Automatizada

Considere criar um script de manutenção periódica (ex: via cron job):

```sql
-- Script de manutenção semanal
VACUUM ANALYZE fazendas;
REINDEX INDEX CONCURRENTLY idx_fazendas_geom_geog;
```

---

## 📚 Referências

- [PostgreSQL GiST Indexes](https://www.postgresql.org/docs/current/gist.html)
- [PostGIS Spatial Indexing](https://postgis.net/docs/using_postgis_dbmanagement.html#spatial_indexes)
- [ST_DWithin Documentation](https://postgis.net/docs/ST_DWithin.html)

---

**Última atualização:** Dezembro 2024

