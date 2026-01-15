"""
Seed knowledge base with comprehensive career advice content.
Run this script to populate the vector store with starter content.
"""
import asyncio
import sys
sys.path.insert(0, '.')

from core.config import get_settings
from core.rag.vector_store import initialize_vector_store, add_documents

# Resume Tips
RESUME_CONTENT = [
    {
        "content": """Resume Formatting Best Practices:
- Keep your resume to 1 page for entry-level, 2 pages max for experienced professionals
- Use a clean, professional font like Arial, Calibri, or Helvetica (10-12pt)
- Include clear section headers: Summary, Experience, Education, Skills
- Use bullet points, not paragraphs
- Ensure consistent formatting throughout
- Save as PDF unless specifically asked for Word format
- Include your name and contact info at the top: email, phone, LinkedIn, portfolio/GitHub if relevant""",
        "metadata": {"category": "resume", "subcategory": "formatting", "title": "Resume Formatting Guide"}
    },
    {
        "content": """Writing Powerful Resume Bullet Points:
- Start each bullet with a strong action verb: Led, Developed, Implemented, Achieved, Optimized
- Quantify results whenever possible: "Increased sales by 25%", "Reduced load time by 40%"
- Use the XYZ formula: Accomplished [X] as measured by [Y] by doing [Z]
- Focus on achievements, not just responsibilities
- Tailor bullets to match the job description keywords
- Keep bullets concise: 1-2 lines maximum
- Include 3-5 bullets per role, prioritizing most impactful achievements""",
        "metadata": {"category": "resume", "subcategory": "content", "title": "Writing Resume Bullets"}
    },
    {
        "content": """Resume Summary and Objective Statements:
- Use a Summary for experienced professionals (3+ years experience)
- Use an Objective for entry-level or career changers
- Keep it to 2-3 sentences maximum
- Summary example: "Results-driven software engineer with 5 years of experience building scalable web applications. Expertise in React, Node.js, and AWS. Proven track record of leading teams and delivering projects 20% ahead of schedule."
- Objective example: "Recent computer science graduate seeking a software engineering role where I can apply my skills in Python and machine learning while contributing to innovative products."
- Customize for each application by including relevant keywords""",
        "metadata": {"category": "resume", "subcategory": "summary", "title": "Resume Summary Writing"}
    },
    {
        "content": """Skills Section Best Practices:
- Divide into categories: Technical Skills, Tools, Soft Skills
- List technologies in order of proficiency
- Only include skills you can confidently discuss in an interview
- For tech roles, include: Programming languages, Frameworks, Databases, Cloud platforms, Tools
- Match skills to job description requirements
- Avoid outdated technologies unless specifically required
- Consider a skills matrix showing proficiency levels for senior roles
- Keep soft skills brief: "Team Leadership, Communication, Problem Solving" """,
        "metadata": {"category": "resume", "subcategory": "skills", "title": "Skills Section Guide"}
    },
    {
        "content": """Resume for Fresh Graduates with No Experience:
- Lead with Education section if you have strong academic achievements
- Include relevant coursework and academic projects
- Highlight internships, even if unpaid
- Include part-time jobs demonstrating transferable skills
- Feature personal projects, hackathons, or open-source contributions
- Add volunteer work showing leadership or relevant skills
- Include certifications and online courses
- List relevant extracurricular activities and student organizations
- Create a portfolio website to showcase projects""",
        "metadata": {"category": "resume", "subcategory": "fresher", "title": "Fresher Resume Tips"}
    },
    {
        "content": """ATS (Applicant Tracking System) Optimization:
- Use standard section headers that ATS can recognize
- Avoid tables, graphics, headers/footers, and text boxes
- Use standard bullet points (•) not special characters
- Include keywords from the job description naturally
- Don't use acronyms alone—write "Search Engine Optimization (SEO)"
- Use standard fonts, not decorative ones
- Submit in .docx or .pdf format as specified
- Test your resume through free ATS checkers online
- Keep formatting simple and avoid columns""",
        "metadata": {"category": "resume", "subcategory": "ats", "title": "ATS Optimization Guide"}
    },
    {
        "content": """Cover Letter Writing Tips:
- Address it to a specific person when possible ("Dear [Hiring Manager Name]")
- Opening paragraph: Hook + why this company + what position
- Middle paragraph: 2-3 achievements that match job requirements with examples
- Closing paragraph: Enthusiasm + call to action + thank you
- Keep it to one page (250-400 words)
- Match the tone to company culture
- Don't repeat your resume—tell a story
- Proofread multiple times for errors""",
        "metadata": {"category": "resume", "subcategory": "cover_letter", "title": "Cover Letter Tips"}
    },
]

