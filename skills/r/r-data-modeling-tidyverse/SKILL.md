---
name: r-data-modeling-tidyverse
description: Definitive skill for R statistical computing, tidyverse pipelines, high-speed data.table manipulation, ggplot2 visualization, and reproducible modeling.
language: r
category: programming-languages
quality_score: 100
tier: official
triggers:
  - r
  - tidyverse
  - data.table
  - ggplot2
  - statistical modeling
  - cran
---
# R High-Performance Data Modeling, Tidyverse & Data.table

Architectural standards for large-scale data transformation, statistical modeling, and reproducible analysis in R.

## 1. High-Performance Data Manipulation (data.table)
* **In-Place Memory Modification**: For datasets exceeding 1GB, use `data.table` and reference assignment (`:=`) to avoid memory copying.
  ```r
  library(data.table)

  compute_metrics <- function(dt, min_volume) {
      # In-place filtering and aggregation
      dt[volume >= min_volume, .(
          mean_price = mean(price, na.rm = TRUE),
          total_trades = .N
      ), by = .(ticker, sector)]
  }
  ```

## 2. Functional Programming & Reproducibility
* **Vectorized Computations**: Completely avoid imperative `for` loops over data frames; utilize vectorized primitives and `purrr::map` workflows.
