# 🤖 LogicMind - Employee Intelligence Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.14.0-green.svg)](https://neo4j.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A powerful AI-powered employee intelligence assistant that transforms your organizational data into actionable insights through natural language queries. Built with Streamlit, Neo4j, and advanced AI models.

## ✨ Features

### 🧠 **Intelligent Query Processing**
- **Natural Language Interface**: Ask questions in plain English about your employees, skills, projects, and organizational structure
- **AI-Powered Cypher Generation**: Automatically converts your questions into Neo4j Cypher queries
- **Multi-Model Support**: Works with OpenAI GPT models and Google Gemini
- **Smart Error Handling**: Comprehensive error handling with retry logic and user-friendly messages

### 📊 **Advanced Data Visualization**
- **Interactive Charts**: Beautiful Plotly visualizations for data insights
- **Real-time Analytics**: Live data processing and visualization
- **Export Capabilities**: Copy queries and export results
- **Responsive Design**: Works seamlessly on desktop and mobile

### 🗄️ **Robust Data Management**
- **Excel Integration**: Import employee data directly from Excel files
- **Neo4j Graph Database**: Store and query complex organizational relationships
- **Data Validation**: Automatic data validation and error reporting
- **Connection Testing**: Built-in tools to test database and API connections

### 🎨 **Modern User Interface**
- **Clean Design**: Professional, modern interface with custom CSS styling
- **Chat Interface**: Conversational AI experience with chat history
- **Sidebar Configuration**: Easy access to settings and controls
- **Status Indicators**: Real-time connection and configuration status

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Neo4j database (local or cloud)
- OpenAI API key or Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/LogicMind.git
   cd LogicMind
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## ⚙️ Configuration

### Database Setup

1. **Neo4j Configuration**
   - Set up a Neo4j database (local or cloud)
   - Note your database URI, username, and password
   - Enter these details in the sidebar when running the app

2. **AI Model Setup**
   - Choose between OpenAI or Google Gemini
   - Enter your API key in the sidebar
   - Select your preferred model

### Data Import

1. **Prepare Excel File**
   - Create an Excel file with your employee data
   - Ensure columns include: Name, Department, Skills, Projects, etc.
   - See `Employee_Graph_Transformed.xlsx` for reference

2. **Import Data**
   - Use the "Upload Excel File" option in the sidebar
   - Click "Initialize Database" to import your data
   - Wait for the import summary to confirm success

## 📖 Usage Examples

### Basic Queries
```
"Show me all employees in the Engineering department"
"Who has skills in Python and Machine Learning?"
"What projects is John Smith working on?"
"Find employees with more than 5 years of experience"
```

### Advanced Analytics
```
"Create a skill gap analysis for the Marketing team"
"Show me the organizational hierarchy"
"Which employees have the most diverse skill sets?"
"Find potential mentors for junior developers"
```

### Data Exploration
```
"How many employees are in each department?"
"What are the most common skills across the organization?"
"Show me project distribution by team"
"Which employees are working on multiple projects?"
```

## 🏗️ Project Structure

```
LogicMind/
├── app.py                          # Main Streamlit application
├── requirements.txt                 # Python dependencies
├── config/
│   └── settings.py                 # Configuration settings
├── utils/
│   ├── ai_helper.py               # AI model integration
│   ├── neo4j_helper.py            # Neo4j database operations
│   └── excel_processor.py         # Excel data processing
├── Employee_Graph_Transformed.xlsx # Sample data file
├── ERROR_HANDLING_GUIDE.md        # Error handling documentation
└── README.md                      # This file
```

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Neo4j**: Graph database for relationship data
- **OpenAI/Google Gemini**: AI language models
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive data visualization
- **OpenPyXL**: Excel file processing

### Architecture
- **Frontend**: Streamlit with custom CSS styling
- **Backend**: Python with modular utility classes
- **Database**: Neo4j graph database
- **AI Integration**: Multi-provider AI model support
- **Data Processing**: Excel import and validation pipeline

## 🛠️ Development

### Running Tests
```bash
# Test AI connections
python test_gemini.py
python test_openai.py

# Test database connections
python test_connection.py

# Test error handling
streamlit run test_error_handling.py
```

### Error Handling
The application includes comprehensive error handling for:
- API rate limits and quota exceeded
- Invalid API keys and authentication errors
- Database connection issues
- Network timeouts and connectivity problems
- Data validation and import errors

See `ERROR_HANDLING_GUIDE.md` for detailed information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) for the amazing web framework
- [Neo4j](https://neo4j.com) for the powerful graph database
- [OpenAI](https://openai.com) and [Google](https://ai.google.dev) for AI capabilities
- [Plotly](https://plotly.com) for beautiful visualizations

## 📞 Support

If you encounter any issues or have questions:

1. Check the [ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md)
2. Review the test files for examples
3. Open an issue on GitHub
4. Check your API keys and database connections

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Real-time collaboration features
- [ ] Mobile app development
- [ ] Integration with HR systems
- [ ] Advanced reporting capabilities

---

**Made with ❤️ for better organizational intelligence**
