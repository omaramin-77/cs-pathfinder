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
    ]
    
}