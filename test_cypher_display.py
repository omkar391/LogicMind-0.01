"""
Test script to verify Cypher query display functionality
"""
import streamlit as st

def test_cypher_display():
    """Test the Cypher query display functionality"""
    st.title("🧪 Cypher Query Display Test")
    
    st.write("This test shows how the Cypher query will be displayed in your chatbot.")
    
    # Sample Cypher query
    sample_query = """
    MATCH (e:Employee)
    WHERE toLower(trim(e.name)) = toLower(trim('John Doe'))
    OPTIONAL MATCH (e)-[:HAS_DESIGNATION]->(d:Designation)
    OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
    OPTIONAL MATCH (e)-[:WORKS_ON]->(p:Project)
    RETURN e,
            collect(DISTINCT d) AS designations,
            collect(DISTINCT s) AS skills,
            collect(DISTINCT p) AS projects
    """
    
    # Sample response
    sample_response = """
    ## 👤 Employee Details Found
    
    I found information about **John Doe** in our employee database:
    
    **Designation:** Senior Software Engineer
    **Skills:** Python, JavaScript, React, Node.js
    **Projects:** E-commerce Platform, Mobile App Development
    
    This employee has 4 skills and is currently working on 2 active projects.
    """
    
    st.markdown("### Sample Chat Response:")
    st.markdown(sample_response)
    
    # Show the Cypher query section
    st.markdown("---")
    st.markdown("""
    <div class="cypher-section">
        <div class="cypher-title">🔍 Executed Cypher Query:</div>
    </div>
    """, unsafe_allow_html=True)
    st.code(sample_query, language="cypher")
    st.markdown("""
    <div class="records-count">📊 Records Found: 1</div>
    """, unsafe_allow_html=True)
    
    # Copy button
    if st.button("📋 Copy Query"):
        st.code(sample_query, language="cypher")
        st.success("Query copied! (You can copy from the code block above)")
    
    st.markdown("---")
    st.info("✅ This is how every response in your chatbot will now show the executed Cypher query!")

if __name__ == "__main__":
    test_cypher_display()
