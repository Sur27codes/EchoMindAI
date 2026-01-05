def get_custom_css():
    """Returns the custom CSS for the application (Reference Standard / Apple Dark)."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        :root {
            /* System Palette (Apple-like Dark Mode) */
            --bg-base: #000000;
            --bg-sidebar: #1C1C1E;
            --bg-card: #1C1C1E;
            --bg-input: #2C2C2E;
            
            --text-primary: #FFFFFF;
            --text-secondary: #8E8E93;
            --text-tertiary: #48484A;
            
            --accent: #0A84FF; /* iOS Blue */
            --success: #30D158;
            --warning: #FFD60A;
            --danger: #FF453A;
            
            --border: 1px solid rgba(255, 255, 255, 0.1);
            --radius-lg: 18px;
            --radius-md: 12px;
            --radius-sm: 8px;
        }

        /* 1. Base Structure */
        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
        }

        /* 2. Sidebar */
        section[data-testid="stSidebar"] {
            background-color: var(--bg-sidebar);
            border-right: var(--border);
        }

        /* 3. Cards & Containers */
        .glass-card {
            background-color: var(--bg-card);
            border: var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.4);
            transition: transform 0.2s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.2);
        }

        /* 4. Typography */
        h1, h2, h3 {
            font-weight: 600 !important;
            letter-spacing: -0.02em;
            color: var(--text-primary) !important;
        }
        
        p, .stMarkdown {
            color: var(--text-secondary);
            font-size: 16px;
            line-height: 1.5;
        }
        
        .hero-title {
            background: linear-gradient(180deg, #FFFFFF 0%, #A1A1AA 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* 5. Inputs */
        .stTextInput input {
            background-color: var(--bg-input) !important;
            border: 1px solid transparent !important;
            border-radius: var(--radius-md) !important;
            padding: 12px 16px !important;
            color: white !important;
            font-size: 16px !important;
        }
        
        .stTextInput input:focus {
            background-color: #3A3A3C !important;
            border-color: var(--accent) !important;
        }

        /* 6. Buttons */
        div.stButton > button {
            background-color: #2C2C2E;
            color: var(--accent);
            border: none;
            border-radius: var(--radius-md);
            padding: 8px 16px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        div.stButton > button:hover {
            background-color: #3A3A3C;
            transform: scale(1.02);
        }
        
        div.stButton > button[kind="primary"] {
            background-color: var(--accent);
            color: white;
            padding: 10px 20px;
            border-radius: var(--radius-lg);
            font-weight: 600;
        }
        
        div.stButton > button[kind="primary"]:hover {
            background-color: #007AFF; /* Darker Blue */
        }

        /* 7. Chat Bubbles (iMessage Style) */
        .stChatMessage {
            background: transparent;
        }
        
        div[data-testid="stChatMessageContent"] {
            padding: 16px 20px !important;
            border-radius: 20px !important;
            box-shadow: none;
        }

        /* User */
        div[data-testid="stChatMessage"][data-testid="stChatMessage-user"] div[data-testid="stChatMessageContent"] {
            background-color: var(--accent);
            color: white;
            border-bottom-right-radius: 4px !important;
        }
        
        /* Assistant */
        div[data-testid="stChatMessage"][data-testid="stChatMessage-assistant"] div[data-testid="stChatMessageContent"] {
            background-color: var(--bg-card);
            color: var(--text-primary);
            border-bottom-left-radius: 4px !important;
        }

        /* Utility */
        #MainMenu, footer, header { visibility: hidden; }
        .stDivider { border-bottom-color: var(--bg-input); }
        
    </style>
    """
