# AI Revenue Audit RAG Prototype

## Overview

This project demonstrates an AI-assisted eCash reconciliation workflow for casino revenue audit operations.

The prototype compares SDS Slot System eCash data against CMP eCash data by slot location and gaming date, identifies variances, enables human-in-the-loop validation, captures adjustment reasons, validates adjustments against SDS values, and reruns reconciliation after approved adjustments are committed.

The solution simulates a real-world casino revenue audit process using Python, Pandas, and Streamlit.



## Business Problem

Casino revenue audit teams spend significant operational effort reconciling transactional data across multiple systems.

Traditional reconciliation processes are:
- highly manual
- spreadsheet driven
- time-consuming
- prone to human error

Revenue auditors must:
- compare SDS and CMP values
- identify variances
- investigate discrepancies
- apply adjustments
- rerun reconciliation reports

This prototype demonstrates how AI-assisted workflows and human-in-the-loop validation can modernize the reconciliation process.



## Key Features

- SDS vs CMP eCash reconciliation
- Slot-level variance detection
- Human-in-the-loop adjustment validation
- Adjustment reason capture
- CMP adjustment simulation
- Reconciliation rerun process
- Downloadable reconciliation reports
- Downloadable adjustment audit logs
- AI-style audit summary generation



## Workflow


Upload SDS eCash File
        ↓
Upload CMP eCash File
        ↓
System compares data by:
- slot_location
- gamingdt
        ↓
Variance detection
        ↓
Human validation review
        ↓
Adjustment reason entry
        ↓
CMP adjustment simulation
        ↓
Validation against SDS values
        ↓
Commit approved adjustments
        ↓
Rerun reconciliation

## Application Screenshots

### File Upload Screen
![File Upload Screen](assets/upload-screen.png)

### Variance Detection Screen
![Variance Detection Screen](assets/variance-screen.png)

### Human-in-the-Loop Adjustment Screen
![Human-in-the-Loop Adjustment Screen](assets/adjustment-screen.png)


## Sample Data Format

### SDS eCash File


slot_location,gamingdt,ecash_in,ecash_out
101,2026-05-01,1200,500
102,2026-05-01,900,300
103,2026-05-01,1500,700
104,2026-05-01,2000,800


### CMP eCash File


slot_location,gamingdt,ecash_in,ecash_out
101,2026-05-01,1200,500
102,2026-05-01,900,250
103,2026-05-01,1500,700
104,2026-05-01,1950,800




## Technologies Used

- Python
- Streamlit
- Pandas



## How to Run the Application

### Install Dependencies


py -m pip install -r requirements.txt


### Run Streamlit Application


py -m streamlit run app.py



## Human-in-the-Loop Validation

This prototype demonstrates enterprise-style audit controls where:

- variances are identified automatically
- human auditors validate discrepancies
- adjustment reasons are captured
- CMP adjustments are validated against SDS values
- approved changes are committed
- reconciliation is rerun after adjustments

This approach helps improve:
- audit accuracy
- operational control
- adjustment traceability
- reconciliation efficiency



## AI Use Case

This project represents an early-stage AI-assisted revenue audit workflow that can evolve into a Retrieval-Augmented Generation (RAG) solution.

Potential future AI enhancements include:
- AI-generated root cause analysis
- automated adjustment recommendations
- anomaly detection
- conversational audit assistant
- vector database integration
- enterprise reporting dashboards



## Repository Structure


ai-revenue-audit-rag-prototype/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── sds_ecash.csv
│   └── cmp_ecash.csv
│
├── assets/
│   ├── app-upload-screen.png
│   └── variance-review-screen.png
│
└── architecture/
    └── workflow-diagram.png



## Skills Demonstrated

- Revenue Audit Workflow Automation
- Human-in-the-Loop AI Design
- Enterprise Reconciliation Logic
- Variance Detection
- Data Validation
- Audit Controls
- Streamlit Application Development
- Python Data Processing
- Technical Project Management
- AI Solution Architecture



## Future Enhancements

- Real-time reconciliation engine
- AI-generated root cause explanations
- Adjustment approval workflow
- Role-based access control
- Database integration
- LangChain integration
- Vector database implementation
- Enterprise audit dashboard
- Cloud deployment architecture



## Author

Gowrishankar Sivalingappa, PMP

AI TPM | Revenue Systems | AI Automation | Gaming Operations