# Interview Preparation
INTERVIEW_CONTENT = [
    {
        "content": """The STAR Method for Behavioral Interviews:
S - Situation: Set the context for your story (1-2 sentences)
T - Task: Describe your responsibility in that situation
A - Action: Explain the specific steps you took (the most important part, be detailed)
R - Result: Share the outcomes and what you learned

Example Question: "Tell me about a time you handled conflict"
Example Answer:
- Situation: "During a team project, two developers disagreed on the tech stack"
- Task: "As team lead, I needed to resolve the conflict without losing momentum"
- Action: "I scheduled a 1:1 with each person, understood their concerns, then facilitated a group discussion focusing on project requirements not personal preferences"
- Result: "We reached consensus in 30 minutes, shipped on time, and established a decision framework for future technical choices" """,
        "metadata": {"category": "interview", "subcategory": "behavioral", "title": "STAR Method Guide"}
    },
    {
        "content": """Most Common Interview Questions and How to Answer:
1. "Tell me about yourself" - 2-minute professional summary: background, key achievements, why you're here
2. "Why do you want to work here?" - Research company values, mission, recent news; connect to your goals
3. "What's your greatest strength?" - Choose relevant skill, give example with results
4. "What's your greatest weakness?" - Be genuine, show self-awareness, explain how you're improving
5. "Where do you see yourself in 5 years?" - Show ambition aligned with role, don't say "your job"
6. "Why should we hire you?" - Match your skills to job requirements, add unique value
7. "Tell me about a challenge you overcame" - Use STAR method, show problem-solving
8. "Do you have questions for us?" - Always say yes! Ask about team, growth, success metrics""",
        "metadata": {"category": "interview", "subcategory": "common_questions", "title": "Common Interview Questions"}
    },
    {
        "content": """Technical Interview Preparation:
For Software Engineering:
- Practice coding problems daily (LeetCode, HackerRank) - focus on Easy/Medium
- Master data structures: Arrays, Strings, Hash Maps, Trees, Graphs
- Know basic algorithms: Sorting, Searching, BFS/DFS, Dynamic Programming basics
- Practice thinking aloud while coding
- Review system design basics for senior roles

During the Interview:
1. Clarify the problem before coding
2. Discuss your approach before implementing
3. Write clean, readable code
4. Talk through your thought process
5. Test your code with examples
6. Discuss time and space complexity
7. Ask about edge cases

After coding:
- Walk through your solution
- Explain trade-offs in your approach
- Suggest optimizations if time permits""",
        "metadata": {"category": "interview", "subcategory": "technical", "title": "Technical Interview Prep"}
    },
    {
        "content": """Questions to Ask the Interviewer:
About the Role:
- "What does a typical day look like for this position?"
- "What are the biggest challenges facing the team right now?"
- "How is success measured in this role?"
- "What are the opportunities for growth?"

About the Team:
- "Can you tell me about the team I'd be working with?"
- "How does the team collaborate on projects?"
- "What's the onboarding process like?"

About the Company:
- "What do you enjoy most about working here?"
- "How would you describe the company culture?"
- "What are the company's plans for growth?"

Avoid asking:
- Salary/benefits (save for HR discussions)
- Vacation days (too early)
- Anything easily found on the website""",
        "metadata": {"category": "interview", "subcategory": "questions_to_ask", "title": "Questions for Interviewer"}
    },
    {
        "content": """Video Interview Best Practices:
Before the Interview:
- Test your camera, microphone, and internet connection
- Choose a quiet, well-lit location (natural light facing you)
- Use a plain, professional background
- Close unnecessary browser tabs and applications
- Have a copy of your resume and notes nearby
- Dress professionally from head to toe (you might need to stand)

During the Interview:
- Look at the camera, not the screen, to make "eye contact"
- Sit up straight and lean slightly forward
- Smile and use hand gestures naturally
- Speak clearly and at a moderate pace
- Wait a beat before answering (accounts for lag)
- Mute yourself when not speaking in group calls

Technical Issues:
- Have a backup plan (phone number to call)
- If audio fails, offer to switch to phone
- Stay calm if there are glitches - it happens to everyone""",
        "metadata": {"category": "interview", "subcategory": "video", "title": "Video Interview Tips"}
    },
    {
        "content": """Salary Negotiation Tips:
Before the Negotiation:
- Research market rates on Glassdoor, LinkedIn, Levels.fyi
- Know your minimum acceptable salary
- Consider total compensation: base, bonus, equity, benefits

During Negotiation:
- Never give a number first if possible
- If asked, provide a range (make the bottom your target)
- Express enthusiasm for the role first
- Use silence strategically after the offer
- Ask for time to consider the offer

Key Phrases:
- "Based on my research and experience, I was expecting something in the range of..."
- "Is there flexibility in the base salary?"
- "What would it take to get to [target number]?"
- "Can we discuss the sign-on bonus or equity to bridge the gap?"

Don't forget to negotiate:
- Start date, remote work options, signing bonus, equity, PTO, professional development budget""",
        "metadata": {"category": "interview", "subcategory": "salary", "title": "Salary Negotiation"}
    },
    {
        "content": """Following Up After an Interview:
Same Day (within 24 hours):
- Send a personalized thank-you email to each interviewer
- Reference something specific you discussed
- Reiterate your interest and fit for the role

Email Template:
"Dear [Name],

Thank you for taking the time to meet with me today about the [Position] role. I enjoyed learning about [specific topic discussed] and was particularly excited by [something about the role/company].

Our conversation reinforced my enthusiasm for this opportunity. I believe my experience in [relevant skill] would allow me to contribute meaningfully to [specific goal/project mentioned].

Please don't hesitate to reach out if you need any additional information. I look forward to hearing from you.

Best regards,
[Your Name]"

If you haven't heard back after one week, send a polite follow-up email.""",
        "metadata": {"category": "interview", "subcategory": "follow_up", "title": "Interview Follow-Up"}
    },
]

