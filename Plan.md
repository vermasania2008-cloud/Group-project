🎓 Academic Search Engine

A centralized academic platform for searching, analyzing, and managing educational resources.Academic Search Engine is a Python-based academic productivity application built
with Streamlit. It brings academic search, question-paper analysis, AI assistance, activity history, and daily achievement tracking into a single platform.

📌 Problem & Solution

🔴 Problems

Problem	Description

📚 Scattered Resources :                   	Academic content is often spread across multiple PDFs, notes, websites, and applications.
📄 Manual Question Paper Analysis 	        Students have to manually check multiple previous-year papers to find repeated and important questions.
🔍 Difficult Information Retrieval	        Finding a specific academic topic or relevant information can take considerable time.
🤖 Lack of Centralized AI Assistance      	Students often need to switch between different AI tools while studying.
🕒 No Activity Tracking                   	Students may not have a simple way to review their academic searches and previous activities.
📊 Limited Academic Insights               	Raw academic activity does not provide an easy overview of study patterns.
🎯 Inconsistent Study Tracking	            Students may find it difficult to monitor their daily academic engagement.

🟢 Proposed Solution

Academic Search Engine addresses these challenges by providing multiple academic functionalities through a single platform.

Problem	Proposed Solution

📚 Scattered resources                    	Provide a centralized academic platform for accessing and processing resources.
📄 Manual paper analysis	                  Use PyPDF, Regex, TF-IDF, and Scikit-learn to analyze question papers and identify important questions.
🔍 Difficult information retrieval         	Provide academic search and text-based analysis capabilities.
🤖 Separate AI tools                      	Integrate an AI Assistant through an API/LLM within the application.
🕒 No activity tracking                    	Store searches and activities using SQLite.
📊 Limited insights	                        Use Pandas and Matplotlib to process and visualize activity data.
🎯 Inconsistent tracking	                  Provide Today's Achievement to summarize daily academic activity.

🛠️ Tech Stack

Technology	Role

Python	                                    Application development and core logic
Streamlit                                 	Web application framework and UI
Pandas                                    	Data manipulation and analysis
Matplotlib	                                Data visualization
Scikit-learn                              	Machine learning and text analysis
TF-IDF	                                    Text representation and relevance analysis
PyPDF	PDF                                   Text extraction
Regex	                                      Text cleaning and pattern-based extraction
SQLite	                                    Local database and activity storage
API	                                        External/AI service integration

🧠 How It Works

Question Paper Analyzer Workflow

Upload                     -        User uploads a PDF/text file with questions.

Preprocessing              –        Text is cleaned using regex and normalized.

Vectorization              –        TF-IDF converts questions into numerical vectors.

Similarity Calculation     –        Cosine similarity ranks questions against a knowledge base.

Display Results            –        Top matches shown with priority and match percentage.


AI Assistant Workflow

Query Input            – User types a question in the search bar.

Processing             – Query is preprocessed and matched against indexed academic content.

Response Generation    – LLM or rule-based system generates an answer.

Logging                – Query and answer are saved to History with timestamp.

👥 Team
Team Leader  : Samridhi Verma

Team Members : Tarun Soni
               Palak

📄 License
This project is open-source and available for educational purposes.

💡 Academic Search Engine

   Search smarter. Analyze better. Learn consistently.
