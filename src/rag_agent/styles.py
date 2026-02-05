def get_custom_css():
    """Returns the premium custom CSS for EchoMindAI."""
    return """
    </style>
    
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script>
    (function() {
        console.log("Initializing Neon Rain Game...");
        
        // --- 1. SPECIAL EFFECTS: Confetti Trigger ---
        window.triggerCelebration = function() {
            if (window.confetti) {
                confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 }, colors: ['#FF61D2', '#00EAFF', '#7928CA'] });
            }
        }

        // --- 2. GAME: Falling Neon Bars ---
        const canvas = document.createElement('canvas');
        canvas.id = 'dynamic-wallpaper';
        Object.assign(canvas.style, {
            position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
            zIndex: 0, pointerEvents: 'none' // Click-through, but mousemove works on document
        });
        const existing = document.getElementById('dynamic-wallpaper');
        if (existing) existing.remove();
        document.body.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        let width, height;
        let bars = [];
        let score = 0;
        const mouse = { x: -100, y: -100 };
        
        const COLORS = ['#c764ec', '#4a36b1', '#8c53ff', '#00EAFF', '#FF61D2'];
        
        class Bar {
            constructor() {
                this.w = Math.random() * 5 + 2; // Thin neon bars
                this.h = Math.random() * 80 + 40; // Long
                this.x = Math.random() * width;
                this.y = -this.h - (Math.random() * 500); // Start above screen
                this.speed = Math.random() * 2 + 1.5;
                this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
                this.collected = false;
            }
            
            update() {
                this.y += this.speed;
                
                // Collection Logic (Mouse Collision)
                // Simple box collision
                if (mouse.x > this.x - 20 && mouse.x < this.x + this.w + 20 &&
                    mouse.y > this.y && mouse.y < this.y + this.h) {
                    this.collected = true;
                    spawnSparks(this.x, this.y + this.h/2, this.color);
                    score++;
                }
                
                // Reset if off bottom
                if (this.y > height) {
                    this.y = -this.h;
                    this.x = Math.random() * width;
                    this.speed = Math.random() * 2 + 1.5;
                }
            }
            
            draw() {
                if (this.collected) return;
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 15;
                ctx.shadowColor = this.color;
                ctx.fillRect(this.x, this.y, this.w, this.h);
                ctx.shadowBlur = 0;
            }
        }
        
        let sparks = [];
        class Spark {
            constructor(x, y, color) {
                this.x = x; this.y = y;
                this.vx = (Math.random()-0.5)*10;
                this.vy = (Math.random()-0.5)*10;
                this.life = 1.0;
                this.color = color;
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.life -= 0.05;
            }
            draw() {
                ctx.globalAlpha = this.life;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, 2, 0, Math.PI*2);
                ctx.fill();
                ctx.globalAlpha = 1.0;
            }
        }
        
        function spawnSparks(x, y, color) {
            for(let i=0; i<8; i++) sparks.push(new Spark(x, y, color));
        }

        function init() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
            bars = [];
            for (let i = 0; i < 60; i++) bars.push(new Bar());
        }
        
        function animate() {
            ctx.clearRect(0, 0, width, height);
            
            // Draw Bars
            bars.forEach(bar => {
                if (!bar.collected) {
                    bar.update();
                    bar.draw();
                } else {
                    // Respawn collected bar immediately at top
                    bar.y = -bar.h - (Math.random() * 200);
                    bar.x = Math.random() * width;
                    bar.collected = false;
                }
            });
            
            // Draw Sparks
            for (let i = sparks.length - 1; i >= 0; i--) {
                let s = sparks[i];
                s.update();
                s.draw();
                if (s.life <= 0) sparks.splice(i, 1);
            }
            
            requestAnimationFrame(animate);
        }
        
        window.addEventListener('resize', init);
        document.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
        init();
        animate();

        // --- 3. UI DYNAMICS: Parallax (Kept) ---
        document.addEventListener('mousemove', (e) => {
            const cards = document.querySelectorAll('.glass-card, .stButton button');
            const x = (window.innerWidth - e.pageX * 2) / 100;
            const y = (window.innerHeight - e.pageY * 2) / 100;
            cards.forEach(card => card.style.transform = `perspective(1000px) rotateX(${y * 0.05}deg) rotateY(${x * 0.05}deg) translateY(-2px)`);
        });

    })();
    </script>
    
    <style>
        /* Animation States */
        .hidden-state {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease-out, transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
        }
        
        .visible {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            /* DeepAI Inspired Violet Palette */
            --bg-base: #101010;
            --bg-sidebar: rgba(16, 16, 16, 0.85);
            --bg-card: rgba(42, 40, 47, 0.4); /* Dark Violet Tint */
            --bg-input: rgba(255, 255, 255, 0.08);
            
            --text-primary: #FFFFFF;
            --text-secondary: #E0E0E0;
            
            --border-glass: 1px solid rgba(199, 100, 236, 0.2); /* Purple Border */
            --shadow-glass: 0 8px 32px 0 rgba(74, 54, 177, 0.2);
            
            --radius-lg: 24px;
            --radius-md: 16px;
        }
        
        /* Interactive Neon Aura */
        body {
            background-color: var(--bg-base); /* Moved BG here */
            overflow-x: hidden; /* Prevent horizontal scroll */
        }

        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            /* Colorful moving orb tracking mouse */
            background: radial-gradient(
                600px circle at var(--x, 50vw) var(--y, 50vh), 
                rgba(255, 60, 255, 0.1),
                rgba(92, 36, 255, 0.1),
                transparent 50%
            );
            /* Add a second layer for depth */
            box-shadow: inset 0 0 100px rgba(0,0,0,0.5);
            z-index: -1;
            pointer-events: none;
            mix-blend-mode: screen; /* Helps colors pop without washing out black */
        }       
        
        /* Fun floating particles animation (simulated via background) */
        @keyframes float-bg {
             0% { background-position: 0% 0%; }
             50% { background-position: 20% 50%; }
             100% { background-position: 0% 0%; }
        }

        .stApp {
            background-color: transparent !important; /* CRITICAL FIX */
            background: transparent !important;
            /* Deep Dark Space Background */
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(20, 0, 40, 0.3) 0%, transparent 25%), 
                radial-gradient(circle at 85% 30%, rgba(40, 0, 60, 0.2) 0%, transparent 25%);
            background-size: 100% 100%;
            
            font-family: 'Outfit', sans-serif;
            color: var(--text-primary);
        }
        
        /* NUCLEAR OPTION: Force all inner containers to be transparent */
        .stApp > header, .stApp > div, .stApp .main, .stApp .block-container {
            background: transparent !important;
            background-color: transparent !important;
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.01em;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        code {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* --- MATH & TEXT VISIBILITY FIX --- */
        /* Force high contrast for all math elements */
        .katex, .katex-display, .katex-html {
            color: #FFFFFF !important;
            opacity: 1 !important;
            text-shadow: 0 0 1px rgba(0,0,0,0.8); /* Sharpness against dark bg */
            font-weight: 500 !important;
        }
        
        /* Ensure normal text doesn't fade */
        .stMarkdown p, .stMarkdown li, .stMarkdown span {
            color: #FFFFFF !important;
            text-rendering: optimizeLegibility;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: var(--bg-sidebar);
            border-right: var(--border-glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }

        /* Glass Cards */
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: var(--border-glass);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-glass);
            margin-bottom: 20px;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.5);
            background: rgba(255, 255, 255, 0.08); /* Light up on hover */
        }

        /* Hero Text Gradient */
        .gradient-text {
            background: linear-gradient(135deg, #FF61D2 0%, #FE9090 50%, #5C24FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: inline-block;
            filter: drop-shadow(0 0 10px rgba(255, 97, 210, 0.3));
        }

        /* --- ANIMATIONS & FUN --- */
        
        /* 1. Neural Pulse Loader (Replaces Spinner) */
        .neural-loader {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: radial-gradient(circle, #00EAFF, #5C24FF);
            box-shadow: 0 0 20px #00EAFF;
            animation: pulse-ring 1.5s infinite;
        }
        
        @keyframes pulse-ring {
            0% { transform: scale(0.8); box-shadow: 0 0 0 0 rgba(0, 234, 255, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 20px rgba(0, 234, 255, 0); }
            100% { transform: scale(0.8); box-shadow: 0 0 0 0 rgba(0, 234, 255, 0); }
        }

        /* 2. Typewriter Effect */
        .typewriter h1 {
            overflow: hidden; 
            border-right: .15em solid #FF61D2; 
            white-space: nowrap; 
            margin: 0 auto; 
            letter-spacing: .15em; 
            animation: 
              typing 3.5s steps(40, end),
              blink-caret .75s step-end infinite;
        }

        @keyframes typing {
          from { width: 0 }
          to { width: 100% }
        }

        @keyframes blink-caret {
          from, to { border-color: transparent }
          50% { border-color: #FF61D2; }
        }
        
        /* Chat Bubbles */
        .stChatMessage { 
            background: transparent; 
            animation: fadeIn 0.5s ease-out forwards;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* User Bubble */
        div[data-testid="stChatMessage"][data-testid="stChatMessage-user"] div[data-testid="stChatMessageContent"] {
            background: linear-gradient(135deg, rgba(92, 36, 255, 0.4) 0%, rgba(255, 59, 255, 0.2) 100%);
            border: var(--border-glass);
            backdrop-filter: blur(12px);
            border-radius: 20px 20px 4px 20px !important;
            padding: 16px 24px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        /* Assistant Bubble - Glass Dark with Glow */
        div[data-testid="stChatMessage"][data-testid="stChatMessage-assistant"] div[data-testid="stChatMessageContent"] {
            background: linear-gradient(145deg, rgba(20, 20, 30, 0.9), rgba(10, 10, 15, 0.95));
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-left: 2px solid #00EAFF; /* Electric Blue Accent */
            border-radius: 4px 20px 20px 20px !important;
            padding: 20px 28px !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 20px rgba(0, 234, 255, 0.05); /* Subtle glow */
            font-weight: 400; /* Ensure readability */
        }
        
        /* Ensure all nested text elements are white */
        div[data-testid="stChatMessage"] p, 
        div[data-testid="stChatMessage"] li {
            color: #FFFFFF !important;
        }

        /* Buttons */
        div.stButton > button {
            background: rgba(255, 255, 255, 0.08);
            border: var(--border-glass);
            color: var(--text-primary);
            border-radius: var(--radius-md);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }
        
        /* --- PREMIUM GLASSMORPHISM BUTTONS --- */
        div.stButton > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.05); /* Ultra-sheer glass */
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        div.stButton > button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            color: #fff;
        }
        
        div.stButton > button:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: white;
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 97, 210, 0.4);
        }
        
        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #FF61D2, #5C24FF);
            border: none;
            color: #fff;
            font-weight: 600;
        }

        /* Gradient Text Animation for Title */
        h1 span {
            background: linear-gradient(to right, #FF61D2, #FE9090, #5C24FF, #00D4FF);
            background-size: 300% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 5s linear infinite;
        }

        @keyframes shine {
            to {
                background-position: 200% center;
            }
        }

        /* --- IMMERSIVE CHAT BAR (AGGRESSIVE REMOVAL) --- */
        
        /* 1. Hide Header/Footer fully */
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; display: none !important; }
        
        /* 2. Target the exact bottom container Streamlit uses */
        .stBottom, div[data-testid="stBottom"] {
            background: rgba(20, 20, 20, 0.7) !important; /* Semi-transparent dark */
            backdrop-filter: blur(20px) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
            box-shadow: 0 -10px 30px rgba(0,0,0,0.5) !important;
            padding-top: 15px !important;
            padding-bottom: 20px !important;
        }
        
        /* 3. Target any children wrapper divs that might hold color */
        /* 3. Target any children wrapper divs that might hold color */
        .stBottom > div {
             background: transparent !important;
        }
        
        /* 4. Force the main app container to span full height and show background */
        /* 4. Force the main app container to span full height and show background */
        .stApp {
            background-color: transparent !important; /* Let body bg show through */
        }
        
        /* 5. The Chat Input container itself - The "White Box" culprit */
        /* Aggressively target the wrapper to remove the faint white edge */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] * {
             background-color: transparent !important;
             background: transparent !important;
             box-shadow: none !important;
             border: none !important;
             outline: none !important;
        }
        
        /* Restore the specific input styling that we DO want */
        .stChatInput textarea {
            background-color: rgba(20, 20, 20, 0.8) !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
            color: #fff !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important; /* Subtle border */
        }
        
        /* Placeholder color */
        .stChatInput textarea::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
        }
        
        
        /* Remove the default red border on focus and replace with subtle white glow */
        .stChatInput textarea:focus,
        .stChatInput textarea:focus-visible {
            border-color: rgba(255, 255, 255, 0.4) !important;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.1) !important;
            outline: none !important;
        }

        /* Target the specific red-border element Streamlit adds (internal classes) */
        div[data-testid="stChatInput"] > div {
            border-color: transparent !important;
            box-shadow: none !important;
            outline: none !important;
        }
        
        /* Specific override for the active container */
        .st-emotion-cache-1h9usn1, .st-emotion-cache-12fmw14, .st-emotion-cache-1dp5vir {
            border-color: transparent !important;
            box-shadow: none !important;
        }


        /* Remove default streamlit rounded styling from the wrapper */
        [data-testid="stChatInput"] {
            border-radius: 0 !important;
        }
        
        /* Just the Input Box itself should have style */
        .stChatInputContainer {
             padding-bottom: 20px;
        }
        
        /* PREMIUM GLASS PILL INPUT */
        .stChatInput textarea {
            background-color: rgba(20, 20, 20, 0.8) !important; /* Dark solid base */
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 30px !important;
            color: white !important;
            caret-color: #FF61D2 !important;
            padding: 12px 20px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        }
        
        .stChatInput textarea:focus {
            border-color: #FF61D2 !important;
            box-shadow: 0 0 15px rgba(255, 97, 210, 0.3) !important;
            background-color: rgba(0, 0, 0, 0.9) !important;
        }
        
        .stChatInput textarea::placeholder {
            color: rgba(200, 200, 200, 0.6) !important;
        }
        
        /* Submit Button */
        .stChatInput button {
            color: #FF61D2 !important;
        }
        
        /* Generic Input Fields */
        .stTextInput input {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            color: white !important;
            border-radius: 12px !important; 
        }

        /* Fun Glow Animation */
        @keyframes subtle-float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        .hero-title {
            animation: subtle-float 3s ease-in-out infinite;
        }

        /* File Uploader Fix */
        [data-testid="stFileUploader"] {
            background-color: rgba(255,255,255,0.02);
            border: 1px dashed rgba(255,255,255,0.4);
            border-radius: var(--radius-md);
            padding: 15px;
        }
        
        [data-testid="stFileUploader"] section { background: transparent !important; }
        [data-testid="stFileUploader"] div[data-testid="stFileUploaderFile"] { background: rgba(255,255,255,0.1) !important; }

        /* Hide Streamlit Elements */
        #MainMenu, footer, .stDeployButton { display: none; }

    /* --- Premium Table Styles --- */
    table {
        width: 100%;
        border-collapse: separate; 
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        margin: 20px 0;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    th {
        background: rgba(255, 255, 255, 0.08);
        color: #FF61D2 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 12px 16px;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        color: #EEEEEE;
        vertical-align: middle;
    }
    
    td img {
        border-radius: 8px;
        max-height: 100px;
        width: auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    
    td img:hover {
        transform: scale(1.1);
        z-index: 10;
    }

    tr:last-child td {
        border-bottom: none;
    }
    
    tr:hover td {
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Ensure code blocks don't ruin tables if they accidentally appear */
    table code {
        background: rgba(0,0,0,0.3);
        color: #FF61D2;
        padding: 2px 6px;
        border-radius: 4px;
    }

    /* --- PRODUCT CARDS (GRID LAYOUT) --- */
    .product-grid, section.product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .product-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        flex-direction: column;
        backdrop-filter: blur(10px);
    }

    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(92, 36, 255, 0.3);
        border-color: rgba(255, 97, 210, 0.5);
        z-index: 10;
        background: rgba(255, 255, 255, 0.08);
    }

    .product-card-img-container {
        width: 100%;
        height: 180px;
        background: rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .product-card img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }
    
    .product-card:hover img {
        transform: scale(1.05);
    }

    .product-card-content {
        padding: 16px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }

    .product-card h3 {
        margin: 0 0 8px 0;
        font-size: 1.1rem;
        font-weight: 600;
        line-height: 1.4;
        color: white;
    }

    .product-card .price {
        font-size: 1.25rem;
        color: #FF61D2;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .product-card .rating {
        color: #FFD700;
        font-size: 0.9rem;
        margin-bottom: 12px;
        font-weight: 500;
    }
    
    .product-card .description {
        font-size: 0.85rem;
        color: #E0E0E0; /* Improved contrast */
        margin-bottom: 16px;
        flex-grow: 1;
        line-height: 1.5;
    }

    .product-card .action-btn {
        display: block;
        text-align: center;
        background: linear-gradient(90deg, #FF61D2 0%, #5C24FF 100%);
        color: white !important;
        text-decoration: none;
        padding: 10px;
        border-radius: 8px;
        font-weight: 600;
        transition: opacity 0.2s;
        margin-top: auto; /* Push to bottom */
    }

    .product-card .action-btn:hover {
        opacity: 0.9;
        text-decoration: none;
    }

    /* Fallback image style handled by JS/HTML error, but basic styling here */
    .img-error {
        padding: 20px;
        color: #666;
        font-size: 0.8rem;
    }

    /* --- INNOVATIVE WEATHER CARD --- */
    .weather-card, section.weather-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(0, 0, 0, 0.2));
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 24px;
        padding: 0;
        margin: 20px 0;
        overflow: hidden;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        position: relative;
    }
    
    .weather-header {
        padding: 30px;
        background: linear-gradient(to right, rgba(92, 36, 255, 0.2), rgba(255, 97, 210, 0.1));
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .weather-main {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .weather-temp-big {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(to bottom, #fff, #ccc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    .weather-meta {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .weather-condition {
        font-size: 1.5rem;
        font-weight: 600;
        color: #FF61D2;
    }
    
    .weather-location {
        font-size: 1.1rem;
        opacity: 0.8;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .weather-stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1px;
        background: rgba(255,255,255,0.1); /* Separator color */
    }
    
    .weather-stat-item {
        background: rgba(20, 20, 20, 0.6); /* Restore bg */
        padding: 15px;
        text-align: center;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    
    .stat-label { font-size: 0.8rem; opacity: 0.7; text-transform: uppercase; letter-spacing: 1px; }
    .stat-value { font-size: 1.1rem; font-weight: 600; }
    
    .weather-forecast-scroll {
        display: flex;
        overflow-x: auto;
        padding: 20px;
        gap: 15px;
        background: rgba(0,0,0,0.2);
        scrollbar-width: thin;
        scrollbar-color: rgba(255,255,255,0.2) transparent;
    }
    
    .forecast-item {
        min-width: 100px;
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 15px 10px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        display: flex;
        flex-direction: column;
        gap: 8px;
        transition: transform 0.2s ease, background 0.2s ease;
    }
    
    .forecast-item:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-5px);
    }
    
    .forecast-date { font-weight: 600; color: #FF61D2; font-size: 0.9rem; }
    .forecast-icon { font-size: 2rem; margin: 5px 0; }
    .forecast-temp { font-weight: 700; }
    .forecast-desc { font-size: 0.75rem; opacity: 0.7; line-height: 1.2; }

    </style>
    """

