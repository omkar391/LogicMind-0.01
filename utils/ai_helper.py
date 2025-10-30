import streamlit as st
from typing import Dict, List, Any
import json

class AIHelper:
    def __init__(self, api_key: str, model: str, provider: str = "OpenAI"):
        self.api_key = api_key
        self.model = model
        self.provider = provider
        
        try:
            if provider == "OpenAI":
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
            elif provider == "Google Gemini":
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.client = genai
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            raise Exception(f"Failed to initialize AI client: {str(e)}")
    
    def _get_gemini_model_name(self):
        """Map UI model names to actual Gemini models"""
        model_mapping = {
            "gemini-1.5-pro": "gemini-1.5-pro",
            "gemini-1.5-flash": "gemini-1.5-flash",
            "gemini-2.0-flash-exp": "gemini-2.0-flash-exp",
            "gemini-1.0-pro": "gemini-1.0-pro"
        }
        return model_mapping.get(self.model, "gemini-1.5-flash")
    
    def test_connection(self) -> bool:
        """Test AI API connection"""
        try:
            if self.provider == "OpenAI":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                return response.choices[0].message.content is not None
            elif self.provider == "Google Gemini":
                import google.generativeai as genai
                model_name = self._get_gemini_model_name()
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                return response.text is not None
            return False
        except Exception as e:
            st.error(f"AI connection test failed: {str(e)}")
            return False
    
    def generate_cypher_query(self, question: str) -> Dict[str, Any]:
        """Generate Cypher query using AI only"""
        system_prompt = """
        You are a Neo4j Cypher expert and intelligent assistant. 
        Your task is to convert user questions into optimized, correct, and human-friendly Cypher queries 
        based on the following database schema and rules.

        ---------------------------------------------
        DATABASE SCHEMA:
        Nodes and their key properties:
        - Employee: emp_id, name, gender, date_of_joining, email, phone, location, designation
        - Skill: skill_id, name, category
        - Project: project_id, name, status, start_date, end_date
        - Department: department_id, name
        - Designation: designation_id, name

        Relationships:
        - (:Employee)-[:HAS_SKILL]->(:Skill)
        - (:Employee)-[:WORKS_ON]->(:Project)
        - (:Employee)-[:HAS_DESIGNATION]->(:Designation)
        - (:Employee)-[:REPORTS_TO]->(:Employee)

        ---------------------------------------------
        BEHAVIOR RULES:

        1. **Handle Greetings and Small Talk**
        If the user input is conversational (e.g. "Hi", "Hello", "Hey", "How are you?", "Yes", "No", "OK"),
        do not generate a Cypher query.  
        respond as you would in a friendly chat.

        2. **Case-Insensitive and Trimmed Matching**
        Always use both `toLower()` and `trim()` when comparing text properties like names.
        Example:
        WHERE toLower(trim(e.name)) = toLower(trim('omkar khandagale'))

        3. **Detailed Information Queries**
        When the user asks for details about a specific employee (e.g., “tell me about Omkar Khandagale”),
        generate a single query that collects all relevant details including:
        - Employee’s own properties
        - Their Designation(s)
        - Their Skills
        - Their Projects
        - Their Department(s)

        Example:
        MATCH (e:Employee)
        WHERE toLower(trim(e.name)) = toLower(trim('<employee_name>'))
        OPTIONAL MATCH (e)-[:HAS_DESIGNATION]->(d:Designation)
        OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
        OPTIONAL MATCH (e)-[:WORKS_ON]->(p:Project)
        OPTIONAL MATCH (e)-[:WORKS_IN]->(dep:Department)
        RETURN e,
                collect(DISTINCT d) AS designations,
                collect(DISTINCT s) AS skills,
                collect(DISTINCT p) AS projects,
                collect(DISTINCT dep) AS departments

        4. **Graceful Handling of Out-of-Scope Queries**
        If the question cannot be answered from this schema (e.g. weather, time, etc.), return:
        {
            "response_type": "error",
            "message": "I'm sorry, I cannot answer that question using the current database schema."
        }

        5. **General Query Rules**
        - Ensure all Cypher queries are syntactically valid.
        - Never invent properties or relationships not in the schema above.
        - Keep queries readable and optimized (use `MATCH`, `OPTIONAL MATCH`, and filtering properly).
        - Aggregate related data with `collect(DISTINCT ...)` where appropriate.

        ---------------------------------------------
        OUTPUT FORMAT:
        Always return valid JSON with one of the following formats:

        ✅ For Cypher queries:
        {
        "response_type": "cypher",
        "cypher_query": "MATCH ... RETURN ...",
        "query_type": "list | count | aggregate | search | analysis",
        "entities": ["Employee", "Skill", "Project"],
        "relationships": ["HAS_SKILL", "WORKS_ON"]
        }

        ✅ For greetings or small talk:
        {
        "response_type": "smalltalk",
        "message": "Friendly or clarifying response"
        }

        ✅ For out-of-scope questions:
        {
        "response_type": "error",
        "message": "I'm sorry, I cannot answer that question using the current database schema."
        }

        ---------------------------------------------
        IMPORTANT:
        - Only return JSON — no extra explanations or text.
        - Match names and text attributes in a case- and space-insensitive way.
        - If a relationship does not exist in the database, the query must still run safely with OPTIONAL MATCH.
        """
        
        try:
            if self.provider == "OpenAI":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    temperature=0.1
                )
                result_text = response.choices[0].message.content
                
            elif self.provider == "Google Gemini":
                import google.generativeai as genai
                model_name = self._get_gemini_model_name()
                model = genai.GenerativeModel(model_name)
                
                prompt = f"{system_prompt}\n\nUser Question: {question}\n\nReturn only valid JSON:"
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=1000,
                    )
                )
                result_text = response.text
            
            # Clean the response
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            elif result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            result["success"] = True
            return result
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response from AI: {str(e)}",
                "cypher_query": "",
                "query_type": "error",
                "entities": [],
                "relationships": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"AI query generation failed: {str(e)}",
                "cypher_query": "",
                "query_type": "error",
                "entities": [],
                "relationships": []
            }
    
    def generate_sophisticated_response(self, question: str, data: List[Dict], query_type: str, cypher_query: str) -> Dict[str, Any]:
        """Generate sophisticated, natural responses using AI"""
        
        try:
            # --- Added safe serializer for Neo4j / datetime objects ---
            def default_serializer(obj):
                try:
                    if hasattr(obj, "iso_format"):
                        return obj.iso_format()
                    elif hasattr(obj, "isoformat"):
                        return obj.isoformat()
                    else:
                        return str(obj)
                except Exception:
                    return str(obj)

            # Prepare context for the AI
            data_context = json.dumps(data[:10], indent=2, default=default_serializer) if data else "No data found"
            
            sophisticated_prompt = f"""
            You are an intelligent employee data assistant. Provide natural, conversational responses based on the employee graph database.

            USER QUESTION: "{question}"

            DATABASE RESULTS:
            - Records Found: {len(data)}
            - Sample Data: {data_context}

            Please generate a response that:
            1. Directly answers the user's question in a clear, friendly manner
            2. Use **markdown formatting** for readability:
            - Bold important values (like names, roles, dates, IDs, etc.)
            - Use bullet points or line breaks to separate information
            - Begin with a short, clear answer statement
            3. If the question is outside employee/organization data, gently remind you're focused on the employee graph database
            4. Provide 1–2 relevant follow-up question suggestions
            5. Keep tone friendly and conversational
            6. Mention data comes from the employee database when appropriate

            Return valid JSON with this structure:
            {{
                "answer": "Your formatted markdown response here",
                "data_table": // include the data here only if it helps understanding, otherwise null,
                "suggested_questions": ["suggested question 1", "suggested question 2"]
            }}

            Keep it natural but well-structured and visually clear.
            """
            
            if self.provider == "OpenAI":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a helpful employee data assistant. Provide natural, conversational responses based on the employee graph database. Use readable markdown formatting."
                        },
                        {
                            "role": "user", 
                            "content": sophisticated_prompt
                        }
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                result_text = response.choices[0].message.content
                
            elif self.provider == "Google Gemini":
                import google.generativeai as genai
                model_name = self._get_gemini_model_name()
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content(
                    sophisticated_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=2000,
                    )
                )
                result_text = response.text
            
            # Clean the response
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            elif result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            result["success"] = True
            
            # Ensure suggested_questions exists
            if "suggested_questions" not in result:
                result["suggested_questions"] = self._generate_suggested_questions(question, data, query_type)
                
            return result
            
        except json.JSONDecodeError as e:
            return self._generate_fallback_response(question, data, query_type)
        except Exception as e:
            return {
                "success": False,
                "error": f"AI response generation failed: {str(e)}",
                "answer": "I apologize, but I encountered an error while generating the response. Please try again.",
                "data_table": None,
                "suggested_questions": []
            }


    
    def _generate_suggested_questions(self, question: str, data: List[Dict], query_type: str) -> List[str]:
        """Generate relevant follow-up questions based on the current query"""
        
        suggestions = []
        
        # Common follow-up patterns based on query type
        if "employee" in question.lower() and "skill" not in question.lower():
            suggestions = [
                "What skills does this employee have?",
                "Which projects is this employee working on?"
            ]
        elif "skill" in question.lower():
            suggestions = [
                "Which employees have advanced level in this skill?",
                "What projects require this skill?"
            ]
        elif "project" in question.lower():
            suggestions = [
                "Which departments are involved in this project?",
                "What skills are needed for this project?"
            ]
        elif "department" in question.lower():
            suggestions = [
                "Show me the reporting structure in this department",
                "What projects is this department working on?"
            ]
        else:
            suggestions = [
                "Can you show me the organizational structure?",
                "Which employees have the most skills?"
            ]
        
        return suggestions[:2]  # Return max 2 suggestions
    
    def _generate_fallback_response(self, question: str, data: List[Dict], query_type: str) -> Dict[str, Any]:
        """Generate a natural fallback response when JSON parsing fails"""
        
        if not data:
            answer = f"""
            ## 🤔 No Employee Data Found

            I searched through our employee database but couldn't find any information matching **"{question}"**.

            **💡 Tip:** I'm designed to help you explore the employee graph database, which includes:
            - Employee profiles and details
            - Skills and competencies
            - Project assignments
            - Department structures
            - Reporting relationships

            **Try asking about:**
            - "Show me employees with Python skills"
            - "Which projects are currently active?"
            - "Display the organizational chart"
            - "Find employees in the Engineering department"
            """
            
            return {
                "success": True,
                "answer": answer,
                "data_table": None,
                "suggested_questions": [
                    "Show me all departments",
                    "Which employees have the most skills?"
                ]
            }
        
        # Create a natural response based on data
        count = len(data)
        
        if query_type == "count":
            answer = f"""
            ## 📊 Found {count} Matching Records

            Based on your question about **"{question}"**, I found **{count} results** in the employee database.

            The data shows there are {count} items that match your criteria. Would you like to see more details about any specific records?
            """
        elif query_type == "aggregate":
            answer = f"""
            ## 📈 Analysis Complete

            I've analyzed the employee data and found **{count} aggregated results** for your query about **"{question}"**.

            This gives you a summarized view across the organization. The detailed breakdown is shown below.
            """
        else:
            answer = f"""
            ## 🔍 Here's What I Found

            I found **{count} relevant records** in the employee database for your question about **"{question}"**.

            Here are the details from our organizational data:
            """

        return {
            "success": True,
            "answer": answer,
            "data_table": data if data and len(data) > 0 else None,
            "suggested_questions": self._generate_suggested_questions(question, data, query_type)
        }