# Job Search Strategy
JOB_SEARCH_CONTENT = [
    {
        "content": """Effective Job Search Strategies:
1. Quality Over Quantity - Apply to fewer jobs but customize each application
2. Use Multiple Channels:
   - LinkedIn Jobs (optimize your profile for search)
   - Company career pages (often have exclusive listings)
   - Indeed, Glassdoor for broad searches
   - Industry-specific job boards
   - Referrals (highest success rate!)
   
3. Network Strategically:
   - Attend virtual and in-person industry events
   - Join professional communities and Slack groups
   - Do informational interviews
   - Engage meaningfully on LinkedIn
   
4. Track Your Applications:
   - Use a spreadsheet with: Company, Role, Date Applied, Status, Follow-up Date
   - Note which strategies are working
   - Follow up after 1 week if no response""",
        "metadata": {"category": "job_search", "subcategory": "strategy", "title": "Job Search Strategy"}
    },
    {
        "content": """LinkedIn Optimization for Job Seekers:
Profile Essentials:
- Professional headshot (increases profile views by 14x)
- Headline: Job Title + Key Skills + What You're Looking For
  Example: "Software Engineer | React, Node.js | Open to New Opportunities"
- About section: Your story, achievements, and what you're seeking
- Experience: Match your resume, add rich media if possible
- Skills: List 50 skills, prioritize most relevant ones
- Recommendations: Ask colleagues and managers

Job Search Features:
- Set "Open to Work" (visible to recruiters or everyone)
- Use job alerts with specific keywords
- Research companies before applying
- Connect with recruiters in your industry
- Engage with content (like, comment) to increase visibility

Networking on LinkedIn:
- Personalize every connection request
- Send thank-you notes after interviews
- Share industry insights and celebrate others' wins""",
        "metadata": {"category": "job_search", "subcategory": "linkedin", "title": "LinkedIn Optimization"}
    },
    {
        "content": """Networking for Introverts:
You don't have to be outgoing to network effectively:

1. Start Online:
   - Engage with posts before reaching out
   - Join LinkedIn groups in your industry
   - Participate in Twitter/X tech communities
   - Contribute to open source projects

2. Do Informational Interviews:
   - Reach out with specific, genuine questions
   - Keep it to 20-30 minutes
   - Ask about their career path, not for job leads
   - Always send a thank-you note

3. Attend Small Events:
   - Prefer workshops over large networking events
   - Arrive early when crowds are smaller
   - Prepare 2-3 conversation starters
   - Set a small goal: "I'll talk to 3 people"

4. Follow Up is Key:
   - Connect on LinkedIn within 24 hours
   - Reference something specific you discussed
   - Share relevant articles to stay in touch
   - Keep relationships warm with occasional check-ins""",
        "metadata": {"category": "job_search", "subcategory": "networking", "title": "Networking for Introverts"}
    },
    {
        "content": """Remote Job Search Tips:
Finding Remote Opportunities:
- Remote-specific job boards: FlexJobs, We Work Remotely, Remote.co, Remotive
- Filter for "Remote" on LinkedIn, Indeed
- Look for "distributed" or "remote-first" companies
- Check company careers pages directly

Making Your Application Stand Out:
- Highlight previous remote work experience
- Emphasize self-management and communication skills
- Mention experience with remote tools: Slack, Zoom, Notion, Asana
- Show you have a dedicated workspace

Red Flags to Watch For:
- "Remote" but requires you to be in a specific timezone
- Vague job descriptions or unrealistic expectations
- No clear communication about equipment/expenses
- Unusually low pay for the role

Interview Tips for Remote Roles:
- Ask about communication practices and meeting schedules
- Inquire about team culture and how they stay connected
- Discuss expectations for response times and availability""",
        "metadata": {"category": "job_search", "subcategory": "remote", "title": "Remote Job Search"}
    },
    {
        "content": """Applying to FAANG/MAANG Companies:
Understanding the Process:
- Application → Online Assessment → Phone Screen → On-site (Virtual) → Team Match → Offer
- Timeline: 4-8 weeks typically

Preparation Strategy:
1. Resume: Focus on impact, numbers, and leadership
2. Online Assessment: Practice coding challenges (2-3 LeetCode per day)
3. Technical Interviews: System design, coding, behavioral
4. Behavioral: Use STAR method with Amazon Leadership Principles style

Key Tips:
- Apply through referrals when possible (2x higher callback rate)
- Research company-specific interview patterns
- Practice with mock interviews (Pramp, interviewing.io)
- Know the product inside out

After Rejection:
- You can reapply after 6-12 months typically
- Ask for feedback if possible
- Use the experience to improve
- Many successful engineers took 2-3 attempts""",
        "metadata": {"category": "job_search", "subcategory": "faang", "title": "FAANG Interview Guide"}
    },
]

