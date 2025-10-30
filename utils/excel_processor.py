import pandas as pd
from neo4j import GraphDatabase
import streamlit as st
from typing import Dict, List
import re

class ExcelProcessor:
    def __init__(self):
        self.required_sheets = [
            'EMPLOYEES', 'DESIGNATIONS', 'DEPARTMENTS', 'PROJECTS', 
            'SKILLS', 'PROJECT_ASSIGNMENTS', 'EMPLOYEE_SKILLS', 'REPORTING_STRUCTURE'
        ]
    
    def validate_excel_file(self, uploaded_file) -> bool:
        """Validate that Excel file has all required sheets"""
        try:
            excel_file = pd.ExcelFile(uploaded_file)
            missing_sheets = [sheet for sheet in self.required_sheets if sheet not in excel_file.sheet_names]
            
            if missing_sheets:
                st.error(f"❌ Missing required sheets: {', '.join(missing_sheets)}")
                st.info(f"Available sheets: {', '.join(excel_file.sheet_names)}")
                return False
            
            # Validate each sheet has required columns
            validation_result = self._validate_sheet_columns(uploaded_file)
            return validation_result
            
        except Exception as e:
            st.error(f"❌ Error reading Excel file: {str(e)}")
            return False
    
    def _validate_sheet_columns(self, uploaded_file) -> bool:
        """Validate that each sheet has the required columns"""
        required_columns = {
            'EMPLOYEES': ['emp_id', 'name'],
            'DESIGNATIONS': ['designation_id', 'designation_name'],
            'DEPARTMENTS': ['department_id', 'department_name'],
            'PROJECTS': ['project_id', 'project_name'],
            'SKILLS': ['skill_id', 'skill_name'],
            'PROJECT_ASSIGNMENTS': ['emp_id', 'project_id'],
            'EMPLOYEE_SKILLS': ['emp_id', 'skill_id'],
            'REPORTING_STRUCTURE': ['emp_id', 'manager_id']
        }
        
        all_valid = True
        
        for sheet_name, required_cols in required_columns.items():
            try:
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Sheet '{sheet_name}' missing columns: {', '.join(missing_cols)}")
                    st.info(f"Available columns in {sheet_name}: {list(df.columns)}")
                    all_valid = False
                else:
                    st.success(f"✅ {sheet_name}: All required columns present")
                    
            except Exception as e:
                st.error(f"❌ Error reading sheet {sheet_name}: {str(e)}")
                all_valid = False
        
        return all_valid
    
    def import_excel_to_neo4j(self, uploaded_file, uri: str, username: str, password: str) -> bool:
        """Import all data from Excel to Neo4j with better error handling"""
        try:
            # Validate file first
            if not self.validate_excel_file(uploaded_file):
                return False
            
            # Read all sheets
            employees_df = pd.read_excel(uploaded_file, sheet_name='EMPLOYEES')
            designations_df = pd.read_excel(uploaded_file, sheet_name='DESIGNATIONS')
            departments_df = pd.read_excel(uploaded_file, sheet_name='DEPARTMENTS')
            projects_df = pd.read_excel(uploaded_file, sheet_name='PROJECTS')
            skills_df = pd.read_excel(uploaded_file, sheet_name='SKILLS')
            project_assignments_df = pd.read_excel(uploaded_file, sheet_name='PROJECT_ASSIGNMENTS')
            employee_skills_df = pd.read_excel(uploaded_file, sheet_name='EMPLOYEE_SKILLS')
            reporting_structure_df = pd.read_excel(uploaded_file, sheet_name='REPORTING_STRUCTURE')
            
            # Clean column names (remove spaces, special characters)
            employees_df = self._clean_dataframe(employees_df)
            designations_df = self._clean_dataframe(designations_df)
            departments_df = self._clean_dataframe(departments_df)
            projects_df = self._clean_dataframe(projects_df)
            skills_df = self._clean_dataframe(skills_df)
            project_assignments_df = self._clean_dataframe(project_assignments_df)
            employee_skills_df = self._clean_dataframe(employee_skills_df)
            reporting_structure_df = self._clean_dataframe(reporting_structure_df)
            
            # Connect to Neo4j
            driver = GraphDatabase.driver(uri, auth=(username, password))
            
            with driver.session() as session:
                # Clear existing data
                session.run("MATCH (n) DETACH DELETE n")
                
                # Create constraints
                self._create_constraints(session)
                
                # Import data in proper order with progress tracking
                steps = [
                    ("Designations", lambda: self._import_designations(session, designations_df)),
                    ("Departments", lambda: self._import_departments(session, departments_df)),
                    ("Skills", lambda: self._import_skills(session, skills_df)),
                    ("Projects", lambda: self._import_projects(session, projects_df)),
                    ("Employees", lambda: self._import_employees(session, employees_df)),
                    ("Project Assignments", lambda: self._import_project_assignments(session, project_assignments_df)),
                    ("Employee Skills", lambda: self._import_employee_skills(session, employee_skills_df)),
                    ("Reporting Structure", lambda: self._import_reporting_structure(session, reporting_structure_df))
                ]
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, (step_name, step_func) in enumerate(steps):
                    status_text.text(f"🔄 Importing {step_name}...")
                    try:
                        step_func()
                        progress_bar.progress((i + 1) / len(steps))
                    except Exception as e:
                        st.error(f"❌ Error importing {step_name}: {str(e)}")
                        driver.close()
                        return False
                
                status_text.text("✅ Data import completed!")
                
                # Verify data import
                result = session.run("""
                    MATCH (n)
                    RETURN labels(n)[0] as label, count(n) as count
                    ORDER BY label
                """)
                
                st.success("✅ Database initialized successfully!")
                st.subheader("📊 Import Summary:")
                summary_data = []
                for record in result:
                    label = record['label']
                    count = record['count']
                    summary_data.append(f"**{label}:** {count}")
                    st.write(f"**{label}:** {count}")
            
            driver.close()
            return True
            
        except Exception as e:
            st.error(f"❌ Error initializing database: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            return False
    
    def _clean_dataframe(self, df):
        """Clean dataframe column names and handle missing values"""
        # Clean column names
        df.columns = [re.sub(r'[^a-zA-Z0-9_]', '', col.lower().replace(' ', '_')) for col in df.columns]
        
        # Fill NaN values with empty string for string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('')
        
        return df
    
    def _create_constraints(self, session):
        """Create database constraints with error handling"""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Employee) REQUIRE e.emp_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Skill) REQUIRE s.skill_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Project) REQUIRE p.project_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Department) REQUIRE d.department_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (des:Designation) REQUIRE des.designation_id IS UNIQUE"
        ]
        
        for constraint in constraints:
            try:
                session.run(constraint)
            except Exception as e:
                st.warning(f"Constraint might already exist: {e}")
    
    def _import_designations(self, session, df):
        """Import designation data"""
        for _, row in df.iterrows():
            params = {
                'designation_id': str(row.get('designation_id', '')),
                'name': str(row.get('designation_name', row.get('name', '')))
            }
            session.run("""
                MERGE (d:Designation {designation_id: $designation_id})
                SET d.name = $name
            """, parameters=params)
    
    def _import_departments(self, session, df):
        """Import department data"""
        for _, row in df.iterrows():
            params = {
                'department_id': str(row.get('department_id', '')),
                'name': str(row.get('department_name', row.get('name', '')))
            }
            session.run("""
                MERGE (d:Department {department_id: $department_id})
                SET d.name = $name
            """, parameters=params)
    
    def _import_skills(self, session, df):
        """Import skill data"""
        for _, row in df.iterrows():
            params = {
                'skill_id': str(row.get('skill_id', '')),
                'name': str(row.get('skill_name', row.get('name', '')))
            }
            session.run("""
                MERGE (s:Skill {skill_id: $skill_id})
                SET s.name = $name
            """, parameters=params)
    
    def _import_projects(self, session, df):
        """Import project data"""
        for _, row in df.iterrows():
            params = {
                'project_id': str(row.get('project_id', '')),
                'name': str(row.get('project_name', row.get('name', ''))),
                'status': str(row.get('status', 'Active'))
            }
            session.run("""
                MERGE (p:Project {project_id: $project_id})
                SET p.name = $name, p.status = $status
            """, parameters=params)
    
    def _import_employees(self, session, df):
        """Import employee data with relationships"""
        for _, row in df.iterrows():
            # Prepare parameters with defaults
            params = {
                'emp_id': int(row.get('emp_id', 0)),
                'name': str(row.get('name', '')),
                'gender': str(row.get('gender', '')),
                'date_of_joining': str(row.get('date_of_joining', '1900-01-01')),
                'email': str(row.get('email', '')),
                'phone': str(row.get('phone', '')),
                'location': str(row.get('location', '')),
                'designation_id': str(row.get('designation_id', '')),
                'department_id': str(row.get('department_id', ''))
            }
            
            # Create employee node
            session.run("""
                MERGE (e:Employee {emp_id: $emp_id})
                SET e.name = $name, e.gender = $gender, 
                    e.date_of_joining = date($date_of_joining),
                    e.email = $email, e.phone = $phone,
                    e.location = $location
            """, parameters=params)
            
            # Connect to Designation if available
            if params['designation_id']:
                session.run("""
                    MATCH (e:Employee {emp_id: $emp_id})
                    MATCH (d:Designation {designation_id: $designation_id})
                    MERGE (e)-[r:HAS_DESIGNATION]->(d)
                    SET r.start_date = date($date_of_joining)
                """, parameters=params)
            
            # Connect to Department if available
            if params['department_id']:
                session.run("""
                    MATCH (e:Employee {emp_id: $emp_id})
                    MATCH (d:Department {department_id: $department_id})
                    MERGE (e)-[:BELONGS_TO]->(d)
                """, parameters=params)
    
    def _import_project_assignments(self, session, df):
        """Import project assignments"""
        for _, row in df.iterrows():
            params = {
                'emp_id': int(row.get('emp_id', 0)),
                'project_id': str(row.get('project_id', '')),
                'assignment_type': str(row.get('assignment_type', 'Primary')),
                'start_date': str(row.get('start_date', '1900-01-01'))
            }
            session.run("""
                MATCH (e:Employee {emp_id: $emp_id})
                MATCH (p:Project {project_id: $project_id})
                MERGE (e)-[r:WORKS_ON]->(p)
                SET r.assignment_type = $assignment_type,
                    r.start_date = date($start_date)
            """, parameters=params)
    
    def _import_employee_skills(self, session, df):
        """Import employee skills"""
        for _, row in df.iterrows():
            params = {
                'emp_id': int(row.get('emp_id', 0)),
                'skill_id': str(row.get('skill_id', '')),
                'level': str(row.get('level', 'Intermediate')),
                'date_acquired': str(row.get('date_acquired', '1900-01-01'))
            }
            session.run("""
                MATCH (e:Employee {emp_id: $emp_id})
                MATCH (s:Skill {skill_id: $skill_id})
                MERGE (e)-[r:HAS_SKILL]->(s)
                SET r.level = $level,
                    r.date_acquired = date($date_acquired)
            """, parameters=params)
    
    def _import_reporting_structure(self, session, df):
        """Import reporting structure"""
        for _, row in df.iterrows():
            params = {
                'emp_id': int(row.get('emp_id', 0)),
                'manager_id': int(row.get('manager_id', 0)),
                'report_type': str(row.get('report_type', 'line'))
            }
            session.run("""
                MATCH (e:Employee {emp_id: $emp_id})
                MATCH (m:Employee {emp_id: $manager_id})
                MERGE (e)-[r:REPORTS_TO]->(m)
                SET r.report_type = $report_type
            """, parameters=params)