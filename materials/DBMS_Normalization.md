# Database Management Systems: Relational Normalization

## 1. What is Database Normalization?
Normalization is the systematic approach of decomposing tables to eliminate data redundancy (duplicate data) and avoid insertion, update, and deletion anomalies. It divides larger tables into smaller tables and links them using relationships.

## 2. Functional Dependencies
A functional dependency $\alpha \rightarrow \beta$ is a constraint between two sets of attributes in a relational database. It states that the value of $\alpha$ uniquely determines the value of $\beta$.
- **Trivial Functional Dependency**: If $\beta \subseteq \alpha$.
- **Non-Trivial Functional Dependency**: If $\beta \not\subseteq \alpha$.

## 3. Normal Forms (1NF through BCNF)
- **First Normal Form (1NF)**:
  - Each column contains atomic (indivisible) values.
  - No repeating groups or multivalued attributes are allowed.
  - Each record must have a unique identifier (Primary Key).

- **Second Normal Form (2NF)**:
  - Table is in 1NF.
  - No partial dependencies: Every non-prime attribute must be fully functionally dependent on the entire primary key, not on a subset of a composite primary key.

- **Third Normal Form (3NF)**:
  - Table is in 2NF.
  - No transitive dependencies: Non-prime attributes must not depend on other non-prime attributes ($X \rightarrow Y$ and $Y \rightarrow Z$).
  - For every functional dependency $X \rightarrow A$, either $X$ is a super key, or $A$ is a prime attribute.

- **Boyce-Codd Normal Form (BCNF)**:
  - A stricter version of 3NF.
  - For every non-trivial functional dependency $X \rightarrow A$, $X$ must be a super key.
  - Eliminates all anomalies arising from multiple overlapping candidate keys.

## 4. Lossless Join and Dependency Preservation
When decomposing a relation $R$ into $R_1$ and $R_2$:
1. **Lossless Decomposition**: $R_1 \bowtie R_2 = R$. The common attributes must form a superkey of at least one relation ($R_1 \cap R_2 \rightarrow R_1$ or $R_1 \cap R_2 \rightarrow R_2$).
2. **Dependency Preservation**: All functional dependencies of the original relation can be enforced on the decomposed relations without needing joins.
