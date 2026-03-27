---
title: "CELLxGENE Census: 5천만 세포 데이터를 API로 조회하기"
header:
  teaser: /assets/images/cellxgene-teaser.svg
  og_image: /assets/images/orange.jpg
date: 2026-03-27T12:00:00+09:00
categories:
  - AI
tags:
  - Bioinformatics
  - scRNA-seq
  - CELLxGENE
  - API
  - Single Cell
---

# CELLxGENE Census란?

**CELLxGENE Census**는 Chan Zuckerberg Initiative(CZI)에서 제공하는 단일세포 데이터 플랫폼입니다. 전 세계 연구자들이 공개한 **5천만 개 이상의 세포** 데이터를 하나의 Python SDK로 쿼리할 수 있습니다.

일반적으로 scRNA-seq 데이터를 얻으려면 GEO에서 데이터셋을 찾고, 다운로드하고, 포맷을 맞추고, 통합해야 합니다. Census는 이 과정을 **한 줄의 쿼리**로 대체합니다.

> 공식 문서: [https://chanzuckerberg.github.io/cellxgene-census/](https://chanzuckerberg.github.io/cellxgene-census/)


# 뭘 조회할 수 있나

Census의 핵심은 **조건부 슬라이싱**입니다:

| 필터 | 예시 |
|------|------|
| **cell_type** | T cell, B cell, macrophage, hepatocyte, neuron |
| **tissue** | lung, liver, brain, blood, kidney |
| **disease** | normal, lung adenocarcinoma, glioblastoma |
| **sex** | male, female |
| **organism** | Homo sapiens, Mus musculus |

이 필터들을 조합하면 매우 구체적인 쿼리가 가능합니다:
- "인간 폐의 T cell에서 CD3E 발현"
- "간암 vs 정상 간의 macrophage 비교"
- "삼중음성 유방암의 B cell 유전자 발현 패턴"


# 암종 데이터

Census에는 다양한 암종 데이터가 포함되어 있습니다. CELLxGENE API로 실제 확인한 데이터 규모:

| 암종 | 데이터셋 수 | 세포 수 |
|------|:---:|---:|
| **Lung adenocarcinoma** | 12 | 4,939,955 |
| **Squamous cell lung carcinoma** | 4 | 4,494,669 |
| **Glioblastoma** | 6 | 1,830,729 |
| **B-cell non-Hodgkin lymphoma** | 6 | 1,590,877 |
| **Malignant ovarian serous tumor** | 5 | 1,549,547 |
| **Breast cancer** | 34 | 1,308,712 |
| **Melanoma** | 2 | 747,904 |
| **Renal cell carcinoma** | 20 | 745,504 |
| **Neuroblastoma** | 3 | 592,116 |
| **Basal cell carcinoma** | 11 | 557,907 |
| **Triple-negative breast carcinoma** | 16 | 544,075 |

폐선암만 해도 **490만 세포**, 유방암 전체는 **130만 세포** 규모입니다.


# 설치 및 기본 사용법

## 설치

```bash
pip install cellxgene-census
```

> **Windows에서는 tiledbsoma 빌드가 안 됩니다.** Linux/macOS를 사용하거나 WSL, Docker, Google Colab에서 실행하세요. Colab이 가장 간편합니다.


## 기본 구조

```python
import cellxgene_census

with cellxgene_census.open_soma() as census:
    # census['census_data']['homo_sapiens']  → 인간 데이터
    # census['census_data']['mus_musculus']  → 마우스 데이터

    adata = cellxgene_census.get_anndata(
        census,
        organism="Homo sapiens",
        obs_value_filter="...",   # 세포 필터
        var_value_filter="...",   # 유전자 필터
    )
```

`get_anndata()`가 핵심 함수입니다. 조건에 맞는 세포만 AnnData 객체로 반환합니다.


# 실습 예시

## 1) 정상 폐 T cell의 marker 유전자 발현

```python
import cellxgene_census

with cellxgene_census.open_soma() as census:
    adata = cellxgene_census.get_anndata(
        census,
        organism="Homo sapiens",
        obs_value_filter=(
            "tissue_general == 'lung' "
            "and cell_type == 'T cell' "
            "and disease == 'normal'"
        ),
        var_value_filter="feature_name in ['CD3E', 'CD4', 'CD8A', 'FOXP3', 'IL2RA']",
    )

    print(f"세포 수: {adata.n_obs}")
    print(f"유전자: {list(adata.var['feature_name'])}")
    print(f"평균 발현:\n{adata.to_df().mean()}")
```


## 2) 폐선암 vs 정상 폐 — Macrophage 비교

```python
import cellxgene_census

with cellxgene_census.open_soma() as census:
    # 폐선암 macrophage
    tumor = cellxgene_census.get_anndata(
        census,
        organism="Homo sapiens",
        obs_value_filter=(
            "tissue_general == 'lung' "
            "and cell_type == 'macrophage' "
            "and disease == 'lung adenocarcinoma'"
        ),
        var_value_filter="feature_name in ['CD68', 'CD163', 'MRC1', 'CD274', 'TGFB1']",
    )

    # 정상 폐 macrophage
    normal = cellxgene_census.get_anndata(
        census,
        organism="Homo sapiens",
        obs_value_filter=(
            "tissue_general == 'lung' "
            "and cell_type == 'macrophage' "
            "and disease == 'normal'"
        ),
        var_value_filter="feature_name in ['CD68', 'CD163', 'MRC1', 'CD274', 'TGFB1']",
    )

    print(f"Tumor macrophages: {tumor.n_obs} cells")
    print(f"Normal macrophages: {normal.n_obs} cells")
    print(f"\n--- Mean expression ---")
    print(f"Tumor:\n{tumor.to_df().mean()}")
    print(f"\nNormal:\n{normal.to_df().mean()}")
```

CD274(PD-L1)가 종양 macrophage에서 더 높게 나온다면, 면역 회피 기전과 일치하는 결과입니다.


## 3) 폐선암 세포 유형 구성 (실제 실행 결과)

발현 데이터 없이 **메타데이터만 조회**할 때는 `get_obs()`를 사용합니다. 훨씬 가볍고 빠릅니다.

```python
import cellxgene_census

with cellxgene_census.open_soma(census_version="2025-11-08") as census:
    obs_df = cellxgene_census.get_obs(
        census,
        organism="Homo sapiens",
        value_filter="tissue_general == 'lung' and disease == 'lung adenocarcinoma'",
        column_names=["cell_type", "disease", "tissue"],
    )

    print(f"총 세포 수: {len(obs_df)}")
    print(obs_df['cell_type'].value_counts().head(15))
```

아래는 WSL Ubuntu 환경에서 실제 실행한 결과입니다:

```
=== Lung Adenocarcinoma Cell Composition ===
Total cells: 1,190,858

cell_type
CD4-positive, alpha-beta T cell         166,387
CD8-positive, alpha-beta T cell         147,701
alveolar macrophage                     102,988
macrophage                               84,820
T cell                                   82,143
natural killer cell                      63,985
B cell                                   62,351
malignant cell                           56,502
classical monocyte                       43,371
epithelial cell of lung                  33,765
regulatory T cell                        31,818
epithelial cell                          29,519
CD1c-positive myeloid dendritic cell     28,159
plasma cell                              26,996
pulmonary alveolar type 2 cell           22,679
```

**119만 세포**에서 세포 유형별 구성을 확인할 수 있습니다. CD4+ T cell과 CD8+ T cell이 가장 많고, macrophage(alveolar + general)가 약 18만으로 종양 미세환경에서 큰 비중을 차지합니다.


## 4) Glioblastoma — 종양 미세환경 유전자 발현

```python
import cellxgene_census

with cellxgene_census.open_soma() as census:
    adata = cellxgene_census.get_anndata(
        census,
        organism="Homo sapiens",
        obs_value_filter=(
            "disease == 'glioblastoma' "
            "and cell_type in ['T cell', 'macrophage', 'microglial cell']"
        ),
        var_value_filter=(
            "feature_name in ['PDCD1', 'CD274', 'CTLA4', 'HAVCR2', "
            "'LAG3', 'TIGIT', 'CD68', 'TMEM119']"
        ),
    )

    print(f"세포 수: {adata.n_obs}")

    # 세포 유형별 평균 발현
    import pandas as pd
    expr = adata.to_df()
    expr['cell_type'] = adata.obs['cell_type'].values
    print(expr.groupby('cell_type').mean())
```

GBM의 면역 checkpoint 발현 패턴을 T cell, macrophage, microglia 별로 비교할 수 있습니다.


# MCP Tool로 만들기

이전 AlphaGenome 포스트와 마찬가지로, Census SDK를 MCP Tool로 감싸면 자연어로 쿼리할 수 있습니다.

```python
# cellxgene_mcp.py
from mcp.server.fastmcp import FastMCP
import cellxgene_census

mcp = FastMCP("cellxgene")

@mcp.tool()
def query_expression(
    tissue: str,
    cell_type: str,
    genes: list[str],
    disease: str = "normal",
    organism: str = "Homo sapiens",
) -> dict:
    """특정 조직/세포 유형의 유전자 발현을 조회합니다."""

    gene_filter = ", ".join([f"'{g}'" for g in genes])

    with cellxgene_census.open_soma() as census:
        adata = cellxgene_census.get_anndata(
            census,
            organism=organism,
            obs_value_filter=(
                f"tissue_general == '{tissue}' "
                f"and cell_type == '{cell_type}' "
                f"and disease == '{disease}'"
            ),
            var_value_filter=f"feature_name in [{gene_filter}]",
        )

    expr_mean = adata.to_df().mean().to_dict()

    return {
        "tissue": tissue,
        "cell_type": cell_type,
        "disease": disease,
        "n_cells": adata.n_obs,
        "genes": {g: round(v, 4) for g, v in expr_mean.items()},
    }


@mcp.tool()
def query_cell_composition(
    disease: str,
    organism: str = "Homo sapiens",
) -> dict:
    """특정 질병의 세포 유형 구성을 조회합니다."""

    with cellxgene_census.open_soma() as census:
        obs_df = cellxgene_census.get_obs(
            census,
            organism=organism,
            value_filter=f"disease == '{disease}'",
            column_names=["cell_type"],
        )

    counts = obs_df['cell_type'].value_counts().head(10).to_dict()

    return {
        "disease": disease,
        "total_cells": len(obs_df),
        "top_cell_types": counts,
    }

if __name__ == "__main__":
    mcp.run()
```


## 사용 예시

```
사용자: "폐선암의 T cell과 macrophage에서 PD-L1(CD274) 발현을 비교해줘"

Claude: cellxgene query_expression 도구를 2번 호출하겠습니다.

1) T cell, lung, lung adenocarcinoma, CD274
   → 12,847 cells, CD274 평균 발현: 0.0312

2) macrophage, lung, lung adenocarcinoma, CD274
   → 8,234 cells, CD274 평균 발현: 0.1847

macrophage에서 PD-L1 발현이 T cell 대비 약 6배 높습니다.
종양 미세환경에서 macrophage가 PD-L1을 통한 면역 억제에
주요 역할을 하고 있음을 시사합니다.
```

> 위 수치는 형식 예시입니다. 실제 값은 Census 쿼리 결과에 따라 달라집니다.


# AlphaGenome과 조합하기

Census와 AlphaGenome을 함께 쓰면 더 강력합니다:

```
1. CELLxGENE Census로 특정 암종의 DEG(차등발현유전자) 확인
2. DEG 중 regulatory variant가 있는 유전자 선별
3. AlphaGenome으로 해당 variant의 기능적 영향 예측
```

예: "GBM에서 과발현되는 유전자 중 known variant의 splicing 영향 분석"

논문 한 편 분량의 분석을 MCP Tool 몇 번 호출로 수행할 수 있습니다.


# 제한사항

| 항목 | 내용 |
|------|------|
| **설치** | Linux/macOS 권장, Windows는 WSL 필요 |
| **데이터 크기** | 전체 다운로드 시 수백 GB, 쿼리 기반 접근 권장 |
| **업데이트** | Census는 주기적으로 스냅샷 업데이트 (최신 데이터셋 반영에 지연) |
| **정규화** | raw count 기반, 정규화는 사용자가 직접 수행 |
| **비용** | 무료 |


# 마무리

CELLxGENE Census는 scRNA-seq 분야에서 유일하게 **API로 접근 가능한 대규모 데이터 플랫폼**입니다. GEO에서 데이터셋을 하나씩 다운로드하던 시대와 비교하면, "폐선암 macrophage의 PD-L1 발현"을 코드 한 줄로 조회할 수 있다는 건 엄청난 변화입니다.

여기에 MCP Tool로 감싸면 자연어로 쿼리하고, AlphaGenome과 조합하면 변이 기능 예측까지 이어지는 파이프라인을 구성할 수 있습니다.


Reference
---
- [https://chanzuckerberg.github.io/cellxgene-census/](https://chanzuckerberg.github.io/cellxgene-census/)
- [https://cellxgene.cziscience.com/](https://cellxgene.cziscience.com/)
- [https://github.com/chanzuckerberg/cellxgene-census](https://github.com/chanzuckerberg/cellxgene-census)
