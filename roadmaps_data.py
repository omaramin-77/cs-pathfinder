"""
Roadmap data for all career fields.

Each roadmap is a list of steps with:
- text (short step title)
- description (what to do / learn)
- course (URL to a resource)
"""

ROADMAPS = {
    "AI Engineer": [
        {
            "text": "Learn Python programming fundamentals",
            "description": "Master Python basics including variables, data types, control structures, and functions. Python is the primary language for AI development.",
            "course": "https://www.coursera.org/learn/python"
        },
        {
            "text": "Master NumPy and Pandas for data manipulation",
            "description": "Learn to work with arrays and dataframes efficiently. These libraries are essential for data preprocessing in AI.",
            "course": "https://www.coursera.org/learn/python-for-data-analysis"
        },
        {
            "text": "Study linear algebra and calculus basics",
            "description": "Understand vectors, matrices, derivatives, and gradients. Mathematical foundation is crucial for understanding AI algorithms.",
            "course": "https://www.khanacademy.org/math/linear-algebra"
        },
        {
            "text": "Learn probability and statistics",
            "description": "Master probability distributions, statistical inference, and hypothesis testing. Essential for understanding ML models.",
            "course": "https://www.coursera.org/learn/probability-statistics"
        },
        {
            "text": "Understand machine learning fundamentals",
            "description": "Learn core ML concepts including supervised/unsupervised learning, model evaluation, and bias-variance tradeoff.",
            "course": "https://www.coursera.org/learn/machine-learning"
        },
        {
            "text": "Study supervised learning algorithms",
            "description": "Master regression, classification, decision trees, and ensemble methods. These are the building blocks of ML.",
            "course": "https://www.udacity.com/course/intro-to-machine-learning--ud120"
        },
        {
            "text": "Learn unsupervised learning techniques",
            "description": "Understand clustering, dimensionality reduction, and anomaly detection. Useful for pattern discovery.",
            "course": "https://www.coursera.org/learn/unsupervised-learning"
        },
        {
            "text": "Master neural networks basics",
            "description": "Learn about perceptrons, activation functions, backpropagation, and gradient descent. Foundation of deep learning.",
            "course": "https://www.coursera.org/learn/neural-networks-deep-learning"
        },
        {
            "text": "Study deep learning with TensorFlow/PyTorch",
            "description": "Master modern deep learning frameworks. Build and train complex neural networks efficiently.",
            "course": "https://www.tensorflow.org/tutorials"
        },
        {
            "text": "Learn convolutional neural networks (CNNs)",
            "description": "Understand image processing with deep learning. CNNs are essential for computer vision tasks.",
            "course": "https://www.coursera.org/learn/convolutional-neural-networks"
        },
        {
            "text": "Study recurrent neural networks (RNNs)",
            "description": "Master sequence modeling for time series and text. Learn LSTM and GRU architectures.",
            "course": "https://www.coursera.org/learn/nlp-sequence-models"
        },
        {
            "text": "Master natural language processing (NLP)",
            "description": "Learn text processing, embeddings, transformers, and language models. Build chatbots and text analyzers.",
            "course": "https://www.coursera.org/specializations/natural-language-processing"
        },
        {
            "text": "Learn computer vision techniques",
            "description": "Master image classification, object detection, and segmentation. Apply AI to visual data.",
            "course": "https://www.coursera.org/learn/computer-vision-basics"
        },
        {
            "text": "Study reinforcement learning",
            "description": "Understand agents, rewards, Q-learning, and policy gradients. Build AI that learns from interaction.",
            "course": "https://www.coursera.org/specializations/reinforcement-learning"
        },
        {
            "text": "Practice with Kaggle competitions",
            "description": "Apply your skills to real-world problems. Learn from the community and improve your techniques.",
            "course": "https://www.kaggle.com/learn"
        },
        {
            "text": "Build end-to-end AI projects",
            "description": "Create complete AI applications from data collection to deployment. Build your portfolio.",
            "course": "https://www.youtube.com/results?search_query=end+to+end+ai+projects"
        },
        {
            "text": "Learn model deployment and MLOps",
            "description": "Master Docker, APIs, model serving, and monitoring. Deploy AI models to production.",
            "course": "https://www.coursera.org/learn/machine-learning-engineering-for-production-mlops"
        },
        {
            "text": "Study AI ethics and responsible AI",
            "description": "Understand bias, fairness, privacy, and ethical implications. Build responsible AI systems.",
            "course": "https://www.coursera.org/learn/ai-for-everyone"
        },
        {
            "text": "Master cloud AI services (AWS/GCP/Azure)",
            "description": "Learn to use cloud platforms for AI. Scale your models and reduce infrastructure complexity.",
            "course": "https://www.coursera.org/learn/aws-machine-learning"
        },
        {
            "text": "Build a portfolio of AI applications",
            "description": "Showcase your skills with diverse projects. Create a GitHub portfolio and write about your work.",
            "course": "https://github.com/topics/artificial-intelligence"
        }
    ],
    "ML Engineer": [
        {
            "text": "Master Python and software engineering basics",
            "description": "Strong programming skills are essential for building production ML systems. Learn clean code practices.",
            "course": "https://www.coursera.org/learn/python-programming"
        },
        {
            "text": "Learn data structures and algorithms",
            "description": "Understand efficient data handling and algorithm complexity. Critical for optimizing ML pipelines.",
            "course": "https://www.coursera.org/learn/algorithms-part1"
        },
        {
            "text": "Study statistics and probability theory",
            "description": "Deep statistical knowledge helps you understand model behavior and make informed decisions.",
            "course": "https://www.coursera.org/learn/statistical-inference"
        },
        {
            "text": "Master SQL and database management",
            "description": "Learn to query and manage large datasets efficiently. Essential for data engineering tasks.",
            "course": "https://www.coursera.org/learn/sql-for-data-science"
        },
        {
            "text": "Learn data preprocessing and feature engineering",
            "description": "Transform raw data into meaningful features. This often determines model success.",
            "course": "https://www.coursera.org/learn/feature-engineering"
        },
        {
            "text": "Study machine learning algorithms in depth",
            "description": "Understand the math and intuition behind algorithms. Know when to use each approach.",
            "course": "https://www.coursera.org/specializations/machine-learning-introduction"
        },
        {
            "text": "Master scikit-learn library",
            "description": "Learn the most popular ML library for Python. Build and evaluate models efficiently.",
            "course": "https://scikit-learn.org/stable/tutorial/index.html"
        },
        {
            "text": "Learn model evaluation and validation",
            "description": "Master cross-validation, metrics, and testing strategies. Ensure your models generalize well.",
            "course": "https://www.coursera.org/learn/ml-foundations"
        },
        {
            "text": "Study ensemble methods and boosting",
            "description": "Combine multiple models for better performance. Learn XGBoost, LightGBM, and CatBoost.",
            "course": "https://www.coursera.org/learn/competitive-data-science"
        },
        {
            "text": "Master hyperparameter tuning",
            "description": "Optimize model performance through systematic parameter search. Learn grid search and Bayesian optimization.",
            "course": "https://www.youtube.com/results?search_query=hyperparameter+tuning+tutorial"
        },
        {
            "text": "Learn MLOps principles and practices",
            "description": "Understand the full ML lifecycle from development to production. Build reliable ML systems.",
            "course": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops"
        },
        {
            "text": "Study model versioning with MLflow/DVC",
            "description": "Track experiments, models, and datasets. Ensure reproducibility in ML projects.",
            "course": "https://mlflow.org/docs/latest/tutorials-and-examples/index.html"
        },
        {
            "text": "Master Docker and containerization",
            "description": "Package ML applications with all dependencies. Ensure consistent environments across deployments.",
            "course": "https://www.docker.com/101-tutorial"
        },
        {
            "text": "Learn Kubernetes for ML deployment",
            "description": "Orchestrate containerized ML applications at scale. Manage resources efficiently.",
            "course": "https://kubernetes.io/docs/tutorials/"
        },
        {
            "text": "Study CI/CD pipelines for ML",
            "description": "Automate testing, training, and deployment. Build robust ML workflows.",
            "course": "https://www.coursera.org/learn/continuous-integration"
        },
        {
            "text": "Master cloud platforms (AWS SageMaker, GCP AI)",
            "description": "Deploy and scale ML models using cloud services. Reduce infrastructure management.",
            "course": "https://www.coursera.org/learn/aws-machine-learning"
        },
        {
            "text": "Learn model monitoring and maintenance",
            "description": "Track model performance in production. Detect and handle model drift.",
            "course": "https://www.evidentlyai.com/blog/ml-monitoring-tutorial"
        },
        {
            "text": "Study A/B testing for ML models",
            "description": "Evaluate model improvements scientifically. Make data-driven deployment decisions.",
            "course": "https://www.udacity.com/course/ab-testing--ud257"
        },
        {
            "text": "Master distributed training techniques",
            "description": "Train large models across multiple machines. Handle big data efficiently.",
            "course": "https://www.tensorflow.org/guide/distributed_training"
        },
        {
            "text": "Build production-ready ML systems",
            "description": "Combine all skills to create robust, scalable ML applications. Focus on reliability and maintainability.",
            "course": "https://github.com/eugeneyan/applied-ml"
        }
    ],
    "Data Scientist": [
        {
            "text": "Learn Python or R programming",
            "description": "Master a primary language for data analysis. Python is versatile, R excels in statistics.",
            "course": "https://www.datacamp.com/courses/intro-to-python-for-data-science"
        },
        {
            "text": "Master statistics and probability",
            "description": "Understand distributions, hypothesis testing, and statistical inference. Foundation of data science.",
            "course": "https://www.coursera.org/learn/statistical-inference"
        },
        {
            "text": "Study data visualization with Matplotlib/Seaborn",
            "description": "Learn to create compelling visualizations. Communicate insights effectively through charts.",
            "course": "https://www.datacamp.com/courses/introduction-to-data-visualization-with-matplotlib"
        },
        {
            "text": "Learn SQL for data querying",
            "description": "Extract and manipulate data from databases. Essential skill for accessing business data.",
            "course": "https://www.coursera.org/learn/sql-for-data-science"
        },
        {
            "text": "Master Pandas for data manipulation",
            "description": "Transform, clean, and analyze data efficiently. The workhorse of data science.",
            "course": "https://www.coursera.org/learn/python-for-data-analysis"
        },
        {
            "text": "Study exploratory data analysis (EDA)",
            "description": "Discover patterns, anomalies, and relationships in data. Guide your analysis strategy.",
            "course": "https://www.coursera.org/learn/exploratory-data-analysis"
        },
        {
            "text": "Learn hypothesis testing",
            "description": "Make statistical inferences from data. Validate assumptions and test theories.",
            "course": "https://www.khanacademy.org/math/statistics-probability/significance-tests-one-sample"
        },
        {
            "text": "Master regression analysis",
            "description": "Model relationships between variables. Predict continuous outcomes.",
            "course": "https://www.coursera.org/learn/regression-models"
        },
        {
            "text": "Study classification algorithms",
            "description": "Predict categorical outcomes. Learn logistic regression, decision trees, and more.",
            "course": "https://www.coursera.org/learn/classification-vector-spaces-in-nlp"
        },
        {
            "text": "Learn clustering techniques",
            "description": "Group similar data points. Discover hidden patterns without labels.",
            "course": "https://www.coursera.org/learn/cluster-analysis"
        },
        {
            "text": "Master time series analysis",
            "description": "Analyze temporal data and make forecasts. Essential for business metrics.",
            "course": "https://www.coursera.org/learn/practical-time-series-analysis"
        },
        {
            "text": "Study A/B testing methodology",
            "description": "Design and analyze experiments. Make data-driven business decisions.",
            "course": "https://www.udacity.com/course/ab-testing--ud257"
        },
        {
            "text": "Learn data storytelling skills",
            "description": "Present insights compellingly. Bridge the gap between data and decision-makers.",
            "course": "https://www.coursera.org/learn/data-driven-storytelling"
        },
        {
            "text": "Master Tableau or Power BI",
            "description": "Create interactive dashboards. Enable self-service analytics for stakeholders.",
            "course": "https://www.tableau.com/learn/training"
        },
        {
            "text": "Study big data tools (Spark, Hadoop)",
            "description": "Process large-scale datasets. Handle data that doesn't fit in memory.",
            "course": "https://www.coursera.org/learn/big-data-introduction"
        },
        {
            "text": "Learn feature engineering techniques",
            "description": "Create meaningful variables from raw data. Improve model performance.",
            "course": "https://www.coursera.org/learn/feature-engineering"
        },
        {
            "text": "Master machine learning pipelines",
            "description": "Build end-to-end ML workflows. Automate data processing and modeling.",
            "course": "https://www.coursera.org/learn/machine-learning-pipelines"
        },
        {
            "text": "Study business intelligence concepts",
            "description": "Understand business metrics and KPIs. Align analysis with business goals.",
            "course": "https://www.coursera.org/learn/business-intelligence-tools"
        },
        {
            "text": "Learn to communicate insights effectively",
            "description": "Present findings to non-technical audiences. Drive action with your analysis.",
            "course": "https://www.coursera.org/learn/data-visualization-storytelling"
        },
        {
            "text": "Build a portfolio of data projects",
            "description": "Showcase your analytical skills. Demonstrate impact through real projects.",
            "course": "https://www.dataquest.io/blog/build-a-data-science-portfolio/"
        }
    ],
    "Web Developer": [
        {
            "text": "Learn HTML5 fundamentals",
            "description": "Master the structure of web pages. HTML is the foundation of all websites.",
            "course": "https://www.freecodecamp.org/learn/responsive-web-design/"
        },
        {
            "text": "Master CSS3 and responsive design",
            "description": "Style websites beautifully. Make them work on all devices and screen sizes.",
            "course": "https://www.freecodecamp.org/learn/responsive-web-design/"
        },
        {
            "text": "Study JavaScript basics",
            "description": "Add interactivity to websites. JavaScript powers modern web applications.",
            "course": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"
        },
        {
            "text": "Learn DOM manipulation",
            "description": "Dynamically update web pages. Create interactive user experiences.",
            "course": "https://www.youtube.com/results?search_query=javascript+dom+manipulation+tutorial"
        },
        {
            "text": "Master ES6+ features",
            "description": "Use modern JavaScript syntax. Write cleaner, more efficient code.",
            "course": "https://www.udemy.com/course/javascript-es6-tutorial/"
        },
        {
            "text": "Study Git and version control",
            "description": "Track code changes and collaborate. Essential for all developers.",
            "course": "https://www.coursera.org/learn/version-control"
        },
        {
            "text": "Learn a CSS framework (Bootstrap/Tailwind)",
            "description": "Build responsive layouts quickly. Use pre-built components effectively.",
            "course": "https://getbootstrap.com/docs/5.3/getting-started/introduction/"
        },
        {
            "text": "Master React.js or Vue.js",
            "description": "Build modern single-page applications. Create reusable UI components.",
            "course": "https://react.dev/learn"
        },
        {
            "text": "Study state management (Redux/Vuex)",
            "description": "Manage complex application state. Keep your app data organized.",
            "course": "https://redux.js.org/tutorials/essentials/part-1-overview-concepts"
        },
        {
            "text": "Learn Node.js and Express",
            "description": "Build server-side applications with JavaScript. Create APIs and web servers.",
            "course": "https://www.freecodecamp.org/learn/back-end-development-and-apis/"
        },
        {
            "text": "Master RESTful API design",
            "description": "Create well-structured APIs. Enable communication between frontend and backend.",
            "course": "https://www.coursera.org/learn/rest-api"
        },
        {
            "text": "Study databases (SQL and NoSQL)",
            "description": "Store and retrieve data efficiently. Learn PostgreSQL and MongoDB.",
            "course": "https://www.coursera.org/learn/intro-sql"
        },
        {
            "text": "Learn authentication and authorization",
            "description": "Secure your applications. Implement user login and access control.",
            "course": "https://www.youtube.com/results?search_query=authentication+authorization+tutorial"
        },
        {
            "text": "Master testing (Jest, Cypress)",
            "description": "Write automated tests. Ensure code quality and catch bugs early.",
            "course": "https://jestjs.io/docs/getting-started"
        },
        {
            "text": "Study web security best practices",
            "description": "Protect against common vulnerabilities. Learn about XSS, CSRF, and SQL injection.",
            "course": "https://www.coursera.org/learn/web-security-fundamentals"
        },
        {
            "text": "Learn deployment and hosting",
            "description": "Deploy applications to production. Use platforms like Vercel, Netlify, or AWS.",
            "course": "https://www.netlify.com/blog/2016/09/29/a-step-by-step-guide-deploying-on-netlify/"
        },
        {
            "text": "Master performance optimization",
            "description": "Make websites fast. Optimize loading times and user experience.",
            "course": "https://web.dev/learn/performance/"
        },
        {
            "text": "Study Progressive Web Apps (PWA)",
            "description": "Build apps that work offline. Provide native-like experiences on the web.",
            "course": "https://web.dev/learn/pwa/"
        },
        {
            "text": "Learn GraphQL",
            "description": "Query APIs more efficiently. Fetch exactly the data you need.",
            "course": "https://www.howtographql.com/"
        },
        {
            "text": "Build full-stack projects for portfolio",
            "description": "Showcase your skills with complete applications. Demonstrate end-to-end development.",
            "course": "https://www.freecodecamp.org/news/full-stack-project-ideas/"
        }
    ],
    "Cybersecurity Analyst": [
        {
            "text": "Learn networking fundamentals (TCP/IP, DNS, HTTP)",
            "description": "Understand how data flows across networks. Foundation of cybersecurity.",
            "course": "https://www.coursera.org/learn/computer-networking"
        },
        {
            "text": "Master operating systems (Linux and Windows)",
            "description": "Know system internals and command-line tools. Essential for security analysis.",
            "course": "https://www.coursera.org/learn/linux-fundamentals"
        },
        {
            "text": "Study information security basics",
            "description": "Learn CIA triad, security principles, and threat landscape. Build security mindset.",
            "course": "https://www.coursera.org/learn/intro-cyber-security"
        },
        {
            "text": "Learn cryptography fundamentals",
            "description": "Understand encryption, hashing, and digital signatures. Protect data confidentiality.",
            "course": "https://www.coursera.org/learn/crypto"
        },
        {
            "text": "Master network security concepts",
            "description": "Secure network infrastructure. Learn firewalls, VPNs, and IDS/IPS.",
            "course": "https://www.coursera.org/learn/network-security"
        },
        {
            "text": "Study common vulnerabilities (OWASP Top 10)",
            "description": "Know the most critical web application risks. Learn to identify and mitigate them.",
            "course": "https://owasp.org/www-project-top-ten/"
        },
        {
            "text": "Learn penetration testing basics",
            "description": "Think like an attacker. Identify vulnerabilities before malicious actors do.",
            "course": "https://www.coursera.org/learn/penetration-testing"
        },
        {
            "text": "Master security tools (Nmap, Wireshark, Metasploit)",
            "description": "Use industry-standard tools for security testing. Analyze network traffic and vulnerabilities.",
            "course": "https://www.youtube.com/results?search_query=nmap+wireshark+metasploit+tutorial"
        },
        {
            "text": "Study web application security",
            "description": "Secure web apps against attacks. Understand injection, XSS, and authentication flaws.",
            "course": "https://portswigger.net/web-security"
        },
        {
            "text": "Learn incident response procedures",
            "description": "Handle security breaches effectively. Contain, investigate, and recover from incidents.",
            "course": "https://www.coursera.org/learn/incident-response"
        },
        {
            "text": "Master security information and event management (SIEM)",
            "description": "Monitor and analyze security events. Detect threats in real-time.",
            "course": "https://www.splunk.com/en_us/training.html"
        },
        {
            "text": "Study malware analysis basics",
            "description": "Understand how malware works. Analyze and reverse engineer malicious software.",
            "course": "https://www.coursera.org/learn/malware-analysis"
        },
        {
            "text": "Learn threat intelligence",
            "description": "Stay informed about emerging threats. Use intelligence to improve defenses.",
            "course": "https://www.cybrary.it/course/threat-intelligence/"
        },
        {
            "text": "Master security frameworks (NIST, ISO 27001)",
            "description": "Implement structured security programs. Follow industry best practices.",
            "course": "https://www.coursera.org/learn/nist-cybersecurity-framework"
        },
        {
            "text": "Study cloud security (AWS, Azure, GCP)",
            "description": "Secure cloud infrastructure and applications. Understand shared responsibility model.",
            "course": "https://www.coursera.org/learn/cloud-security-basics"
        },
        {
            "text": "Learn security automation and scripting",
            "description": "Automate security tasks with Python. Improve efficiency and consistency.",
            "course": "https://www.coursera.org/learn/python-for-cybersecurity"
        },
        {
            "text": "Master risk assessment methodologies",
            "description": "Identify and prioritize security risks. Make informed security decisions.",
            "course": "https://www.coursera.org/learn/risk-management"
        },
        {
            "text": "Study compliance and regulations (GDPR, HIPAA)",
            "description": "Understand legal requirements. Ensure organizational compliance.",
            "course": "https://www.coursera.org/learn/data-privacy-fundamentals"
        },
        {
            "text": "Get certified (Security+, CEH, CISSP)",
            "description": "Validate your skills with industry certifications. Boost career prospects.",
            "course": "https://www.comptia.org/certifications/security"
        },
        {
            "text": "Build a home lab for practice",
            "description": "Practice skills in a safe environment. Set up vulnerable machines and practice attacks.",
            "course": "https://www.youtube.com/results?search_query=cybersecurity+home+lab+setup"
        }
    ],
    "Cloud Engineer": [
        {
            "text": "Learn networking fundamentals",
            "description": "Understand IP addressing, subnets, routing, and DNS. Essential for cloud architecture.",
            "course": "https://www.coursera.org/learn/computer-networking"
        },
        {
            "text": "Master Linux system administration",
            "description": "Manage Linux servers efficiently. Most cloud workloads run on Linux.",
            "course": "https://www.coursera.org/learn/linux-fundamentals"
        },
        {
            "text": "Study virtualization concepts",
            "description": "Understand VMs, hypervisors, and resource allocation. Foundation of cloud computing.",
            "course": "https://www.coursera.org/learn/cloud-computing-basics"
        },
        {
            "text": "Learn cloud computing basics",
            "description": "Understand IaaS, PaaS, SaaS models. Know cloud service types and benefits.",
            "course": "https://www.coursera.org/learn/introduction-to-cloud"
        },
        {
            "text": "Master AWS/Azure/GCP fundamentals",
            "description": "Learn a major cloud platform. Understand core services and architecture.",
            "course": "https://aws.amazon.com/training/"
        },
        {
            "text": "Study Infrastructure as Code (IaC)",
            "description": "Manage infrastructure through code. Ensure consistency and repeatability.",
            "course": "https://www.coursera.org/learn/infrastructure-as-code"
        },
        {
            "text": "Learn Terraform or CloudFormation",
            "description": "Automate infrastructure provisioning. Define resources declaratively.",
            "course": "https://learn.hashicorp.com/terraform"
        },
        {
            "text": "Master Docker containerization",
            "description": "Package applications with dependencies. Ensure consistent environments.",
            "course": "https://www.docker.com/101-tutorial"
        },
        {
            "text": "Study Kubernetes orchestration",
            "description": "Manage containerized applications at scale. Automate deployment and scaling.",
            "course": "https://kubernetes.io/docs/tutorials/"
        },
        {
            "text": "Learn CI/CD pipelines",
            "description": "Automate build, test, and deployment. Enable rapid, reliable releases.",
            "course": "https://www.coursera.org/learn/continuous-integration"
        },
        {
            "text": "Master monitoring and logging (CloudWatch, Prometheus)",
            "description": "Track system health and performance. Troubleshoot issues quickly.",
            "course": "https://www.coursera.org/learn/cloud-monitoring"
        },
        {
            "text": "Study cloud security best practices",
            "description": "Secure cloud resources and data. Implement least privilege and defense in depth.",
            "course": "https://www.coursera.org/learn/cloud-security-basics"
        },
        {
            "text": "Learn serverless computing (Lambda, Cloud Functions)",
            "description": "Build event-driven applications. Pay only for what you use.",
            "course": "https://aws.amazon.com/lambda/getting-started/"
        },
        {
            "text": "Master cloud storage solutions",
            "description": "Choose appropriate storage services. Optimize for performance and cost.",
            "course": "https://www.coursera.org/learn/cloud-storage"
        },
        {
            "text": "Study cloud databases (RDS, DynamoDB, Cosmos DB)",
            "description": "Deploy and manage databases in the cloud. Choose SQL vs NoSQL appropriately.",
            "course": "https://www.coursera.org/learn/cloud-database-fundamentals"
        },
        {
            "text": "Learn cost optimization strategies",
            "description": "Reduce cloud spending. Right-size resources and use reserved instances.",
            "course": "https://aws.amazon.com/aws-cost-management/"
        },
        {
            "text": "Master high availability and disaster recovery",
            "description": "Design resilient systems. Ensure business continuity.",
            "course": "https://www.coursera.org/learn/disaster-recovery"
        },
        {
            "text": "Study microservices architecture",
            "description": "Build scalable, maintainable applications. Decompose monoliths into services.",
            "course": "https://www.coursera.org/learn/microservices"
        },
        {
            "text": "Get cloud certifications (AWS/Azure/GCP)",
            "description": "Validate your cloud expertise. Boost career opportunities.",
            "course": "https://aws.amazon.com/certification/"
        },
        {
            "text": "Build cloud-native applications",
            "description": "Design applications for the cloud. Leverage cloud services effectively.",
            "course": "https://www.coursera.org/learn/cloud-native-development"
        }
    ]
    
}