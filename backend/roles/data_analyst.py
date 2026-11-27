"""
RolePrompt AI: Data Analyst role configuration (Iteration 5).

This file holds all Data Analyst instructions. No other file contains them.

Each task has:
- objective:     what a strong optimized prompt for this task should achieve
- validation:    task-specific checks the optimized prompt should include
- requirements:  information the context analyzer looks for. Each one is:
    essential = True  -> if missing, the agent asks a clarification question
    essential = False -> if missing, the agent records an assumption instead
  Keywords are matched as whole words, case-insensitively.
"""

# ---------------------------------------------------------------------------
# Shared requirements (reused by several tasks)
# ---------------------------------------------------------------------------
DATA_SOURCE = {
    "key": "data_source",
    "label": "Data source",
    "essential": True,
    "keywords": [
        "csv", "excel", "xlsx", "spreadsheet", "dataset", "data set", "table",
        "database", "sql", "postgres", "postgresql", "mysql", "sqlite", "bigquery",
        "snowflake", "json", "parquet", "file", "records", "rows", "columns",
    ],
    "question": (
        "What data does this task work on (for example a CSV file, an Excel sheet, "
        "or a database table), and which columns does it contain?"
    ),
}

# ---------------------------------------------------------------------------
# Role definition
# ---------------------------------------------------------------------------
ROLE = {
    "id": "data-analyst",
    "label": "Data Analyst",
    "persona": (
        "You are a senior data analyst. You write precise, reproducible analysis instructions, "
        "state your assumptions, and never claim a result that the data cannot support."
    ),
    "validation_standards": [
        "State the number of rows and columns the analysis covers before drawing conclusions.",
        "Name every assumption and every data quality issue explicitly.",
        "Make results reproducible: the steps, filters and definitions must be stated.",
    ],
    "tasks": {
        "data-cleaning": {
            "label": "Data Cleaning",
            "objective": "Prepare the dataset for analysis by finding and fixing quality problems without losing information silently.",
            "validation": [
                "Report how many rows were changed, removed or imputed, and by what rule.",
                "Confirm that column types are correct after cleaning.",
            ],
            "requirements": [
                DATA_SOURCE,
                {
                    "key": "quality_issues",
                    "label": "Known data quality issues",
                    "essential": False,
                    "keywords": ["missing", "duplicate", "outlier", "null", "inconsistent", "typo", "whitespace", "format"],
                    "assumption": "No specific quality issues were named, so the prompt asks for checks on missing values, duplicates and inconsistent formats.",
                },
            ],
        },
        "exploratory-data-analysis": {
            "label": "Exploratory Data Analysis",
            "objective": "Summarize the dataset's structure, distributions and relationships to surface patterns and questions worth investigating.",
            "validation": [
                "Report summary statistics for every numeric column and frequencies for key categories.",
                "Separate observed patterns from conclusions that need further testing.",
            ],
            "requirements": [
                DATA_SOURCE,
                {
                    "key": "eda_focus",
                    "label": "Focus of the exploration",
                    "essential": False,
                    "keywords": ["distribution", "correlat", "trend", "outlier", "summary", "pattern", "relationship"],
                    "assumption": "No specific question was named, so the prompt asks for a general summary of distributions, relationships and outliers.",
                },
            ],
        },
        "sql-query-generation": {
            "label": "SQL Query Generation",
            "objective": "Produce a correct, readable SQL query that answers the stated question against the stated schema.",
            "validation": [
                "State the SQL dialect and confirm every table and column name exists in the given schema.",
                "Explain the join logic and how NULL values are handled.",
            ],
            "requirements": [
                {
                    "key": "schema",
                    "label": "Database and schema",
                    "essential": True,
                    "keywords": ["table", "column", "schema", "database", "postgres", "postgresql", "mysql", "sqlite", "bigquery", "snowflake", "sql server"],
                    "question": "Which database and tables should the query use, and what are the main columns?",
                },
            ],
        },
        "data-visualization": {
            "label": "Data Visualization",
            "objective": "Specify a chart that shows the intended pattern clearly and honestly for the stated audience.",
            "validation": [
                "Name the chart type and justify it for the data shape.",
                "Require labelled axes, units and a title that states the finding.",
            ],
            "requirements": [
                DATA_SOURCE,
                {
                    "key": "chart_type",
                    "label": "Chart type",
                    "essential": False,
                    "keywords": ["bar", "line", "pie", "scatter", "histogram", "chart", "graph", "plot", "heatmap", "dashboard"],
                    "assumption": "No chart type was specified, so the prompt asks for the chart type that best suits the data.",
                },
            ],
        },
        "statistical-analysis": {
            "label": "Statistical Analysis",
            "objective": "Define the statistical question, the appropriate test or model, and how results should be interpreted.",
            "validation": [
                "Check and state the assumptions of the chosen test before reporting results.",
                "Report effect sizes and confidence intervals alongside p-values.",
            ],
            "requirements": [
                DATA_SOURCE,
                {
                    "key": "statistical_question",
                    "label": "Statistical question",
                    "essential": False,
                    "keywords": ["hypothesis", "significan", "correlat", "regression", "t-test", "p-value", "confidence", "compare", "difference"],
                    "assumption": "No specific statistical question was named, so the prompt requires stating the hypothesis and test before analysis.",
                },
            ],
        },
        "business-intelligence": {
            "label": "Business Intelligence",
            "objective": "Turn data into a business-focused analysis that links metrics to decisions.",
            "validation": [
                "Define each metric precisely, including the time period and filters.",
                "Separate what the data shows from recommendations, and label recommendations as such.",
            ],
            "requirements": [
                DATA_SOURCE,
                {
                    "key": "business_metric",
                    "label": "Business metric or KPI",
                    "essential": True,
                    "keywords": ["revenue", "sales", "kpi", "metric", "profit", "churn", "conversion", "margin", "cost", "retention", "growth"],
                    "question": "Which business metric or KPI should this analysis focus on?",
                },
            ],
        },
        "predictive-analytics": {
            "label": "Predictive Analytics",
            "objective": "Specify a predictive model workflow: target definition, features, evaluation and limitations.",
            "validation": [
                "Require a train, validation and test split, with no leakage between them.",
                "Report at least one appropriate metric and a baseline comparison.",
            ],
            "requirements": [
                DATA_SOURCE,
                {
                    "key": "target",
                    "label": "Target outcome",
                    "essential": True,
                    "keywords": ["predict", "forecast", "target", "label", "outcome", "classify", "classification", "estimate"],
                    "question": "Which outcome should the model predict (the target column), and what counts as success?",
                },
            ],
        },
        "data-reporting": {
            "label": "Data Reporting",
            "objective": "Produce a clear report that communicates findings to a specific audience with supporting numbers.",
            "validation": [
                "Lead with the key finding, then the supporting evidence.",
                "Every number must state its source, period and definition.",
            ],
            "requirements": [
                DATA_SOURCE,
                {
                    "key": "audience",
                    "label": "Report audience",
                    "essential": False,
                    "keywords": ["executive", "manager", "team", "stakeholder", "client", "board", "non-technical", "audience"],
                    "assumption": "No audience was named, so the report is written for a non-specialist business reader.",
                },
            ],
        },
    },
}