# Career Development
CAREER_CONTENT = [
    {
        "content": """Software Engineering Career Roadmap:
Junior Developer (0-2 years):
- Master one programming language deeply
- Learn Git, command line, and development workflows
- Build projects and contribute to open source
- Focus on code quality and best practices

Mid-Level Developer (2-5 years):
- Lead small features end-to-end
- Mentor junior developers
- Learn system design fundamentals
- Develop expertise in 1-2 technologies

Senior Developer (5-8 years):
- Own major system components
- Make architectural decisions
- Influence team processes
- Balance technical and leadership skills

Staff/Principal Engineer (8+ years):
- Set technical direction for the org
- Solve cross-team problems
- Mentor other senior engineers
- Impact beyond your immediate team

Alternative Paths:
- Engineering Manager: People and project leadership
- Technical Lead: Hands-on with team leadership
- Architect: System design and technical vision
- Specialist: Deep expertise in one area (ML, Security, etc.)""",
        "metadata": {"category": "career", "subcategory": "swe_roadmap", "title": "Software Engineering Career Path"}
    },
    {
        "content": """Skills to Learn for Tech Careers in 2024-2025:
High-Demand Technical Skills:
1. AI/ML: Python, TensorFlow, prompt engineering, LLM applications
2. Cloud: AWS, Azure, or GCP certifications
3. Full-Stack: React/Next.js + Node.js/Python + PostgreSQL
4. DevOps: Docker, Kubernetes, CI/CD, Infrastructure as Code
5. Data Engineering: SQL, Spark, Airflow, dbt

Emerging Technologies:
- Generative AI and LLMs
- WebAssembly
- Edge computing
- Rust programming
- Web3 (selective opportunities)

Essential Soft Skills:
- Communication: Clear writing and speaking
- Problem-solving: Breaking down complex problems
- Collaboration: Working effectively in teams
- Adaptability: Learning new technologies quickly
- Time management: Prioritizing and meeting deadlines

Learning Approach:
- Focus on fundamentals first
- Build real projects
- Learn in public (blog, share progress)
- Find a mentor or community""",
        "metadata": {"category": "career", "subcategory": "skills", "title": "In-Demand Tech Skills"}
    },
    {
        "content": """Career Transition to Tech:
Assess Your Starting Point:
- Identify transferable skills from current career
- Research which tech roles align with your strengths
- Be realistic about the time and effort required

Popular Entry Points:
- Technical Writing: Uses communication skills
- QA/Testing: Lower barrier, good stepping stone
- Project Management: Leverage leadership experience
- Product Management: Good for business backgrounds
- Data Analysis: Bridge role for analytics experience
- UX Design: Creative + tech combination

Learning Path:
1. Start with free resources (freeCodeCamp, The Odin Project)
2. Build a portfolio with 3-5 projects
3. Consider a bootcamp for structured learning and networking
4. Get certifications relevant to target role
5. Start applying while still learning

Breaking In:
- Leverage your network from previous career
- Look for roles bridging your experience and tech
- Consider contract or freelance work to build experience
- Be open to startups and smaller companies
- Highlight transferable skills on resume and interviews""",
        "metadata": {"category": "career", "subcategory": "transition", "title": "Career Transition Guide"}
    },
    {
        "content": """Building a Portfolio that Gets Interviews:
What to Include:
- 3-5 quality projects (not 15 mediocre ones)
- At least one complex, full-stack project
- Projects relevant to your target roles
- Live demos or screenshots
- Clean, commented code on GitHub

Project Ideas That Stand Out:
- Clone of a real product with improvements
- Tool that solves a real problem you've had
- Open-source contribution
- Project with real users (even if small)

Portfolio Website Tips:
- Keep design clean and professional
- Mobile responsive
- Fast loading
- Clear project descriptions with tech stack
- Include contact info and resume download

For Each Project, Show:
- Problem you solved
- Technologies used and why
- Challenges you faced and overcame
- Results or learnings
- Link to live demo and source code""",
        "metadata": {"category": "career", "subcategory": "portfolio", "title": "Portfolio Building Guide"}
    },
    {
        "content": """Freelancing and Side Hustles in Tech:
Getting Started:
- Platforms: Upwork, Fiverr, Toptal (for experienced), Freelancer
- Start with lower rates to build reviews
- Niche down: "React developer for startups" beats "developer"
- Create detailed profiles with portfolio samples

Finding Clients:
- Cold outreach on LinkedIn
- Network in online communities
- Create content (YouTube, blog, Twitter)
- Referrals from happy clients

Pricing Strategies:
- Hourly: Good for ongoing work, harder to scale
- Project-based: Better margins, clearer scope
- Retainer: Monthly fee for ongoing availability

Tips for Success:
- Communicate clearly and often
- Set expectations upfront
- Use contracts for every project
- Build systems and templates to work faster
- Save 30% for taxes""",
        "metadata": {"category": "career", "subcategory": "freelancing", "title": "Freelancing Guide"}
    },
    {
        "content": """Dealing with Job Rejection:
Mindset Shifts:
- Rejection is normal (even experienced candidates face it)
- It's about fit, not your worth
- Each rejection is practice for the right opportunity
- Most successful people faced many rejections

Practical Steps After Rejection:
1. Allow yourself to feel disappointed briefly
2. Ask for feedback if possible
3. Review your performance honestly
4. Identify one thing to improve for next time
5. Update your tracking spreadsheet
6. Keep applying—momentum is key

When to Adjust Your Strategy:
- No callbacks after 50+ applications: Revise resume
- Failing first-round interviews: Practice answers
- Failing final rounds: Work on specific skills
- No responses from networking: Improve your pitch

Self-Care:
- Job searching is stressful—take breaks
- Connect with supportive friends/family
- Maintain hobbies and exercise
- Celebrate small wins along the way""",
        "metadata": {"category": "career", "subcategory": "rejection", "title": "Handling Job Rejection"}
    },
    {
        "content": """First 90 Days in a New Job:
First Week:
- Meet your team and key stakeholders
- Understand the codebase/product at a high level
- Set up your development environment
- Identify your onboarding buddy/mentor

First 30 Days:
- Complete onboarding tasks and training
- Have 1:1s with team members to understand their work
- Ship a small win (bug fix, small feature)
- Understand team processes and norms
- Ask lots of questions—it's expected!

30-60 Days:
- Take on more substantial tasks
- Start contributing to team discussions
- Build relationships across teams
- Identify areas where you can add value
- Start documenting things you learn

60-90 Days:
- Own a small feature or project
- Propose improvements based on fresh perspective
- Have career conversation with manager
- Set goals for the next quarter
- Show impact and document your wins

Key Tips:
- Listen more than you talk early on
- Don't try to change everything on day one
- Build trust before pushing ideas
- Find a mentor inside and outside your team""",
        "metadata": {"category": "career", "subcategory": "first_90_days", "title": "First 90 Days Guide"}
    },
]


async def seed_knowledge_base():
    """Seed the knowledge base with comprehensive content."""
    print("🌱 Seeding InnoFolio knowledge base...")
    
    # Initialize vector store
    await initialize_vector_store()
    
    # Combine all content
    all_content = RESUME_CONTENT + INTERVIEW_CONTENT + JOB_SEARCH_CONTENT + CAREER_CONTENT
    
    # Prepare documents and metadata
    documents = [item["content"] for item in all_content]
    metadatas = [item["metadata"] for item in all_content]
    ids = [f"{item['metadata']['category']}_{item['metadata']['subcategory']}_{i}" 
           for i, item in enumerate(all_content)]
    
    # Add to vector store
    await add_documents(documents, metadatas, ids)
    
    print(f"✅ Successfully seeded {len(documents)} documents!")
    print("\nCategories added:")
    print(f"  📄 Resume tips: {len(RESUME_CONTENT)}")
    print(f"  🎯 Interview prep: {len(INTERVIEW_CONTENT)}")
    print(f"  💼 Job search: {len(JOB_SEARCH_CONTENT)}")
    print(f"  🗺️ Career development: {len(CAREER_CONTENT)}")
    print(f"\n📚 Total documents: {len(all_content)}")


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
