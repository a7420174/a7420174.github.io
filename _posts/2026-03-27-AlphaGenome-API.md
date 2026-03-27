---
title: "AlphaGenome API로 변이 효과 예측하기"
header:
  teaser: /assets/images/alphagenome-teaser.svg
  og_image: /assets/images/orange.jpg
date: 2026-03-27T09:00:00+09:00
categories:
  - AI
tags:
  - AI
  - AlphaGenome
  - DeepMind
  - Variant
  - Genomics
---

# AlphaGenome이란?

**AlphaGenome**은 Google DeepMind가 개발한 DNA regulatory code 해석 모델입니다. 최대 **100만 bp** 길이의 DNA 서열을 입력받아 유전자 발현, 스플라이싱, 크로마틴 구조 등 **11가지 modality**를 단일 염기 해상도로 예측합니다.

쉽게 말하면, 특정 변이가 유전자에 어떤 영향을 미치는지 AI로 예측해주는 도구입니다.

> Avsec et al. "Advancing regulatory variant effect prediction with AlphaGenome" *Nature* 649, 1206–1218 (2026). [DOI: 10.1038/s41586-025-10014-0](https://doi.org/10.1038/s41586-025-10014-0)


# 예측 가능한 Output

AlphaGenome은 하나의 모델에서 11가지 output을 예측합니다:

| Output | 설명 |
|--------|------|
| **RNA_SEQ** | 유전자 발현 |
| **SPLICE_SITES** | 스플라이스 사이트 분류 |
| **SPLICE_SITE_USAGE** | 상대적 스플라이스 사이트 사용량 |
| **SPLICE_JUNCTIONS** | 스플라이스 정션 예측 |
| **DNASE** | 크로마틴 접근성 (DNase-seq) |
| **ATAC** | 크로마틴 접근성 (ATAC-seq) |
| **CAGE** | 프로모터 활성 |
| **CHIP_HISTONE** | 히스톤 변형 |
| **CHIP_TF** | 전사인자 결합 |
| **CONTACT_MAPS** | 3D 크로마틴 접촉 지도 |
| **PROCAP** | 초기 전사 활성 (PRO-cap) |


# API 설정

## API Key 발급

1. [https://deepmind.google.com/science/alphagenome](https://deepmind.google.com/science/alphagenome) 접속
2. Google 계정으로 로그인
3. API key 발급 (무료, 비상업용)

## 설치

```bash
pip install -U alphagenome
```

Python 3.10 이상 필요 (3.11 권장).

## 클라이언트 초기화

```python
from alphagenome.models import dna_client

model = dna_client.create('YOUR_API_KEY')
```

Colab에서는 Secrets에 `ALPHA_GENOME_API_KEY`를 저장한 뒤:

```python
from alphagenome import colab_utils
model = dna_client.create(colab_utils.get_api_key())
```


# 변이 효과 예측 실습

## 기본 구조

AlphaGenome의 변이 예측은 **reference 서열과 alternate 서열을 비교**하는 방식입니다.

```python
from alphagenome.data import genome
from alphagenome.models import dna_client

model = dna_client.create('YOUR_API_KEY')

# 변이 정의 (1-based, VCF 형식)
variant = genome.Variant(
    chromosome='chr22',
    position=36201698,
    reference_bases='A',
    alternate_bases='C',
)

# 분석 구간 설정 (변이를 중심으로 1MB)
interval = variant.reference_interval.resize(dna_client.SEQUENCE_LENGTH_1MB)

# 예측 실행
outputs = model.predict_variant(
    interval=interval,
    variant=variant,
    ontology_terms=['UBERON:0001157'],  # 조직 ontology
    requested_outputs=[dna_client.OutputType.RNA_SEQ],
)

# 결과: reference vs alternate 비교
ref_output = outputs.reference.rna_seq  # REF 서열 예측
alt_output = outputs.alternate.rna_seq  # ALT 서열 예측
```


## 임상 변이 예시: BRCA2 스플라이싱 변이

유방암/난소암 관련 유전자 BRCA2의 스플라이싱 변이를 예측합니다:

```python
from alphagenome.models import variant_scorers

# BRCA2 스플라이싱 변이
variant = genome.Variant(
    chromosome='chr13',
    position=32316462,
    reference_bases='T',
    alternate_bases='G',
)

# 스플라이싱 관련 scorer 3종
splicing_scorers = [
    variant_scorers.RECOMMENDED_VARIANT_SCORERS['SPLICE_SITES'],
    variant_scorers.RECOMMENDED_VARIANT_SCORERS['SPLICE_SITE_USAGE'],
    variant_scorers.RECOMMENDED_VARIANT_SCORERS['SPLICE_JUNCTIONS'],
]

interval = variant.reference_interval.resize(dna_client.SEQUENCE_LENGTH_1MB)

# 스코어링 실행
scores = model.score_variant(
    interval=interval,
    variant=variant,
    variant_scorers=splicing_scorers,
    organism=dna_client.Organism.HOMO_SAPIENS,
)
```

> 스플라이싱 통합 점수가 **1.0 이상**이면 유의미한 스플라이싱 영향이 있다고 판단합니다.


## 배치 변이 스코어링

여러 변이를 한 번에 11가지 modality로 스코어링할 수 있습니다:

```python
from alphagenome.models import variant_scorers

# 권장 scorer 11종 전체 사용
all_scorers = variant_scorers.RECOMMENDED_VARIANT_SCORERS

variant = genome.Variant(
    chromosome='chr3',
    position=58394738,
    reference_bases='A',
    alternate_bases='T',
)
interval = variant.reference_interval.resize(dna_client.SEQUENCE_LENGTH_1MB)

# 전체 modality 스코어링
variant_scores = model.score_variant(
    interval=interval,
    variant=variant,
    variant_scorers=list(all_scorers.values()),
    organism=dna_client.Organism.HOMO_SAPIENS,
)

# DataFrame으로 정리
df = variant_scorers.tidy_scores([variant_scores])
```

반환되는 DataFrame 컬럼:

| 컬럼 | 설명 |
|------|------|
| `gene_name` | 영향받는 유전자 |
| `output_type` | 예측 modality (RNA_SEQ, DNASE 등) |
| `variant_scorer` | 사용된 scorer 종류 |
| `raw_score` | 원시 점수 |
| `quantile_score` | 분위수 점수 (0~1) |


## 시각화

```python
from alphagenome.visualization import plot_components
import matplotlib.pyplot as plt

plot_components.plot(
    [
        plot_components.OverlaidTracks(
            tdata={
                'REF': outputs.reference.rna_seq,
                'ALT': outputs.alternate.rna_seq,
            },
            colors={'REF': 'dimgrey', 'ALT': 'red'},
        ),
    ],
    interval=outputs.reference.rna_seq.interval.resize(2**15),
    annotations=[plot_components.VariantAnnotation([variant], alpha=0.8)],
)
plt.show()
```

REF(회색)와 ALT(빨간색) 트랙을 겹쳐서 변이가 유전자 발현에 미치는 영향을 시각적으로 확인할 수 있습니다.


# 지원 범위와 제한사항

| 항목 | 내용 |
|------|------|
| **지원 종** | Human (hg38), Mouse (mm10) |
| **서열 길이** | 16KB, 100KB, 500KB, 1MB (4가지) |
| **변이 유형** | SNV, insertion, deletion |
| **비용** | 무료 (비상업용) |
| **상업용** | 별도 신청 필요 ([신청 페이지](https://deepmind.google.com/science/alphagenome)) |
| **Rate limit** | 수천 건 수준 적합, 100만 건 이상은 부적합 |


# 공식 리소스

- **Colab 노트북 8개** 제공 ([GitHub](https://github.com/google-deepmind/alphagenome/tree/main/colabs/)):
  - `quick_start.ipynb` — 첫 예측
  - `batch_variant_scoring.ipynb` — 배치 스코어링
  - `splicing_variant_scoring.ipynb` — 스플라이싱 분석 (BRCA1, BRCA2, CFTR)
  - `example_analysis_workflow.ipynb` — TAL1 종양유전자 분석
  - `visualization_modality_tour.ipynb` — 11가지 modality 시각화
- **YouTube**: [AlphaGenome 101](https://youtu.be/Xbvloe13nak)
- **커뮤니티 포럼**: [https://www.alphagenomecommunity.com](https://www.alphagenomecommunity.com)


# 마무리

AlphaGenome은 변이 해석에 있어 기존 도구(CADD, SpliceAI 등)와 차별화되는 점이 있습니다. 하나의 모델에서 발현, 스플라이싱, 크로마틴, 3D 구조까지 **통합적으로 예측**한다는 점입니다.

API key 하나면 Python에서 바로 사용할 수 있으니, 관심 있는 변이가 있다면 직접 돌려보세요.


Reference
---
- [https://github.com/google-deepmind/alphagenome](https://github.com/google-deepmind/alphagenome)
- [https://www.alphagenomedocs.com/](https://www.alphagenomedocs.com/)
- [https://deepmind.google.com/science/alphagenome](https://deepmind.google.com/science/alphagenome)
- [https://doi.org/10.1038/s41586-025-10014-0](https://doi.org/10.1038/s41586-025-10014-0)
