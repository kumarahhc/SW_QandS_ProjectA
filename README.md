# SW_QandS_ProjectA
Advanced Software Quality and Security - Project A
 Project Tasks
 1. Data Preparation:
 • Utilize the raw data in the referenced paper, comprising 193 unique scenarios
 and their 1283 representative samples.
 • Ensure data anonymization and formatting to prepare for use in LRM.
 2. Model Integration:
 • Implement LRM with reasoning enhancements, ensuring it can process risk
 analysis scenarios.
 • Set up Retrieval-Augmented Generation (RAG) mechanisms for context en
richment during risk assessment.
 3. Experimentation:
 • Replicate the original analysis conducted with GPT-3.5, GPT-4, and their
 f
 ine-tuned and RAG-assisted versions using LRM.
 • Conduct a detailed evaluation of LRM’s outputs against ground truth and
 human expert reviews by carefully storing the output and the reasoning
• Create a CSV file containing scenario ID, reasoning, description of the classi
f
 ication, threat ID, and vulnerability ID.
 • W.O:themodelcanoutputmultiple threats or vulnerabilities for each scenario.
 You can handle those cases by creating multiple rows on the csv for the given
 scenario ID.
 4. Anomaly Analysis:
 • Identify and document anomalies in LRM’s outputs, focusing on errors, hal
lucinations, or inconsistencies in reasoning.
 • Explore the root causes of these anomalies and compare them with findings
 from the referenced study.
 5. Performance Comparison:
 • Benchmark LRM against the models used in the paper (e.g., GPT-3.5 and
 GPT-4) in terms of:– Accuracy (IR Accuracy Metrics)– Actionability (As described in the paper)– Speed (Time elapsed between the first and last API call)– Comprehensiveness (As described in the paper)– Ability to discover hidden risks (As described in the paper)
 6. Results Analysis:
 • Present detailed statistical analysis and visualization of LRM’s performance.
 • Discuss the implications of LRM’s reasoning enhancements on mission-critical
 risk analysis.
 Deliverables
 1. Source Code:
 • Fully commented and structured code for integrating LRM, implementing
 RAG, and conducting the analysis.
 2. Dataset:
 • An anonymized version of the processed raw data used in the analysis.
 • The output csv as described before.
 3. Report:
 • Acomprehensive document containing:– Introduction and objectives– Methodology (including model setup, data preprocessing, and experimen
tation details)– Results and discussions
 2
– Root cause analysis of anomalies– Conclusions and recommendations for future work
 4. Visualizations:
 • Graphical representation of key findings (e.g., accuracy trends, error analysis,
 hallucination frequency)
