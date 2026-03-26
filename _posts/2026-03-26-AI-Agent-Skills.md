---
title: "AI Agent Skill: scRNA-seq QC 전처리 자동화"
header:
  teaser: https://scanpy.readthedocs.io/en/stable/_static/Scanpy_Logo_BrightFG.svg
  og_image: https://scanpy.readthedocs.io/en/stable/_static/Scanpy_Logo_BrightFG.svg
date: 2026-03-26T21:00:00+09:00
categories:
  - AI
tags:
  - AI
  - Skill
  - Bioinformatics
  - scRNA-seq
  - Scanpy
  - LLM
---

# AI Agent Skill이란?

이전 포스트에서 MCP Server가 AI에게 외부 도구를 사용할 수 있는 **"손과 발"**을 달아준다고 했습니다. 그렇다면 **Skill**은 무엇일까요?

**Skill은 AI에게 도메인 전문 지식과 워크플로우를 알려주는 "매뉴얼"입니다.**

| 구분 | MCP Server | Skill |
|------|-----------|-------|
| 역할 | 실행 가능한 **도구** 제공 | 도구를 **어떻게 쓸지** 안내 |
| 비유 | 공구 세트 (망치, 드릴) | 가구 조립 설명서 |
| 형태 | JSON-RPC 함수 | 프롬프트 템플릿 + 스크립트 |
| 예시 | PubMed 검색 API | scRNA-seq QC 워크플로우 |

Skill은 프롬프트 기반의 재사용 가능한 워크플로우 템플릿으로, 특정 분야의 best practice를 AI에게 주입합니다. MCP Server가 "무엇을 할 수 있는가"를 정의한다면, Skill은 "무엇을 어떤 순서로 해야 하는가"를 정의합니다.

Anthropic은 **Life Sciences 마켓플레이스**를 통해 생명과학 분야의 Skill들을 제공하고 있습니다:
- Single-cell RNA-seq QC
- Nextflow 파이프라인 개발
- scvi-tools를 이용한 딥러닝 분석
- 임상시험 프로토콜 생성
- Allotrope 포맷 변환

이 중에서 **Single-cell RNA-seq QC** skill을 이용한 전처리 예시를 살펴보겠습니다.


# Single-cell RNA-seq QC Skill

Single-cell RNA-seq(scRNA-seq) 분석의 첫 번째 단계는 항상 **Quality Control(QC)**입니다. 죽은 세포, ambient RNA, doublet 등을 걸러내지 않으면 downstream 분석 결과를 신뢰할 수 없기 때문입니다.

이 Skill은 [**scverse**][1] 생태계의 best practice를 따르며, **Scanpy**를 기반으로 QC 워크플로우를 자동화합니다.


## QC metric

QC에서 확인하는 주요 지표는 다음과 같습니다:

| metric | 설명 | 정상 범위 |
|--------|------|-----------|
| **Total counts** | 세포당 총 UMI 수 | 500 ~ 50,000 |
| **Genes detected** | 발현된 유전자 수 | 200 ~ 5,000 |
| **MT%** | 미토콘드리아 유전자 비율 | < 5~8% |
| **Ribosomal%** | 리보솜 유전자 비율 | 조직별 상이 |
| **Hemoglobin%** | 헤모글로빈 유전자 비율 | ~0% (혈액 오염 지표) |

MT%가 높은 세포는 세포막이 손상되어 cytoplasmic mRNA가 유출되고 미토콘드리아 mRNA만 남은 상태일 가능성이 높습니다. 즉, 죽거나 죽어가는 세포입니다. (Skill 문서에서는 "high MT% = dying cells"로 요약하고 있으며, 위 설명은 일반적인 scRNA-seq 문헌 기반입니다.)


## MAD 기반 필터링

고정 threshold (예: "MT% > 20%이면 제거") 대신, 이 Skill은 **MAD (Median Absolute Deviation)** 기반 필터링을 사용합니다.

```
MAD = median(|X - median(X)|)
Outlier: X > median(X) + n_mads × MAD
```

MAD 방식의 장점은 프로토콜, 조직, 종(species)에 관계없이 **데이터 자체의 분포에 맞춰** outlier를 감지한다는 점입니다.

기본 threshold (scverse best practice):
- **Total counts**: 5 MADs (log-transformed) — 관대하게
- **Genes detected**: 5 MADs (log-transformed)
- **MT%**: 3 MADs — 죽은 세포에 대해서는 엄격하게
- **Hard cutoff**: MT% > 8% — 추가 안전장치


## 실행 예시

Skill이 제공하는 `qc_analysis.py` 스크립트로 한 줄만 실행하면 됩니다:

```bash
# .h5ad 파일 (AnnData 포맷)
python3 scripts/qc_analysis.py input.h5ad

# .h5 파일 (10X Genomics Cell Ranger 출력)
python3 scripts/qc_analysis.py raw_feature_bc_matrix.h5
```

파라미터를 조정할 수도 있습니다:

```bash
# 마우스 데이터, 뇌 조직 (높은 MT% 허용)
python3 scripts/qc_analysis.py brain_data.h5ad \
    --mt-pattern "^mt-" \
    --ribo-pattern "^Rpl|^Rps" \
    --hb-pattern "^Hb[^(p)]" \
    --mt-threshold 15 \
    --mad-mt 5
```

