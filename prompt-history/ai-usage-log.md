# AI Usage Log — Exam Scheduling System

## 1. AI tool used

- Tool: ChatGPT
- Purpose: Development assistance, debugging, test design, documentation guidance, and validation support.
- Development ownership: Individual project implementation, review, and final verification by the candidate.

## 2. Areas where AI assistance was used

| Area | Assistance received |
|---|---|
| Project setup | Guidance on organizing the backend, data, documentation, and test folders |
| Database design | Discussion of entity relationships, primary keys, foreign keys, and constraints |
| Synthetic data generation | Assistance reviewing deterministic data generation and CSV/JSON exports |
| Data validation | Guidance on integrity checks, record counts, and validation results |
| Anomaly detection | Assistance designing and testing five labelled anomaly scenarios |
| Scheduling algorithm | Guidance reviewing room capacity, availability, invigilator, accommodation, and equipment constraints |
| Automated testing | Assistance creating and extending pytest tests |
| Reproducibility | Guidance verifying repeated data generation using SHA-256 checksums |
| Documentation | Assistance updating the data manifest and preparing project documentation |

## 3. Representative prompt topics

The following are summaries of the prompts used during development, not verbatim exports:

1. Guide me step by step through building the exam scheduling system.
2. Help review and improve the synthetic data generator.
3. Help validate primary keys, foreign keys, relationships, and dataset consistency.
4. Help implement and test the five labelled anomaly scenarios.
5. Help improve the scheduling algorithm to consider room requirements and availability.
6. Help create pytest tests for conflict detection and room equipment requirements.
7. Help verify that generated schedules contain no conflicts.
8. Help verify reproducibility using a fixed random seed and file checksums.
9. Help update the generation summary and data manifest.
10. Help prepare the project for GitHub submission.

## 4. How AI assistance was used

AI was used as a development assistant to explain implementation options, suggest code changes, identify potential issues, and help design tests.

I reviewed the suggested changes, applied them to the project, ran the commands locally, and examined the results. I remain responsible for understanding and validating the submitted implementation.

## 5. Verification performed

The following results were obtained during development:

- 15 automated pytest tests passed.
- 12,767 baseline data validation checks passed with zero errors.
- All five labelled anomaly scenarios were detected.
- Two generations using seed `20261022` produced identical checksums for 15 top-level CSV/JSON files.
- The scheduler assigned 300 out of 300 exams.
- Independent schedule validation reported zero conflicts.

## 6. Limitations and remaining review

The implementation and documentation should be reviewed before submission. In particular, the candidate should verify the scheduling constraints, data model, assumptions, test coverage, and known limitations and be prepared to explain the design decisions independently.

---

**Transparency note:** This is a summary of AI assistance, not a verbatim export of every prompt. The original ChatGPT conversation should be retained as the detailed prompt-history record if requested by the assessment instructions.

## 7. Prompt history availability

This log records representative prompt topics and the nature of AI assistance used during development. It is not a complete verbatim transcript.

The original ChatGPT conversation contains the detailed development discussion, code reviews, debugging steps, and verification guidance. If a complete export is unavailable, this summary is provided as the available record. No AI-generated implementation was accepted without local review and execution.