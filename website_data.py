# data.py - Banking Industry Job Database
# Feel free to add, remove, or modify any entries

jobs_list = [
    # ========== FRONT OFFICE (Client-Facing, Revenue Generating) ==========
    {
        "id": 1,
        "name": "Investment Banking Analyst",
        "department": "Investment Banking Division (IBD)",
        "office": "Front Office",
        "description": "Supports M&A deals, IPOs, and corporate financing. Responsible for financial modeling, pitch books, and due diligence. High pressure but lucrative.",
        "salary": "$90k - $150k + bonus",
        "suitable_major": ["Finance", "Economics", "Accounting", "Mathematics"],
        "suitable_grade": "Senior/Recent Graduate",
        "personality": ["Ambitious", "Detail-oriented", "Resilient", "Quantitative"],
        "skills": ["Financial Modeling", "Valuation", "Excel", "Deal Execution"]
    },
    {
        "id": 2,
        "name": "Corporate Banking Relationship Manager",
        "department": "Corporate Banking",
        "office": "Front Office",
        "description": "Manages relationships with large corporations, providing loans, treasury services, and capital market solutions. Focuses on client retention and cross-selling.",
        "salary": "$80k - $130k + bonus",
        "suitable_major": ["Finance", "Business Administration", "Economics"],
        "suitable_grade": "Senior/Graduate Student",
        "personality": ["Outgoing", "Persuasive", "Strategic thinker", "Client-focused"],
        "skills": ["Client Relationship", "Credit Analysis", "Negotiation"]
    },
    {
        "id": 3,
        "name": "Commercial Loan Officer",
        "department": "Commercial Banking",
        "office": "Front Office",
        "description": "Originates and underwrites loans for middle-market businesses. Evaluates financial statements, assesses risk, and structures loan packages.",
        "salary": "$70k - $110k + commission",
        "suitable_major": ["Finance", "Accounting", "Economics"],
        "suitable_grade": "Junior/Senior",
        "personality": ["Analytical", "Sociable", "Risk-aware", "Independent"],
        "skills": ["Underwriting", "Financial Statement Analysis", "Sales"]
    },
    {
        "id": 4,
        "name": "Private Banker / Wealth Advisor",
        "department": "Private Banking / Wealth Management",
        "office": "Front Office",
        "description": "Provides personalized financial planning, investment management, and estate planning to high-net-worth individuals (HNWIs).",
        "salary": "$85k - $140k + bonus",
        "suitable_major": ["Finance", "Economics", "Psychology", "Marketing"],
        "suitable_grade": "Senior/Graduate Student",
        "personality": ["Trustworthy", "Empathetic", "Discreet", "Patient"],
        "skills": ["Portfolio Management", "Client Advisory", "CFA/CWM Preferred"]
    },
    {
        "id": 5,
        "name": "Retail Branch Manager",
        "department": "Retail Banking",
        "office": "Front Office",
        "description": "Oversees daily operations of a bank branch. Manages staff, drives sales targets, ensures compliance, and delivers excellent customer service.",
        "salary": "$65k - $100k + incentives",
        "suitable_major": ["Business Administration", "Management", "Finance"],
        "suitable_grade": "Senior/Experienced Graduate",
        "personality": ["Leadership-oriented", "Approachable", "Organized", "Decisive"],
        "skills": ["Team Management", "Sales Strategy", "Compliance"]
    },
    {
        "id": 6,
        "name": "Personal Banker",
        "department": "Retail Banking",
        "office": "Front Office",
        "description": "Assists retail customers with opening accounts, applying for loans, and selecting financial products. Acts as the primary financial advisor for individuals.",
        "salary": "$50k - $75k + incentives",
        "suitable_major": ["Finance", "Business", "Communications"],
        "suitable_grade": "Fresh Graduate/Junior",
        "personality": ["Friendly", "Helpful", "Good listener", "Patient"],
        "skills": ["Customer Service", "Product Knowledge", "CRM Tools"]
    },
    {
        "id": 7,
        "name": "Teller / Customer Service Representative",
        "department": "Retail Banking",
        "office": "Front Office",
        "description": "Handles daily cash transactions, check deposits, withdrawals, and basic customer inquiries. The most common entry-level role in banking.",
        "salary": "$35k - $45k",
        "suitable_major": ["Any Major", "Business", "Communications"],
        "suitable_grade": "Fresh Graduate",
        "personality": ["Friendly", "Detail-oriented", "Honest", "Patient"],
        "skills": ["Cash Handling", "Customer Service", "Attention to Detail"]
    },
    
    # ========== MIDDLE OFFICE (Risk, Compliance, Product) ==========
    {
        "id": 8,
        "name": "Credit Risk Analyst",
        "department": "Risk Management",
        "office": "Middle Office",
        "description": "Assesses the creditworthiness of corporate and retail borrowers. Develops risk models, monitors portfolio performance, and recommends credit limits.",
        "salary": "$75k - $115k",
        "suitable_major": ["Finance", "Statistics", "Economics", "Mathematics"],
        "suitable_grade": "Senior/Graduate Student",
        "personality": ["Cautious", "Analytical", "Methodical", "Skeptical"],
        "skills": ["Credit Scoring", "Risk Modeling", "SQL", "Python/R"]
    },
    {
        "id": 9,
        "name": "Market Risk Analyst",
        "department": "Risk Management",
        "office": "Middle Office",
        "description": "Monitors and analyzes financial market risks including interest rate risk, foreign exchange risk, and commodity price risk. Uses VaR and stress testing.",
        "salary": "$80k - $120k",
        "suitable_major": ["Financial Engineering", "Mathematics", "Physics", "Economics"],
        "suitable_grade": "Graduate Student Preferred",
        "personality": ["Quantitative", "Vigilant", "Detail-oriented", "Calm under pressure"],
        "skills": ["VaR", "Stress Testing", "Bloomberg/Reuters", "Python/R"]
    },
    {
        "id": 10,
        "name": "Compliance Officer",
        "department": "Compliance & Legal",
        "office": "Middle Office",
        "description": "Ensures bank operations comply with all regulatory requirements (KYC, AML, Dodd-Frank). Conducts internal audits and training programs.",
        "salary": "$70k - $110k",
        "suitable_major": ["Law", "Finance", "Business Ethics", "Criminal Justice"],
        "suitable_grade": "Senior/Graduate Student",
        "personality": ["Principled", "Meticulous", "Ethical", "Detail-oriented"],
        "skills": ["Regulatory Knowledge", "Auditing", "AML/KYC", "Legal Research"]
    },
    {
        "id": 11,
        "name": "Loan Underwriter",
        "department": "Credit / Underwriting",
        "office": "Middle Office",
        "description": "Evaluates loan applications (mortgage, auto, personal) by analyzing income, credit history, and collateral. Approves or denies applications based on policy.",
        "salary": "$60k - $90k",
        "suitable_major": ["Finance", "Accounting", "Economics"],
        "suitable_grade": "Junior/Senior",
        "personality": ["Conservative", "Logical", "Detail-focused", "Judicious"],
        "skills": ["Underwriting Guidelines", "Credit Reports", "Financial Analysis"]
    },
    {
        "id": 12,
        "name": "Product Manager (Banking)",
        "department": "Product Development",
        "office": "Middle Office",
        "description": "Designs and manages banking products such as checking accounts, credit cards, or mobile banking apps. Works with tech, marketing, and ops teams.",
        "salary": "$90k - $140k",
        "suitable_major": ["Business", "Marketing", "Information Systems"],
        "suitable_grade": "Senior/Graduate Student",
        "personality": ["Creative", "User-centric", "Strategic", "Collaborative"],
        "skills": ["Product Lifecycle", "Agile/Scrum", "Market Research", "UX/UI basics"]
    },
    
    # ========== BACK OFFICE (Support, Operations, IT, Finance) ==========
    {
        "id": 13,
        "name": "Financial Controller",
        "department": "Finance & Accounting",
        "office": "Back Office",
        "description": "Oversees the bank's financial reporting, general ledger, budgeting, and internal controls. Ensures accuracy of financial statements.",
        "salary": "$90k - $140k",
        "suitable_major": ["Accounting", "Finance", "Economics"],
        "suitable_grade": "Graduate Student / CPA Preferred",
        "personality": ["Precise", "Organized", "Conservative", "Disciplined"],
        "skills": ["GAAP/IFRS", "Financial Reporting", "ERP Systems", "Auditing"]
    },
    {
        "id": 14,
        "name": "Software Engineer / Developer",
        "department": "Information Technology (IT)",
        "office": "Back Office",
        "description": "Develops and maintains banking systems including core banking platforms, mobile apps, trading systems, and internal tools.",
        "salary": "$85k - $150k",
        "suitable_major": ["Computer Science", "Software Engineering", "Information Technology"],
        "suitable_grade": "Junior/Senior/Graduate",
        "personality": ["Problem-solver", "Logical", "Curious", "Team-player"],
        "skills": ["Java/Python/C++", "SQL", "Cloud (AWS/Azure)", "Agile Development"]
    },
    {
        "id": 15,
        "name": "Data Analyst / Data Scientist",
        "department": "Data & Analytics",
        "office": "Back Office",
        "description": "Analyzes customer data, transaction patterns, and market trends to drive business decisions. Builds predictive models for fraud detection and customer segmentation.",
        "salary": "$80k - $130k",
        "suitable_major": ["Data Science", "Statistics", "Computer Science", "Mathematics"],
        "suitable_grade": "Senior/Graduate Student",
        "personality": ["Inquisitive", "Analytical", "Creative with data", "Curious"],
        "skills": ["Python/R", "SQL", "Machine Learning", "Tableau/Power BI"]
    },
    {
        "id": 16,
        "name": "Operations Analyst",
        "department": "Operations / Back Office",
        "office": "Back Office",
        "description": "Ensures smooth daily processing of trades, settlements, payments, and reconciliations. Focuses on operational efficiency and error reduction.",
        "salary": "$55k - $80k",
        "suitable_major": ["Business Administration", "Finance", "Economics"],
        "suitable_grade": "Fresh Graduate/Junior",
        "personality": ["Organized", "Process-oriented", "Efficient", "Reliable"],
        "skills": ["Process Improvement", "Settlement Systems", "Attention to Detail"]
    },
    {
        "id": 17,
        "name": "Human Resources (HR) Business Partner",
        "department": "Human Resources",
        "office": "Back Office",
        "description": "Manages recruitment, employee relations, performance management, and talent development within the bank.",
        "salary": "$60k - $100k",
        "suitable_major": ["Human Resources", "Psychology", "Business Administration"],
        "suitable_grade": "Junior/Senior",
        "personality": ["Empathetic", "Approachable", "Confidential", "Fair"],
        "skills": ["Recruiting", "Employee Relations", "HRIS", "Labor Law"]
    },
    {
        "id": 18,
        "name": "Internal Auditor",
        "department": "Internal Audit",
        "office": "Back Office",
        "description": "Evaluates internal controls, risk management, and governance processes. Identifies weaknesses and recommends improvements.",
        "salary": "$70k - $110k",
        "suitable_major": ["Accounting", "Finance", "Business"],
        "suitable_grade": "Senior/Graduate Student",
        "personality": ["Objective", "Thorough", "Independent", "Detail-oriented"],
        "skills": ["Internal Auditing", "Risk Assessment", "CIA/CPA Preferred"]
    },
    
    # ========== SPECIALIZED / NICHE ROLES ==========
    {
        "id": 19,
        "name": "ESG / Sustainability Analyst",
        "department": "Sustainability / Strategy / Community Impact",
        "office": "Specialized",
        "description": "Measures and reports on the bank's environmental, social, and governance performance. Evaluates sustainability initiatives, workforce programs, community investments, and portfolio impacts while helping the bank meet reporting expectations.",
        "salary": "$75k - $150k",
        "suitable_major": ["Finance", "Economics", "Sustainability", "Environmental Studies", "Data Analytics", "Public Policy"],
        "suitable_grade": "Recent Graduate/Graduate Student",
        "personality": ["Analytical", "Curious", "Strategic", "Detail-oriented", "Forward-thinking"],
        "skills": ["ESG Frameworks", "Data Analysis", "Research", "Sustainability Reporting", "Excel", "Presentation Skills"],
        "career_path": "ESG Analyst → Senior ESG Analyst → ESG or Sustainability Manager → Director of Sustainability / Head of ESG",
        "interview_questions": [
            "How would you evaluate a bank's environmental and social impact?",
            "Which ESG reporting frameworks have you researched or used?",
            "Tell us about a time you turned complex data into a clear recommendation."
        ]
    },
    {
        "id": 20,
        "name": "Treasury Analyst",
        "department": "Treasury",
        "office": "Specialized",
        "description": "Manages the bank's liquidity, cash flow, and funding strategies. Executes foreign exchange and interest rate hedging activities.",
        "salary": "$80k - $120k",
        "suitable_major": ["Finance", "Economics", "Mathematical Finance"],
        "suitable_grade": "Senior/Graduate Student",
        "personality": ["Strategic", "Quantitative", "Calm under pressure", "Decisive"],
        "skills": ["Cash Management", "FX Hedging", "Capital Markets", "Bloomberg"]
    },

    # ========== ADDITIONAL BANKING ROLES ==========
    {
        "id": 21,
        "name": "Paralegal",
        "department": "Legal Department",
        "office": "Back Office",
        "description": "Supports in-house counsel through legal research, contract and corporate-record management, document preparation, regulatory tracking, litigation and subpoena coordination, and governance documentation.",
        "salary": "$55k - $90k",
        "suitable_major": ["Legal Studies", "Political Science", "Business Administration"],
        "suitable_grade": "Senior/Fresh Graduate",
        "personality": ["Detail-oriented", "Organized", "Analytical"],
        "skills": ["Legal Research", "Contract Management", "Regulatory Compliance", "Corporate Governance"],
        "career_path": "Paralegal → Senior Paralegal → Legal Operations Manager → Corporate Governance or Legal Department Manager",
        "interview_questions": [
            "How do you organize and protect confidential legal records?",
            "Describe a legal research project and how you communicated your findings.",
            "How would you manage several contracts with competing deadlines?"
        ]
    },
    {
        "id": 22,
        "name": "AML/KYC Analyst",
        "department": "Compliance",
        "office": "Middle Office",
        "description": "Conducts Anti-Money Laundering and Know Your Customer reviews, evaluates customer due-diligence documents, monitors transactions, investigates suspicious activity, and supports sanctions screening and regulatory reporting.",
        "salary": "$65k - $105k",
        "suitable_major": ["Finance", "Business Administration", "Public Policy", "Political Science", "Criminal Justice"],
        "suitable_grade": "Junior/Senior/Fresh Graduate",
        "personality": ["Detail-oriented", "Analytical", "Ethical", "Inquisitive"],
        "skills": ["AML Monitoring", "KYC Due Diligence", "Sanctions Screening", "Regulatory Compliance"],
        "career_path": "AML/KYC Analyst → Senior AML Analyst → AML Investigations Manager → BSA/AML Officer or Chief Compliance Officer",
        "interview_questions": [
            "What information would make you escalate a customer for enhanced due diligence?",
            "How would you investigate an unusual transaction pattern?",
            "How do you balance regulatory rigor with a positive customer experience?"
        ]
    },
    {
        "id": 23,
        "name": "Fixed Income Analyst",
        "department": "Capital Markets",
        "office": "Front Office",
        "description": "Analyzes government, corporate, municipal, mortgage-backed, and other debt securities. Evaluates credit quality, interest-rate trends, and market conditions to support investment decisions, portfolio management, and client recommendations.",
        "salary": "$85k - $140k",
        "suitable_major": ["Finance", "Economics", "Mathematics", "Business Administration"],
        "suitable_grade": "Senior/Fresh Graduate/Graduate Student",
        "personality": ["Analytical", "Quantitative", "Detail-oriented"],
        "skills": ["Bloomberg Terminal", "Credit Analysis", "Fixed Income Analysis", "Interest Rate Analysis"],
        "career_path": "Fixed Income Analyst → Senior Analyst → Portfolio Manager or Fixed Income Strategist → Head of Fixed Income",
        "interview_questions": [
            "How do interest-rate changes affect bond prices and duration?",
            "How would you assess the credit quality of a corporate bond issuer?",
            "Which fixed-income market indicator do you watch most closely and why?"
        ]
    },
    {
        "id": 24,
        "name": "Marketing Coordinator",
        "department": "Marketing and Communications",
        "office": "Middle Office",
        "description": "Supports marketing campaigns, manages project timelines, coordinates with designers and vendors, assists with content creation, and tracks campaign performance.",
        "salary": "$50k - $70k",
        "suitable_major": ["Marketing", "Communications", "Advertising", "Business Administration"],
        "suitable_grade": "Recent Graduate",
        "personality": ["Organized", "Creative", "Detail-oriented", "Collaborative", "Proactive"],
        "skills": ["Project Management", "Writing", "Social Media", "Analytics", "Microsoft Office", "Communication"],
        "career_path": "Marketing Coordinator → Marketing Specialist → Marketing Manager → Director of Marketing",
        "interview_questions": [
            "How would you keep a campaign on schedule when several teams are involved?",
            "Describe a project where you used data to improve a marketing decision.",
            "How would you market a banking product to a new audience?"
        ]
    },
    {
        "id": 25,
        "name": "Communications Associate",
        "department": "Communications",
        "office": "Middle Office",
        "description": "Supports internal and external communications, drafts newsletters and announcements, assists with executive messaging, and coordinates communication campaigns.",
        "salary": "$55k - $80k",
        "suitable_major": ["Communications", "Public Relations", "Marketing", "Journalism"],
        "suitable_grade": "Recent Graduate",
        "personality": ["Organized", "Adaptable", "Detail-oriented", "Collaborative"],
        "skills": ["Writing", "Editing", "Proofreading", "Project Management", "Verbal Communication"],
        "career_path": "Communications Associate → Communications Specialist → Communications Manager → Director of Corporate Communications",
        "interview_questions": [
            "How would you adapt one announcement for employees, customers, and the media?",
            "Describe your editing process for an executive message.",
            "How do you communicate clearly when information is sensitive or changing?"
        ]
    },
    {
        "id": 26,
        "name": "Digital Marketing Specialist",
        "department": "Marketing and Communications",
        "office": "Middle Office",
        "description": "Manages email marketing, website content, digital advertising, and social media campaigns that promote banking products and services.",
        "salary": "$55k - $80k",
        "suitable_major": ["Marketing", "Communications", "Digital Marketing", "Business Analytics"],
        "suitable_grade": "Recent Graduate",
        "personality": ["Analytical", "Creative", "Adaptable", "User-centric"],
        "skills": ["SEO", "Social Media", "Google Analytics", "Email Marketing", "Data Analysis"],
        "career_path": "Digital Marketing Specialist → Senior Digital Specialist → Digital Marketing Manager → Head of Digital Marketing",
        "interview_questions": [
            "Which metrics would you use to evaluate a digital banking campaign?",
            "How would you improve an email campaign with low engagement?",
            "How do you balance creative messaging with financial-services compliance?"
        ]
    },
    {
        "id": 27,
        "name": "Public Relations Associate",
        "department": "Communications",
        "office": "Middle Office",
        "description": "Supports media relations, press releases, reputation management, research, and public-facing communications for the bank.",
        "salary": "$55k - $85k",
        "suitable_major": ["Public Relations", "Communications", "Journalism", "Marketing"],
        "suitable_grade": "Recent Graduate",
        "personality": ["Confident", "Sociable", "Professional", "Proactive"],
        "skills": ["Media Relations", "Writing", "Research", "Communications Strategy"],
        "career_path": "Public Relations Associate → PR Specialist → Media Relations Manager → Director of Public Relations",
        "interview_questions": [
            "How would you respond to an inaccurate media report about the bank?",
            "What makes a financial-services press release newsworthy?",
            "Describe how you would prepare an executive for a media interview."
        ]
    },
    {
        "id": 28,
        "name": "Social Media and Content Coordinator",
        "department": "Marketing and Communications",
        "office": "Middle Office",
        "description": "Creates social media posts, blogs, customer stories, and campaign content that builds brand awareness and customer engagement.",
        "salary": "$50k - $75k",
        "suitable_major": ["Marketing", "Communications", "Journalism", "Public Relations"],
        "suitable_grade": "Recent Graduate",
        "personality": ["Creative", "Outgoing", "Adaptable", "Detail-oriented"],
        "skills": ["Copywriting", "Content Creation", "Social Media Management", "Analytics"],
        "career_path": "Content Coordinator → Content Specialist → Content or Social Media Manager → Director of Content Strategy",
        "interview_questions": [
            "How would you make a complex banking topic engaging on social media?",
            "Which engagement metrics matter most for financial-services content?",
            "How would you handle a negative customer comment on a public channel?"
        ]
    },
    {
        "id": 29,
        "name": "Financial Education Program Manager",
        "department": "Community Impact / Corporate Social Responsibility",
        "office": "Middle Office",
        "description": "Designs and manages financial-literacy programs for students, consumers, small businesses, and community groups. Coordinates workshops, educational resources, and partnerships that improve financial capability.",
        "salary": "$60k - $115k",
        "suitable_major": ["Education", "Communications", "Finance", "Public Policy", "Business", "Economics"],
        "suitable_grade": "Recent Graduate",
        "personality": ["Creative", "Empathetic", "Organized", "Helpful"],
        "skills": ["Program Management", "Public Speaking", "Curriculum Development", "Community Outreach", "Event Planning"],
        "career_path": "Program Coordinator → Financial Education Program Manager → Community Impact Director → Head of Corporate Social Responsibility",
        "interview_questions": [
            "How would you design a financial-literacy program for first-year college students?",
            "How would you measure whether an education program changed financial behavior?",
            "Describe a time you coordinated partners around a community initiative."
        ]
    },
    {
        "id": 30,
        "name": "CRA Officer",
        "department": "Community Impact / Compliance",
        "office": "Middle Office",
        "description": "Helps the bank meet Community Reinvestment Act requirements by supporting lending, investments, and services for low- and moderate-income communities and by coordinating with nonprofits, regulators, and community organizations.",
        "salary": "$85k - $170k",
        "suitable_major": ["Finance", "Economics", "Public Policy", "Business Administration"],
        "suitable_grade": "Recent Graduate/Junior/Senior",
        "personality": ["Analytical", "Detail-oriented", "Organized", "Collaborative"],
        "skills": ["Regulatory Compliance", "Data Analysis", "Community Development", "Relationship Management", "Reporting"],
        "career_path": "CRA Analyst → CRA Officer → CRA Manager → Director of Community Reinvestment / Chief Compliance Officer",
        "interview_questions": [
            "What is the purpose of the Community Reinvestment Act?",
            "How would you identify unmet credit needs in a community?",
            "How would you prepare for a CRA examination?"
        ]
    },
    {
        "id": 31,
        "name": "Community Engagement Manager",
        "department": "Community Impact / Corporate Social Responsibility",
        "office": "Middle Office",
        "description": "Builds relationships with nonprofits, schools, small businesses, and community groups. Manages volunteer initiatives, sponsorships, financial-education events, outreach programs, and partnerships that strengthen the bank's local impact.",
        "salary": "$65k - $120k",
        "suitable_major": ["Communications", "Public Relations", "Nonprofit Management", "Public Policy", "Sociology", "Business Administration"],
        "suitable_grade": "Recent Graduate",
        "personality": ["Outgoing", "Empathetic", "Organized", "Collaborative", "Adaptable"],
        "skills": ["Partnership Development", "Public Speaking", "Event Planning", "Community Outreach", "Project Management", "Stakeholder Engagement"],
        "career_path": "Community Outreach Coordinator → Community Engagement Manager → Community Impact Director → Head of Corporate Social Responsibility",
        "interview_questions": [
            "How would you build trust with a new community partner?",
            "Describe how you would plan and evaluate a community event.",
            "How would you balance community needs with the bank's strategic goals?"
        ]
    }
]