종별 미토콘드리아 유전자 패턴이 다릅니다:
- **Human**: `MT-` (대문자)
- **Mouse**: `mt-` (소문자)


## Workflow 단계

스크립트 실행 시 내부적으로 다음 과정이 진행됩니다:

```
1. 데이터 로드 (.h5ad / .h5 자동 감지)
       ↓
2. QC metric 계산 (scanpy.pp.calculate_qc_metrics)
       ↓
3. 필터링 전 시각화 생성
       ↓
4. MAD 기반 outlier 감지 (counts, genes, MT%)
       ↓
5. Hard MT% threshold 적용
       ↓
6. Threshold 시각화 (pass/fail 오버레이)
       ↓
7. 세포 및 유전자 필터링
       ↓
8. 필터링 후 시각화 생성
       ↓
9. 결과 저장
```


## 출력 파일

실행이 완료되면 `<basename>_qc_results/` 디렉토리에 다음 파일들이 생성됩니다:

| 파일 | 설명 |
|------|------|
| `qc_metrics_before_filtering.png` | 필터링 전 QC metric 분포 |
| `qc_filtering_thresholds.png` | MAD threshold 시각화 (pass/fail) |
| `qc_metrics_after_filtering.png` | 필터링 후 QC metric 분포 |
| `*_filtered.h5ad` | 필터링된 clean 데이터셋 |
| `*_with_qc.h5ad` | QC annotation이 추가된 원본 데이터 |


## 커스텀 워크플로우

스크립트 대신 모듈을 직접 import해서 세밀한 제어도 가능합니다:

```python
import anndata as ad
from qc_core import calculate_qc_metrics, detect_outliers_mad, apply_hard_threshold, filter_cells, filter_genes
from qc_plotting import plot_qc_distributions

# 데이터 로드
adata = ad.read_h5ad("pbmc_10k.h5ad")

# QC metric 계산
calculate_qc_metrics(adata, mt_pattern="^MT-", inplace=True)

# 필터링 전 시각화
plot_qc_distributions(adata, "before_qc.png", title="Before QC")

# MAD 기반 outlier 감지
outlier_counts = detect_outliers_mad(adata, "log1p_total_counts", n_mads=5)
outlier_genes = detect_outliers_mad(adata, "log1p_n_genes_by_counts", n_mads=5)
outlier_mt = detect_outliers_mad(adata, "pct_counts_mt", n_mads=3)

# Hard MT% threshold
high_mt = apply_hard_threshold(adata, "pct_counts_mt", threshold=8, operator=">")

# 필터링 적용
keep = ~(outlier_counts | outlier_genes | outlier_mt | high_mt)
adata_filtered = filter_cells(adata, keep)
filter_genes(adata_filtered, min_cells=20, inplace=True)

# 결과 확인
print(f"Before: {adata.n_obs} cells, {adata.n_vars} genes")
print(f"After:  {adata_filtered.n_obs} cells, {adata_filtered.n_vars} genes")

# 저장
adata_filtered.write_h5ad("pbmc_10k_filtered.h5ad")
```


## 조직별 파라미터 가이드

조직에 따라 적절한 threshold가 다릅니다:

| 조직 | MT% threshold | 참고 |
|------|---------------|------|
| **Blood (PBMC)** | 5~8% | 표준적인 threshold * |
| **Brain / Neuron** | 10~15% | 대사 활성이 높아 MT%가 자연적으로 높음 * |
| **Liver** | 10~15% | 미토콘드리아가 풍부한 조직 |
| **Muscle** | 10~20% | 에너지 소비가 많은 조직 |
| **Tumor** | 8~15% | 종양 미세환경에 따라 상이 |

> \* Blood, Brain은 Skill 문서에 나온 값이고, 나머지는 Skill에 없는 일반적인 참고치입니다. 조직마다 다를 수 있으니 선행 연구도 같이 확인하세요.


# 마무리

Skill의 핵심은 **도메인 전문 지식의 재사용**입니다. scRNA-seq QC의 best practice를 매번 논문에서 찾아볼 필요 없이, Skill 한 번 실행으로 scverse 커뮤니티의 권장 사항을 그대로 적용할 수 있습니다.

MCP Server가 AI의 **능력**을 확장한다면, Skill은 AI의 **판단력**을 확장합니다. 둘을 함께 사용하면, 개떡같은 데이터도 체계적으로 전처리할 수 있습니다.


Reference
---
- [https://www.sc-best-practices.org/preprocessing_visualization/quality_control.html](https://www.sc-best-practices.org/preprocessing_visualization/quality_control.html)
- [https://scanpy.readthedocs.io/en/stable/](https://scanpy.readthedocs.io/en/stable/)
- [https://github.com/anthropics/life-sciences](https://github.com/anthropics/life-sciences)
- [https://scverse.org/](https://scverse.org/)
- [https://www.anthropic.com/news/claude-for-life-sciences](https://www.anthropic.com/news/claude-for-life-sciences)


[1]:https://scverse.org/
