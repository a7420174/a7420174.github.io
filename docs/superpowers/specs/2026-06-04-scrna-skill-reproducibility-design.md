# 실험 설계: AI 에이전트의 scRNA-seq QC — 스킬 사용 vs 미사용 (재현성/정확성)

작성일: 2026-06-04

## 가설
AI 에이전트가 scRNA-seq QC를 수행할 때, bioinformatics 스킬(`single-cell-rna-qc`)을
사용하면 **재현성(reproducibility)** 과 **정확성(scverse best-practice 준수)** 이 향상된다.

핵심 통찰: 해당 스킬은 결정적(deterministic) 파이썬 스크립트(`qc_analysis.py`)로 동작한다.
즉 "스킬 사용 = 검증된 방법론의 고정화" → 재현성이 구조적으로 보장된다.

## 데이터
- `sc.datasets.pbmc3k()` — 2,700 cells × 32,738 genes, raw counts, human PBMC (MT- prefix)
- 저장: `/home/a7420174/scrna-skill-exp/data/pbmc3k_raw.h5ad`

## 설계 (QC만, 동일 입력)
| 조건 | 실행 | 측정 |
|---|---|---|
| 스킬 미사용 | 독립 서브에이전트 N=5 (동일 중립 프롬프트, 방법론 미지정, 격리 디렉토리) | 5회 결과 분산 |
| 스킬 사용 | `qc_analysis.py` 결정적 스크립트 (2회 실행 → 동일 입증) | 분산 = 0 대조군 |

## 측정 지표
- 재현성: 5회 간 (필터 후 셀 수 / 유전자 수 / 사용 임계값)의 분산·범위
- 정확성: MAD 기반 필터링, joint outlier 검출, MT 패턴 정확성, rare population 보존, QC metric 계산
- 완성도: 시각화 / annotated h5ad 등 산출물

## 산출물
- 비교 표 + 방법론 차이 서술
- 블로그 포스트 `_posts/2026-06-04-AI-Agent-scRNA-seq-Skill-Reproducibility.md` (한국어, toc)
- teaser SVG (`/assets/images/`)

## 정직성 원칙
- 실제 실행한 숫자만 보고. N=5 표본의 통계적 한계 명시.
- 스킬이 QC 한정이며 결정적 스크립트라 재현성이 당연하다는 점 솔직히 서술.
